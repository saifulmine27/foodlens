"""Tomar index.html ke Android-er jonno patch kore www/index.html banay.
Run:  python3 prepare.py            (index.html ei folder-e thakle)
      python3 prepare.py path/to/index.html
"""
import re, sys, os, pathlib

src = pathlib.Path(sys.argv[1] if len(sys.argv) > 1 else "index.html")
html = src.read_text(encoding="utf-8")

def patch(name, pattern, repl, flags=0):
    global html
    new, n = re.subn(pattern, lambda m: repl, html, count=1, flags=flags)
    print(("OK      " if n else "SKIPPED ") + name)
    html = new

# 1. Purono hardcoded key shoriye, build-er shomoy GitHub Secret theke key boshano
#    (key repo-te lekha thake na; secret na dile key faka thake, app-e button diye dewa jabe)
key = os.environ.get("FOODLENS_API_KEY", "").strip().replace('"', "")
patch("old-style hardcoded key",
      r'const HARDCODED_API_KEY = "[^"]*";',
      'const HARDCODED_API_KEY = "%s";' % key)
patch("set API key from secret" if key else "clear embedded API key",
      r"let GEMINI_API_KEY = localStorage\.getItem\('user_gemini_api_key'\) \|\| '[^']*';",
      "let GEMINI_API_KEY = localStorage.getItem('user_gemini_api_key') || '%s';" % key)

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

# 6. Mobile UI: niche bottom navigation + settings sheet (sidebar mobile-e lukano)
html = html.replace('<i class="fa-solid fa-bars text-xl"></i>', '<i class="fa-solid fa-gear text-xl"></i>')
old_grid = "grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4"
print(("OK      " if old_grid in html else "SKIPPED ") + "compact 2x2 macro cards")
html = html.replace(old_grid, "grid grid-cols-2 lg:grid-cols-4 gap-2.5 md:gap-4", 1)

