<div dir="rtl" align="center">
  
# [🇮🇷 فارسی](#فارسی) &nbsp;&nbsp;|&nbsp;&nbsp; [🇬🇧 English](#english)

</div>

---

<span id="فارسی"></span>
<div dir="rtl">

# پروژه RAG آفلاین با جستجوی وب

## این پروژه چیکار میکنه؟

این پروژه llama.cpp رو به اینترنت وصل میکنه. هر مدلی که داری، میتونه توی وب بگرده و از اطلاعات به‌روز استفاده کنه.

فایده اصلیش وقتیه که اینترنت بین‌الملل قطع میشه. اون موقع گوگل کروم و بیشتر موتورهای جستجو کار نمیکنن، ولی این پروژه با موتور جستجوی ایرانی به اسم **ذره‌بین** کار میکنه. ذره‌بین توی قطعی اینترنت بین الملل در ایران، سایت‌های باز و مرتبط بیشتری نسبت به رقبای داخلی مثل برتینا، گردو و... پیدا میکنه.

کاربر سوالش رو میپرسه، پروژه توی وب میگرده، متن صفحه‌ها رو درمیاره و با دانش خود مدل (همون مدلی که توی llama.cpp داری) قاطی میکنه تا یه جواب دقیق و درست بده. حتی میتونی در یک پرامپت ازش بخوای در مورد فلان موضوع در وب بگرده و در مورد فلان موضوع از دانش خودش جواب بده...دقیقا همینکار رو میکنه.

هر زمان در پرامپت و سوالت خواستی مدل از وب استفاده کنه، بهش مستقیم بگو که در وب بگرده وگرنه از دانش آفلاین خودش استفاده میکنه.

### یه نکته خیلی مهم

بعد از هر سوال، صبر کن تا جواب کامل بیاد. اگه زودتر و قبل از تموم شدن جواب، کنسل کنی و سوال بعدی رو بپرسی، به خاطر نحوه عملکرد llama با mcp ، از دانش خودش جواب میده و ابزار وب فراخوانی نمیشه.

---

## نیازمندی‌ها

### 1. پایتون (Python)
برو سایت python.org آخرین نسخه رو دانلود و نصب کن. موقع نصب حتماً گزینه Add Python to PATH رو فعال کن.

### 2. کتابخانه‌های پایتون
فایل requirements.txt رو کنار بقیه فایل‌ها بذار. بعد خط فرمان (Command Prompt) رو باز کن، برو به همون پوشه (با دستور cd) و بعد این دستور رو بزن:

pip install -r requirements.txt

این دستور همه کتابخونه‌هایی که لازم داری رو یکجا نصب میکنه. اگه نتونستی، یکی یکی کتابخونه‌ها رو خودت نصب کن.

### 3. کروم‌درایور (Chromedriver)
مرورگر Chrome رو باز کن. برو منوی سه نقطه → Help → About Chrome تا ببینی نسخه کروم چنده. بعد برو از آدرس زیر کروم‌درایور مناسب با همون نسخه رو دانلود کن:

https://developer.chrome.com/docs/chromedriver/downloads

