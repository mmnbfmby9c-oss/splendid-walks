import sys
import os
from playwright.sync_api import sync_playwright
txt=open(sys.argv[3]).read()
with sync_playwright() as p:
    b=p.chromium.launch(executable_path='/usr/bin/google-chrome',args=['--no-sandbox'])
    for sch in ['light','dark']:
        pg=b.new_context(viewport={'width':390,'height':844},device_scale_factor=2,color_scheme=sch,is_mobile=True,has_touch=True).new_page(); errs=[]; pg.on('pageerror',lambda e:errs.append(str(e)))
        pg.goto('file://'+os.path.abspath(sys.argv[1])); pg.wait_for_timeout(1000)
        pg.locator('#guidebtn').click(); pg.locator('#bookbtn').click(); pg.locator('#bookpaste').fill(txt); pg.locator('#booksort').click(); pg.wait_for_timeout(500); pg.locator('#guideclose').click()
        if sch=='light':
            urls=pg.evaluate("[0,11,18,21,22,30,35,48].map(i=>{const r=routeInfo(i); return [walk.steps[i].to, r.a, r.b, r.n, decodeURIComponent(r.url).length]})")
            for u in urls: print('route from step',u)
            print(pg.evaluate("decodeURIComponent(routeInfo(0).url)"))
            print('parts', pg.evaluate("walk.parts.map((x,i)=>{const p=partOf(x.from);return [p.n,p.from,p.to,partMinutes(p)]})"))
            print('end of part 1 says:', pg.evaluate("buildChunks('redlion').chunks.slice(-1)[0].slice(0,90)"))
            print('start of part 2 says:', pg.evaluate("buildChunks('22').chunks[0]"))
        for i in range(22): pg.locator('.navbtn.next').click(); pg.wait_for_timeout(60)
        pg.evaluate('window.scrollTo(0,0)'); pg.wait_for_timeout(300); pg.screenshot(path=f'P_card_{sch}.png')
        pg.locator('#mapcard .jumpdir').tap(); pg.wait_for_timeout(800); pg.screenshot(path=f'P_dir_{sch}.png')
        pg.locator('#tab-steps').click(); pg.wait_for_timeout(500); pg.evaluate("window.scrollBy(0,-200)"); pg.wait_for_timeout(200); pg.screenshot(path=f'P_steps_{sch}.png')
        print(sch,'errors',errs)
    b.close()
