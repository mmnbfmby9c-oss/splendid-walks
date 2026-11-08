import sys
import os
from playwright.sync_api import sync_playwright
txt=open(sys.argv[3]).read()
with sync_playwright() as p:
    b=p.chromium.launch(executable_path='/usr/bin/google-chrome',args=['--no-sandbox'])
    for sch in ['light','dark']:
        pg=b.new_context(viewport={'width':390,'height':844},device_scale_factor=2,color_scheme=sch,is_mobile=True,has_touch=True).new_page(); errs=[]; pg.on('pageerror',lambda e:errs.append(str(e)))
        pg.goto('file://'+os.path.abspath(sys.argv[1])); pg.wait_for_timeout(1000)
        print(sch,'banner at start:',pg.locator('#banner .kick').inner_text().replace('\n',' '),'|',pg.locator('#btitle').inner_text())
        pg.locator('#guidebtn').click(); pg.locator('#bookbtn').click(); pg.locator('#bookpaste').fill(txt); pg.locator('#booksort').click(); pg.wait_for_timeout(400); pg.locator('#guideclose').click()
        for i in range(22): pg.locator('.navbtn.next').click(); pg.wait_for_timeout(40)
        pg.evaluate('scrollTo(0,0)'); pg.wait_for_timeout(300)
        print(sch,'banner at step 23:',pg.locator('#bkick').inner_text(),'|',pg.locator('#btitle').inner_text(),'| partline on card:',pg.locator('.partline').count())
        pg.screenshot(path=f'B_{sch}.png')
        pg.locator('#banner').tap(); pg.wait_for_timeout(400); pg.screenshot(path=f'B_sheet_{sch}.png')
        pg.locator('#walklist .pt').nth(2).tap(); pg.wait_for_timeout(500)
        print(sch,'after choosing Part 3:',pg.locator('.barinfo').inner_text().replace('\n',' | '),'|',pg.locator('#btitle').inner_text(),'| sheet hidden',pg.locator('#walksheet').is_hidden())
        print(sch,'errors',errs)
    pg=b.new_context(viewport={'width':1280,'height':860}).new_page(); pg.goto('file://'+os.path.abspath(sys.argv[1])); pg.wait_for_timeout(900); pg.screenshot(path='B_desk.png')
    b.close()
