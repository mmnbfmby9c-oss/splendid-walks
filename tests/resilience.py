import os, sys, re
from playwright.sync_api import sync_playwright
# 1) map tiles that can't load (no signal) leave the sketch streets visible, not a blank map
# 2) a Safari tab on an iPhone warns that the text lives in the home-screen app
# 3) a stop with no guide text offers "Load your backup"
app=os.path.abspath(sys.argv[1]); out=sys.argv[2]
with sync_playwright() as p:
    b=p.chromium.launch(executable_path='/usr/bin/google-chrome',args=['--no-sandbox']); errs=[]
    ctx=b.new_context(**p.devices['iPhone 13']); ctx.route(re.compile(r'tile\.openstreetmap\.org'),lambda r:r.abort())
    pg=ctx.new_page(); pg.on('pageerror',lambda e:errs.append(str(e))); pg.goto('file://'+app); pg.wait_for_timeout(1500)
    streets=pg.evaluate("document.querySelectorAll('#sketchsvg polyline').length")
    shown=pg.evaluate("getComputedStyle(document.querySelector('#sketchsvg')).display!=='none'")
    print('no signal: sketch streets drawn',streets,'| visible',shown)
    if not(streets>10 and shown): errs.append('no fallback map')
    print('Safari tab warning shown:', pg.locator('#tabwarn').is_visible())
    if not pg.locator('#tabwarn').is_visible(): errs.append('no Safari warning')
    pg.locator('#tabwarnx').tap(); print('dismissed:', pg.locator('#tabwarn').is_hidden())
    print('card offers backup:', pg.locator('#mapcard [data-act=loadbackup]').count()>0)
    if not pg.locator('#mapcard [data-act=loadbackup]').count(): errs.append('no backup offer on card')
    pg.screenshot(path=os.path.join(out,'resilience.png'))
    ctx2=b.new_context(**p.devices['iPhone 13']); pg2=ctx2.new_page(); pg2.add_init_script("Object.defineProperty(navigator,'standalone',{get:()=>true})")
    pg2.goto('file://'+app); pg2.wait_for_timeout(1000); print('home-screen app: no warning:', pg2.locator('#tabwarn').is_hidden())
    if not pg2.locator('#tabwarn').is_hidden(): errs.append('warning shown in app')
    print('errors',errs); b.close()