(اگه این لینک باز نشد، از این یکی دانلود کن: https://github.com/dreamshao/chromedriver/releases/tag/main)

فایل chromedriver.exe رو بذار توی یه پوشه مثلاً C:\chromedriver\

---

## راه‌اندازی

### مرحله 1: ویرایش فایل llama.bat
فایل llama.bat رو با Notepad باز کن. توی این فایل چهار تا جای مختلف نوشته YOUR_ADDRESS_HERE. هر کدوم رو باید با آدرس واقعی خودت عوض کنی:

- اولی آدرس پوشه llama.cpp
- دومی آدرس کامل فایل mcp_server.py
- سومی آدرس کامل فایل مدل GGUF
- چهارمی آدرس کامل فایل mmproj (اگه مدلت همچین فایلی نداره، این خط رو خالی بذار: set "MMPROJ_PATH=")

### مرحله 2: ویرایش فایل mcp_server.py
فایل mcp_server.py رو با Notepad باز کن. یک جا نوشته YOUR_ADDRESS_HERE رو پیدا کن و آدرس کامل فایل chromedriver.exe رو بهش بده.

### مرحله 3: اجرا
روی فایل llama.bat دوبار کلیک کن. سه تا فایل باز میشن که سریع مینیمایز میشن. اونا رو نبند، چون فرایندهای اجرای مدل و سرور هستند. بعدش یه صفحه سیاه توی مرورگرت باز میشه که ورژن llama.cpp و درصد بارگذاری مدلت رو نشون میده. وقتی مدل کاملاً آماده شد، خودکار میری به صفحه http://localhost:8080

---

## چطور استفاده کنم؟

توی صفحه http://localhost:8080 (بهش میگن WebUI) برو به بخش Settings و Message Prompt رو به این شکلی تنظیم کن:

Research assistant. Create ONE short Persian query (max 4 words) using the most common everyday phrase. Call research ONCE. Combine results with your knowledge.

پایینش تیک Show system message in conversations رو بزن که اول پرامپتی که مینویسی این Message Prompt بالایی نمایش داده بشه. این کار برای اینه که مدلت بفهمه که ابزار جستجو رو در اختیارش گذاشتی.

---

## تنظیمات سخت‌افزاری (برای کامپیوتر خودت)

توی فایل llama.bat یه خط خیلی بلند هست که با set "LLAMA_CMD= شروع میشه. اونجا یه سری عدد و پارامتر هست که میتونی برای کامپیوتر خودت عوض کنی:

- t 4 : یعنی چند تا نخ (thread) از CPU استفاده بشه. اگه CPU قوی داری، این عدد رو زیاد کن مثلاً بذار t 8
- cpu-moe : این فقط مال CPU هست. اگه کارت گرافیک (GPU) داری، این بخش رو پاک کن
- reasoning off : این واسه مدل‌های مخصوص استدلال مثل QwQ هست. اگه از اون مدلا داری، بذارش on
- timeout 300000 : یعنی مدل چند میلی‌ثانیه صبر کنه تا جواب بده. اگه مدل دیر جواب میده، این عدد رو زیاد کن مثلاً بذار 600000. البته همین عدد خوبه دستش نزن

---

## موفق باشی!

ساخته شده توسط FATEH-STUDIO

</div>

---

<span id="english"></span>
<div dir="ltr">

# Offline RAG with Web Search

## What does this project do?

It connects llama.cpp to the internet. Any model you have can search the web and use up-to-date information.

The main benefit is when international internet is cut off. Google Chrome and most search engines won't work, but this project uses an Iranian search engine called **Zarebin**. Zarebin works great during internet outages in Iran and finds more accessible, relevant Persian sites than other local search engines like Bertina, Gerdoo, and others.

You ask a question, the project searches the web, extracts text from pages, and combines it with your model's knowledge (the same model you run in llama.cpp) to give an accurate answer. You can even ask it in one prompt to "search the web about X" and "answer Y from your own knowledge" — it does exactly that.

Whenever you want the model to use the web in your prompt or question, directly tell it to "search the web". Otherwise, it will use its offline knowledge.

### One very important note

After each question, wait for the complete answer. If you cancel early and ask another question before the answer finishes, due to how llama works with MCP, the web tool won't be called and the model will answer from its own knowledge.

---

## Requirements

### 1. Python
Go to python.org, download and install the latest version. During installation, make sure to check "Add Python to PATH".

### 2. Python packages
Put requirements.txt next to your other files. Open Command Prompt, go to that folder (using cd command), then run:

pip install -r requirements.txt

This installs all needed packages at once. (If it doesn't work, install them one by one yourself.)

### 3. Chromedriver
Open Chrome browser. Go to the three-dot menu → Help → About Chrome to see your Chrome version. Then download the matching Chromedriver from:

https://developer.chrome.com/docs/chromedriver/downloads

(If this link doesn't open, try: https://github.com/dreamshao/chromedriver/releases/tag/main)

Put chromedriver.exe in a folder like C:\chromedriver\

---

## Setup

### Step 1: Edit llama.bat
Open llama.bat with Notepad. There are four places where YOUR_ADDRESS_HERE is written. Replace each with your real address:

- First: Your llama.cpp folder address
- Second: Full address of mcp_server.py
- Third: Full address of your GGUF model file
- Fourth: Full address of mmproj file (if your model doesn't have one, leave it empty: set "MMPROJ_PATH=")

### Step 2: Edit mcp_server.py
Open mcp_server.py with Notepad. Find where YOUR_ADDRESS_HERE is written and put your full chromedriver.exe address there.

### Step 3: Run
Double-click llama.bat. Three windows will open and minimize quickly. Don't close them — they're the model and server processes. Then a black page opens in your browser showing the llama.cpp version and your model's loading percentage. When the model is fully ready, you'll automatically go to http://localhost:8080

---

## How to use

At http://localhost:8080 (called WebUI), go to Settings and set Message Prompt to:

Research assistant. Create ONE short Persian query (max 4 words) using the most common everyday phrase. Call research ONCE. Combine results with your knowledge.

Below it, check "Show system message in conversations" so this Message Prompt appears at the beginning of your prompt. This helps the model understand that you've given it a search tool.

---

## Hardware settings (for your computer)

In llama.bat, there's a very long line starting with set "LLAMA_CMD=. Inside, you can adjust these parameters for your system:

- t 4 : Number of CPU threads. If you have a strong CPU, increase it (e.g., t 8)
- cpu-moe : CPU only. If you have a GPU, remove this part
- reasoning off : Reasoning mode. If you use QwQ models, change it to on
- timeout 300000 : Timeout in milliseconds. If the model responds slowly, increase it (e.g., 600000) — but the current value is fine, leave it alone

---

## Good luck!

Created by FATEH-STUDIO

</div>
