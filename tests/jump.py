import sys
import os
from playwright.sync_api import sync_playwright
up=os.path.join(os.environ.get('GUIDE_PHOTOS',''),'Screenshot_2026-11-02_at_')  # your own screenshots of the guide's photo pages (not in this repo)
txt=open(sys.argv[3]).read()
with sync_playwright() as p:
    b=p.chromium.launch(executable_path='/usr/bin/google-chrome',args=['--no-sandbox'])
    for sch in ['light','dark']:
        pg=b.new_context(viewport={'width':390,'height':844},device_scale_factor=2,color_scheme=sch,is_mobile=True,has_touch=True).new_page()
        errs=[]; pg.on('pageerror',lambda e:errs.append(str(e)))
        pg.goto('file://'+os.path.abspath(sys.argv[1])); pg.wait_for_timeout(1200)
        pg.locator('#guidebtn').click(); pg.locator('#bookbtn').click(); pg.locator('#bookpaste').fill(txt); pg.locator('#booksort').click(); pg.wait_for_timeout(500)
        pg.locator('#photobtn').click()
        for f in [x for x in ['1_21_18AM','1_21_35AM','1_21_50AM'] if os.path.exists(up+x+'.png')]:
            pg.set_input_files('#photofile', up+f+'.png'); pg.wait_for_timeout(2000); pg.locator('#photoadd').click(); pg.wait_for_timeout(600)
        pg.locator('#photocancel').click(); pg.locator('#guideclose').click(); pg.wait_for_timeout(300)
        for i in range(12): pg.locator('.navbtn.next').click(); pg.wait_for_timeout(120)
        pg.evaluate('window.scrollTo(0,0)'); pg.wait_for_timeout(400)
        pg.screenshot(path=f'J_{sch}_1.png')
        pg.locator('#mapcard .jumpdir').tap(); pg.wait_for_timeout(750)
        pg.screenshot(path=f'J_{sch}_2.png')
        r=pg.evaluate("(()=>{const r=document.querySelector('#mapcard .direction').getBoundingClientRect();return [Math.round(r.top),Math.round(r.bottom)]})()")
        print(sch,'direction box on screen at',r,'errors',errs)
    b.close()
