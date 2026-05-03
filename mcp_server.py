import json, asyncio, urllib.parse, time, os, tempfile
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, StreamingResponse
import trafilatura
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
import aiohttp

app = FastAPI()
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])

MAX_LINKS_TO_COLLECT = 35
MAX_CONTENT_PER_SOURCE = 800
MAX_SOURCES = 10
MAX_CONCURRENT_PAGES = 10
PAGE_TIMEOUT = 10
RETRY_ATTEMPTS = 2

SEEN_URLS = set()

BLOCKED_DOMAINS = [
    'aparat.com', 'namasha.com', 'filimo.com', 'telewebion.com',
    'tamasha.com', 'video.varzesh3.com', 'didar.com', 'rubika.ir',
    'youtube.com', 'youtu.be', 'vimeo.com', 'dailymotion.com',
    'twitch.tv', 'tiktok.com',
    'instagram.com', 'facebook.com', 'twitter.com', 'x.com',
    'telegram.org', 't.me', 'whatsapp.com', 'eitaa.com',
    'bale.ai', 'gap.im', 'soroush.ir', 'igap.net',
    'pinterest.com', 'imgur.com', 'giphy.com', 'tenor.com',
    'flickr.com', 'deviantart.com', '9gag.com', 'unsplash.com', 'pexels.com',
    'bilibili.com', 'd.tube', 'odysee.com', 'rumble.com',
    'metacafe.com', 'veoh.com', 'crackle.com', 'pluto.tv',
    'peacocktv.com', 'tubitv.com', 'dlive.tv', 'kick.com', 'trovo.live',
    'digikala.com', 'torob.com', 'bamilo.com', 'alibaba.ir',
    'snapp.market', 'basalam.com', 'esam.ir', 'divar.ir', 'sheypoor.com',
    'downloadha.com', 'soft98.ir', 'yasdl.com', 'patoghu.com',
    'p30download.com', 'sarzamindownload.com', 'download.ir',
    'blogfa.com', 'blogsky.com', 'mihanblog.com', 'beytoote.com',
    'namnak.com', 'akairan.com', 'seemorgh.com', 'rooziato.com',
    'zoomg.ir', '1pezeshk.com',
]

def is_blocked(url): 
    try: return any(b in urllib.parse.urlparse(url).netloc.lower() for b in BLOCKED_DOMAINS)
    except: return False

def unwrap_zarebin_link(href):
    if not href or 'javascript:' in href or 'zarebin.ir' not in href: return href
    parsed = urllib.parse.urlparse(href)
    for p in ['url','q','link','u','goto','redirect','destination']:
        if p in urllib.parse.parse_qs(parsed.query):
            decoded = urllib.parse.unquote(urllib.parse.parse_qs(parsed.query)[p][0])
            if decoded.startswith('http'): return decoded
    return href

def extract_relevant_text(html, query):
    keywords = [w.strip() for w in query.split() if len(w.strip()) > 1]
    if not keywords:
        keywords = [query.strip()]

    try:
        full_text = trafilatura.extract(
            html,
            include_links=False, include_images=False, include_tables=True,
            include_comments=False, deduplicate=True,
            favor_precision=True, output_format='txt'
        )
        if not full_text:
            return None

        paragraphs = [p.strip() for p in full_text.split('\n') if len(p.strip()) > 50]
        if not paragraphs:
            return None

        scored = []
        for p in paragraphs:
            score = sum(1 for kw in keywords if kw in p)
            scored.append((score, p))
        scored.sort(key=lambda x: x[0], reverse=True)

        result_parts = []
        total_len = 0
        for score, para in scored:
            if total_len >= MAX_CONTENT_PER_SOURCE:
                break
            if score > 0 or total_len < 200:
                result_parts.append(para)
                total_len += len(para) + 2

        result = '\n\n'.join(result_parts)
        if len(result) < 80:
            return full_text[:MAX_CONTENT_PER_SOURCE].strip()
        return result[:MAX_CONTENT_PER_SOURCE].strip()
    except:
        return None

async def fetch_page_content(url, sem, query):
    async with sem:
        domain = urllib.parse.urlparse(url).netloc.lower()
        timeout_val = 12 if domain.endswith('.ir') else PAGE_TIMEOUT
        headers = {'User-Agent': 'Mozilla/5.0'}
        async with aiohttp.ClientSession() as session:
            for _ in range(RETRY_ATTEMPTS):
                try:
                    async with session.get(url, timeout=timeout_val, headers=headers) as resp:
                        if resp.status == 200:
                            html = await resp.text()
                            text = extract_relevant_text(html, query)
                            if text and len(text) > 80:
                                return text[:MAX_CONTENT_PER_SOURCE]
                except: pass
                await asyncio.sleep(2)
        return None

