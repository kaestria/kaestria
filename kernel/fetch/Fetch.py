import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from kernel.system.Constant import VISTRO_OS_NAME, VISTRO_ROOT
import re
import time
START_TIME = time.time()
ANSI_ESCAPE = re.compile(r'\033\[[0-9;]*m')
def visibleLen(s: str) -> int:
    return len(ANSI_ESCAPE.sub('', s))
def padRight(s: str, width: int) -> str:
    pad = width - visibleLen(s)
    return s + ' ' * max(pad, 0)
def getUptime() -> str:
    elapsed = int(time.time() - START_TIME)
    if elapsed < 60:
        return f"{elapsed} seconds"
    elif elapsed < 3600:
        return f"{elapsed // 60} minutes"
    else:
        return f"{elapsed // 3600} hours"
def getMemoryUsage() -> str:
    try:
        import psutil
        mem = psutil.virtual_memory()
        percent = mem.percent
        return f"{mem.total // (1024 * 1024)}MiB (used {percent:.0f}%)"
    except ImportError:
        return "N/A"
def run(session) -> str:
    R = "\033[31m"
    X = "\033[0m"
    logo = [
        f"{R}               =++++++=              {X}",
        f"{R}          +++++++++=========         {X}",
        f"{R}       ++++++++===============.      {X}",
        f"{R}     :++++++++===@@@==========--     {X}",
        f"{R}    +++++++======@@@=====--------:   {X}",
        f"{R}   ++++++========@@@+==-----------:  {X}",
        f"{R}  +++++==========@@@*--------------  {X}",
        f"{R}  ++++===========@@@@--------------- {X}",
        f"{R}  ============--@@@@@--------------: {X}",
        f"{R}  ==========---*@@@@@@----------:::: {X}",
        f"{R}  =======-----*@@@--@@@*------:::::: {X}",
        f"{R}   ===------@@@@@----@@@@@-::::::::  {X}",
        f"{R}   ---@@@@@@@@%--------*@@@@@@@*::   {X}",
        f"{R}    :--###-------------:::::###::    {X}",
        f"{R}      --------------:::::::::::.     {X}",
        f"{R}        ----------:::::::::::.       {X}",
        f"{R}           :--::::::::::::           {X}",
        f"{R}                                    {X}",
    ]
    try:
        rel = session.getCurrentPath().relative_to(VISTRO_ROOT.parent.parent)
        displayPath = "~/" + str(rel).replace("\\", "/")
    except ValueError:
        displayPath = str(session.getCurrentPath())
    info = [
        f"{session.getUsername()}@vistro",
        f"--------------------------",
        f"OS {VISTRO_OS_NAME}",
        f"Uptime {getUptime()}",
        f"Path {displayPath}",
        f"Memory {getMemoryUsage()}",
    ]
    output = []
    maxLen = max(len(logo), len(info))
    for i in range(maxLen):
        left = logo[i] if i < len(logo) else ""
        right = info[i] if i < len(info) else ""
        output.append(padRight(left, 50) + " " + right)
    return "\n".join(output)