MOBILE_UI = r"""
<style>
.bn{display:flex;position:fixed;left:0;right:0;bottom:0;z-index:35;background:#fff;border-top:.5px solid #e2e8f0;padding:6px 0 calc(8px + env(safe-area-inset-bottom,0px));justify-content:space-around}
.dark .bn{background:#1e293b;border-color:#334155}
.bn button{flex:1;display:flex;flex-direction:column;align-items:center;gap:2px;font-size:10px;color:#94a3b8;background:none;border:0;padding:4px 0}
.bn button i{font-size:18px}
.bn button.on{color:#5b21b6;font-weight:600}
.dark .bn button.on{color:#a78bfa}
.ms{position:fixed;inset:0;z-index:60;background:rgba(15,23,42,.45);display:none;align-items:flex-end}
.ms.open{display:flex}
.ms-in{width:100%;background:#fff;border-radius:18px 18px 0 0;padding:10px 14px calc(14px + env(safe-area-inset-bottom,0px));color:#0f172a}
.dark .ms-in{background:#1e293b;color:#f1f5f9}
.ms-in button{display:flex;align-items:center;gap:12px;width:100%;padding:13px 6px;font-size:14px;background:none;border:0;border-bottom:.5px solid rgba(148,163,184,.25);text-align:left;color:inherit}
.ms-in button i{width:20px;color:#5b21b6;text-align:center}
.dark .ms-in button i{color:#a78bfa}
@media(min-width:768px){.bn,.ms{display:none!important}}
@media(max-width:767px){
#sidebar{display:none!important}
main{padding-bottom:5.5rem!important}
#tab-dashboard>.grid:first-child>div{padding:12px!important}
#tab-dashboard>.grid:first-child .w-10{display:none!important}
#tab-dashboard>.grid:first-child .text-2xl{font-size:1.05rem!important}
}
</style>
<nav id="bottomNav" class="bn">
<button data-bn="dashboard" class="on"><i class="fa-solid fa-chart-pie"></i><span>Home</span></button>
<button data-bn="charts"><i class="fa-solid fa-chart-column"></i><span>Charts</span></button>
<button data-bn="tracker"><i class="fa-solid fa-magnifying-glass"></i><span>Search</span></button>
<button data-bn="photo"><i class="fa-solid fa-wand-magic-sparkles"></i><span>AI Scan</span></button>
<button data-bn="dietitian"><i class="fa-solid fa-user-doctor"></i><span>Dietitian</span></button>
</nav>
<div id="mSheet" class="ms">
<div class="ms-in">
<button data-ms="meals"><i class="fa-solid fa-clock-rotate-left"></i><span></span></button>
<button data-ms="theme"><i class="fa-solid fa-moon"></i><span></span></button>
<button data-ms="lang"><i class="fa-solid fa-language"></i><span></span></button>
<button data-ms="key"><i class="fa-solid fa-key"></i><span></span></button>
</div>
</div>
<script>
(function(){
var L={
en:{dashboard:'Home',charts:'Charts',tracker:'Search',photo:'AI Scan',dietitian:'Dietitian',meals:'Meal Log',theme:'Dark / Light mode',lang:'বাংলা',key:'Gemini API Key'},
bn:{dashboard:'হোম',charts:'চার্ট',tracker:'সার্চ',photo:'AI স্ক্যান',dietitian:'ডায়েটিশিয়ান',meals:'মিল লগ',theme:'ডার্ক / লাইট মোড',lang:'English',key:'Gemini API Key'}};
if (typeof window.promptSetApiKey !== 'function') {
window.promptSetApiKey = function(){
var cur = localStorage.getItem('user_gemini_api_key') || '';
var k = prompt('Gemini API Key:', cur);
if (k !== null) { localStorage.setItem('user_gemini_api_key', k.trim()); alert('API Key saved'); }
};
}
if (typeof window.toggleLanguage !== 'function') {
window.toggleLanguage = function(){
currentLang = currentLang === 'en' ? 'bn' : 'en';
var a = document.getElementById('langToggle'), b = document.getElementById('langToggleMobile');
if (a) a.innerText = currentLang === 'en' ? 'বাংলা' : 'English';
if (b) b.innerText = currentLang === 'en' ? 'BN / EN' : 'EN / BN';
document.querySelectorAll('[data-i18n]').forEach(function(el){
var k = el.getAttribute('data-i18n');
if (i18n[currentLang] && i18n[currentLang][k]) el.innerText = i18n[currentLang][k];
});
var q = document.getElementById('foodSearchInput');
renderFoodGrid(q ? q.value : '');
updateDashboardUI();
labels();
};
['langToggle','langToggleMobile'].forEach(function(id){
var el = document.getElementById(id);
if (el) el.addEventListener('click', window.toggleLanguage);
});
}
function tr(){return (typeof currentLang!=='undefined'&&currentLang==='bn')?L.bn:L.en;}
function labels(){
var s=tr();
document.querySelectorAll('#bottomNav [data-bn]').forEach(function(b){b.querySelector('span').textContent=s[b.getAttribute('data-bn')];});
document.querySelectorAll('#mSheet [data-ms]').forEach(function(b){b.querySelector('span').textContent=s[b.getAttribute('data-ms')];});
}
function setActive(id){
document.querySelectorAll('#bottomNav [data-bn]').forEach(function(b){b.classList.toggle('on',b.getAttribute('data-bn')===id);});
}
function openSheet(){labels();document.getElementById('mSheet').classList.add('open');}
function closeSheet(){document.getElementById('mSheet').classList.remove('open');}
var origSwitch=window.switchTab;
window.switchTab=function(id){origSwitch(id);setActive(id);closeSheet();window.scrollTo(0,0);};
var origLang=window.toggleLanguage;
window.toggleLanguage=function(){origLang();labels();};
document.querySelectorAll('#bottomNav [data-bn]').forEach(function(b){
b.addEventListener('click',function(){window.switchTab(b.getAttribute('data-bn'));});
});
document.getElementById('menuToggle').addEventListener('click',openSheet);
document.getElementById('mSheet').addEventListener('click',function(e){if(e.target===this)closeSheet();});
document.querySelectorAll('#mSheet [data-ms]').forEach(function(b){
b.addEventListener('click',function(){
var k=b.getAttribute('data-ms');
if(k==='meals'){window.switchTab('meals');return;}
closeSheet();
if(k==='theme')document.getElementById('themeToggle').click();
if(k==='lang')document.getElementById('langToggle').click();
if(k==='key')promptSetApiKey();
});
});
labels();
})();
</script>
"""
html = html.replace("</body>", MOBILE_UI + "\n</body>", 1)
print("OK      mobile bottom navigation injected")


# Vit D chart-e bhul chhilo: 600 IU-r jaygay 90 diye bhag hochchhilo
fix = "(totalVitD / 90)"
print(("OK      " if fix in html else "SKIPPED ") + "fix Vit D % calculation")
html = html.replace(fix, "(totalVitD / 600)")

leaks = [k for k in re.findall(r"AQ\.[A-Za-z0-9_\-]{20,}", html) if k != key]
if leaks:
    sys.exit("ERROR: kono API key ekhono code-e lekha ache, build bondho kora holo: " + leaks[0][:8] + "...")
print("OK      no leaked key in code")

out = pathlib.Path("www/index.html")
out.parent.mkdir(exist_ok=True)
out.write_text(html, encoding="utf-8")
print("\nDone ->", out)