def selenium_collect_links(query: str) -> list:
    options = webdriver.ChromeOptions()
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--headless")
    temp_dir = tempfile.mkdtemp(prefix="selenium_temp_")
    options.add_argument(f"--user-data-dir={temp_dir}")

    # =========================================================================================================================================================================================================
    # ▼ Paste your chromedriver.exe address here (Example: r"C:\chromedriver\chromedriver.exe") ▼
    # =========================================================================================================================================================================================================
    CHROMEDRIVER_ADDRESS = r"YOUR_ADDRESS_HERE"
    
    service = Service(executable_path=CHROMEDRIVER_ADDRESS)
    driver = webdriver.Chrome(service=service, options=options)
    all_links = []

    try:
        driver.get(f"https://zarebin.ir/search?q={urllib.parse.quote(query)}")
        time.sleep(3)

        while len(all_links) < MAX_LINKS_TO_COLLECT:
            links = driver.find_elements(By.CSS_SELECTOR, "#result a[href^='http']")
            for a in links:
                href = a.get_attribute('href')
                actual = unwrap_zarebin_link(href)
                if actual and 'zarebin.ir' not in actual and not is_blocked(actual) and actual not in all_links:
                    all_links.append(actual)
                    if len(all_links) >= MAX_LINKS_TO_COLLECT:
                        break
            if len(all_links) >= MAX_LINKS_TO_COLLECT:
                break

            try:
                btn = WebDriverWait(driver, 5).until(
                    EC.element_to_be_clickable((By.XPATH, "//button[.//span[contains(text(),'نتایج بیشتر')]]"))
                )
                btn.click()
                time.sleep(4)
            except:
                break

    except Exception as e:
        print(f"Selenium error: {str(e)[:200]}")
    finally:
        driver.quit()
        import shutil
        try: shutil.rmtree(temp_dir)
        except: pass

    return all_links[:MAX_LINKS_TO_COLLECT]

async def search_round(query: str) -> str:
    global SEEN_URLS
    local_failed = set()
    contents = []
    print(f"=== جستجو: {query} ===")

    loop = asyncio.get_event_loop()
    all_links = await loop.run_in_executor(None, selenium_collect_links, query)
    print(f"لینک‌های جمع‌آوری‌شده: {len(all_links)}")

    candidates = [url for url in all_links if url not in SEEN_URLS and not is_blocked(url)]
    print(f"نامزدها: {len(candidates)}")

    sem = asyncio.Semaphore(MAX_CONCURRENT_PAGES)
    tasks = {}
    idx = 0
    success = 0
    while success < MAX_SOURCES and idx < len(candidates):
        while len(tasks) < MAX_CONCURRENT_PAGES and idx < len(candidates):
            url = candidates[idx]
            if url not in tasks.values():
                t = asyncio.create_task(fetch_page_content(url, sem, query))
                tasks[t] = url
            idx += 1
        if not tasks: break
        done, _ = await asyncio.wait(tasks.keys(), return_when=asyncio.FIRST_COMPLETED)
        for finished in done:
            url = tasks.pop(finished)
            result = finished.result()
            if result:
                domain = urllib.parse.urlparse(url).netloc.replace('www.', '')
                contents.append(f"**{domain}**\n{result}\n")
                SEEN_URLS.add(url)
                success += 1
                print(f"  ✅ {len(result)} کاراکتر")
                if success >= MAX_SOURCES: break
            else:
                local_failed.add(url)
                print(f"  ❌ شکست: {url[:60]}")
        if success >= MAX_SOURCES:
            for t in tasks: t.cancel()
            break
    for t in tasks: t.cancel()

    if not contents:
        return "متاسفانه هیچ نتیجه‌ای یافت نشد."
    return f"**نتایج جستجو برای: {query}**\n\n" + "\n\n".join(contents)


async def sse_events():
    yield "event: endpoint\ndata: /message\n\n"
    while True:
        await asyncio.sleep(30); yield ": keepalive\n\n"

@app.api_route("/sse", methods=["GET","POST"])
async def handle_sse(request: Request):
    if request.method == "GET":
        return StreamingResponse(sse_events(), media_type="text/event-stream")
    body = await request.json()
    method = body.get("method")
    req_id = body.get("id")
    if method == "initialize":
        SEEN_URLS.clear()
        return JSONResponse({"jsonrpc":"2.0","id":req_id,"result":{"protocolVersion":"2025-11-25","capabilities":{"tools":{}},"serverInfo":{"name":"short-domain-v74","version":"74.0.0"}}})
    elif method == "tools/list":
        return JSONResponse({"jsonrpc":"2.0","id":req_id,"result":{"tools":[{"name":"research","description":"Search the Persian web. Returns 10 sources (800 chars each). Call with a short Persian query.","inputSchema":{"type":"object","properties":{"query":{"type":"string","description":"Persian search query"}},"required":["query"]}}]}})
    elif method == "tools/call":
        q = body.get("params",{}).get("arguments",{}).get("query")
        if not q: return JSONResponse({"jsonrpc":"2.0","id":req_id,"error":{"code":-32602,"message":"Missing query"}})
        text = await search_round(q)
        return JSONResponse({"jsonrpc":"2.0","id":req_id,"result":{"content":[{"type":"text","text":text}]}})
    return JSONResponse({"jsonrpc":"2.0","id":req_id,"error":{"code":-32601,"message":"Method not found"}})

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8765, log_level="info")
