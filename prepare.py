"""Tomar index.html ke Android-er jonno patch kore www/index.html banay.
Run:  python3 prepare.py            (index.html ei folder-e thakle)
      python3 prepare.py path/to/index.html
"""
import re, sys, pathlib

src = pathlib.Path(sys.argv[1] if len(sys.argv) > 1 else "index.html")
html = src.read_text(encoding="utf-8")

def patch(name, pattern, repl, flags=0):
    global html
    new, n = re.subn(pattern, lambda m: repl, html, count=1, flags=flags)
    print(("OK      " if n else "SKIPPED ") + name)
    html = new

# 1. Hardcoded API key remove (key APK-r bhitore thakle je keu ber kore nite pare)
patch("remove hardcoded API key",
      r'const HARDCODED_API_KEY = "[^"]*";',
      'const HARDCODED_API_KEY = "";')

# 2. Purono model (1.5-flash) bondho hoye gese -> notun model
html = html.replace("gemini-1.5-flash", "gemini-2.5-flash")
print("OK      model -> gemini-2.5-flash")

# 3. Key na thakle AI scan-er age key chai
patch("ask for key before scan",
      r"async function analyzeWithGemini\(\) \{",
      "async function analyzeWithGemini() {\n"
      "            if (!getActiveApiKey()) { promptSetApiKey(); if (!getActiveApiKey()) return; }")

# 4. Sidebar-e 'API Key' button
patch("add API Key button",
      r'<div class="pt-2 flex items-center space-x-3">',
      '<button onclick="promptSetApiKey()" class="w-full flex items-center space-x-2 text-xs font-medium '
      'text-slate-600 dark:text-slate-400 hover:text-slate-900 dark:hover:text-white">'
      '<i class="fa-solid fa-key"></i><span>Gemini API Key</span></button>\n'
      '            <div class="pt-2 flex items-center space-x-3">')

# 5. Typo
html = html.replace("আলো ভর্তা", "আলু ভর্তা")

out = pathlib.Path("www/index.html")
out.parent.mkdir(exist_ok=True)
out.write_text(html, encoding="utf-8")
print("\nDone ->", out)
