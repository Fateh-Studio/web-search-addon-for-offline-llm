@echo off
if not "%~1"=="minimized" (
    start "" /min cmd /c "%~f0 minimized"
    exit
)




REM ======================================================================================================================================================================
REM .....============================================================================================================================================================.....

REM Paste your llama.cpp folder address here (Example: cd /d "C:\llama.cpp")

REM ▼▼
cd /d "YOUR_ADDRESS_HERE"
REM ▲▲ 

REM .....============================================================================================================================================================.....
REM ======================================================================================================================================================================




REM **********************************************************************************************************************************************************************
REM .....************************************************************************************************************************************************************.....

REM Paste your mcp_server.py address here (Example: start "MCP Server" /min python "C:\my-project\mcp_server.py")

REM ▼▼
start "MCP Server" /min python "YOUR_ADDRESS_HERE"
REM ▲▲ 

REM .....************************************************************************************************************************************************************.....
REM **********************************************************************************************************************************************************************




timeout /t 5 /nobreak >nul

for /f "tokens=2 delims=: " %%i in ('llama-server.exe --version 2^>^&1 ^| findstr /R "version:"') do set "V=%%i"
if "%V%"=="" set "V=Unknown"




REM ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
REM .....~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~.....

REM Paste your GGUF model file address here (Example: set "MODEL_PATH=C:\llama.cpp\models\google\Gemma\gemma.gguf")

REM ▼▼
set "MODEL_PATH=YOUR_ADDRESS_HERE"
REM ▲▲ 

REM .....~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~.....
REM ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~




REM ======================================================================================================================================================================
REM .....============================================================================================================================================================.....

REM If you have mmproj file, paste its address here (Example: set "MMPROJ_PATH=C:\llama.cpp\models\google\Gemma\mmproj.gguf")
REM If not, leave it empty like this: set "MMPROJ_PATH="

REM ▼▼
set "MMPROJ_PATH=YOUR_ADDRESS_HERE"
REM ▲▲ 

REM .....============================================================================================================================================================.....
REM ======================================================================================================================================================================




set "LLAMA_CMD=llama-server.exe -m "%MODEL_PATH%""
if not "%MMPROJ_PATH%"=="" set "LLAMA_CMD=%LLAMA_CMD% --mmproj "%MMPROJ_PATH%""




REM ######################################################################################################################################################################
REM .....############################################################################################################################################################.....

REM SYSTEM SETTINGS -  EDIT THESE FOR YOUR HARDWARE:
REM -t NUMBER        : CPU threads (example: -t 4 for 4 cores, -t 8 for 8 cores)
REM --cpu-moe        : FOR CPU ONLY - remove this if you have GPU
REM --flash-attn on  : Memory optimization (keep it ON for most users)
REM --no-mmap        : Disables memory mapping (keep it if you have low RAM)
REM --temp 0.6       : Creativity (0 = deterministic, 1 = creative)
REM --top-p 0.95     : Nucleus sampling (0.9 to 1.0 is normal)
REM --top-k 40       : Top K sampling (30 to 50 is normal)
REM --repeat-penalty 1.2 : Avoid repeating words (1.0 to 1.5)
REM --reasoning off  : Set "off" for Gemma, "on" for QwQ or reasoning models
REM --timeout 300000 : Timeout in milliseconds (increase if slow)
REM 

REM ▼▼
set "LLAMA_CMD=%LLAMA_CMD% -t 4 -b 512 -c 6144 --cpu-moe --flash-attn on --no-mmap --temp 0.6 --top-p 0.95 --top-k 40 --repeat-penalty 1.2 --reasoning off --webui-mcp-proxy --timeout 300000 > llama_output.txt 2>&1"
REM ▲▲ 

REM .....############################################################################################################################################################.....
REM ######################################################################################################################################################################




start "Llama Server" /min cmd /k "%LLAMA_CMD%"

setlocal enabledelayedexpansion
set "P=0%"
set "S=0"

set "LOADING_ADDRESS=%CD%"

call :write

:loop
timeout /t 3 /nobreak >nul

findstr /C:"load_tensors: loading model tensors" "%LOADING_ADDRESS%\llama_output.txt" >nul 2>&1 && if !S! lss 1 (set S=1 && set P=25%% && call :write)
findstr /C:"llama_context: constructing" "%LOADING_ADDRESS%\llama_output.txt" >nul 2>&1 && if !S! lss 2 (set S=2 && set P=50%% && call :write)
findstr /C:"warming up" "%LOADING_ADDRESS%\llama_output.txt" >nul 2>&1 && if !S! lss 3 (set S=3 && set P=75%% && call :write)
findstr /C:"main: model loaded" "%LOADING_ADDRESS%\llama_output.txt" >nul 2>&1 && if !S! lss 4 (set S=4 && set P=95%% && call :write)
findstr /C:"all slots are idle" "%LOADING_ADDRESS%\llama_output.txt" >nul 2>&1 && goto ready
goto loop

:ready
(
echo ^<html^>^<head^>^<meta http-equiv="refresh" content="2;url=http://localhost:8080/"^>^<title^>Loading Model^</title^>^</head^>
echo ^<body style="background:black;color:white;font-size:40px;text-align:center;padding-top:20%%"^>
echo ^<p^>Version: %V%^</p^>
echo ^<p^>Model Ready! Redirecting...^</p^>
echo ^</body^>^</html^>
) > "%LOADING_ADDRESS%\loading.html"
exit

:write
(
echo ^<html^>^<head^>^<meta http-equiv="refresh" content="3"^>^<title^>Loading Model^</title^>^</head^>
echo ^<body style="background:black;color:white;font-size:40px;text-align:center;padding-top:20%%"^>
echo ^<p^>Version: %V%^</p^>
echo ^<p^>Loading... %P%^</p^>
echo ^</body^>^</html^>
) > "%LOADING_ADDRESS%\loading.html"
if "!S!"=="0" start "" "file:///%LOADING_ADDRESS%\loading.html"
exit /b
