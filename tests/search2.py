import sys
from playwright.sync_api import sync_playwright
with sync_playwright() as p:
    b=p.chromium.launch(executable_path='/usr/bin/google-chrome',args=['--no-sandbox'])
    pg=b.new_context(viewport={'width':390,'height':844},has_touch=True,is_mobile=True,device_scale_factor=2).new_page(); errs=[]; pg.on('pageerror',lambda e:errs.append(str(e)))
    pg.goto('file://'+sys.argv[1]); pg.wait_for_timeout(900)
    pg.locator('#cupbtn').tap(); pg.wait_for_timeout(300)
    print('after cup: box =',repr(pg.locator('#q').input_value()),'| x visible:',pg.locator('#clearq').is_visible(),'| results:',pg.locator('#results button').count())
    pg.screenshot(path=sys.argv[2]+'/s_typing.png',clip={'x':0,'y':0,'width':390,'height':320})
    pg.locator('#results button').nth(1).tap(); pg.wait_for_timeout(500)
    print('after pick: box =',repr(pg.locator('#q').input_value()),'| cup visible:',pg.locator('#cupbtn').is_visible(),'| dimmed pins:',pg.locator('#mapsvg .pin.dim').count(),'| card:',pg.locator('#mapcard h2').inner_text())
    pg.locator('#q').fill('byron'); pg.locator('#q').dispatch_event('input'); pg.wait_for_timeout(200)
    print('typed byron: results',pg.locator('#results button').count(),'| dimmed',pg.locator('#mapsvg .pin.dim').count())
    pg.locator('#clearq').tap(); pg.wait_for_timeout(200)
    print('after ×: box =',repr(pg.locator('#q').input_value()),'| results hidden:',pg.locator('#results').is_hidden(),'| dimmed:',pg.locator('#mapsvg .pin.dim').count(),'| cup visible:',pg.locator('#cupbtn').is_visible())
    print('errors',errs); b.close()
