import sys
from playwright.sync_api import sync_playwright
with sync_playwright() as p:
    b=p.chromium.launch(executable_path='/usr/bin/google-chrome',args=['--no-sandbox'])
    ctx=b.new_context(viewport={'width':390,'height':844},has_touch=True,is_mobile=True,device_scale_factor=2)
    pg=ctx.new_page(); errs=[]; pg.on('pageerror',lambda e:errs.append(str(e)))
    pg.goto('file://'+sys.argv[1]); pg.wait_for_timeout(900)
    for _ in range(30): pg.locator('#stepbar [data-act=next]').click()
    pg.wait_for_timeout(300); pg.screenshot(path=sys.argv[2]+'/ol_bar.png',clip={'x':0,'y':700,'width':390,'height':144})
    pg.locator('#stepbar .barinfo').click(); pg.wait_for_timeout(400)
    cur=pg.locator('#steplist li.current')
    bb=cur.bounding_box()
    print('steps tab visible:',pg.locator('#view-steps').is_visible(),'| current step:',cur.locator('.stepno').inner_text(),'| on screen y:',round(bb['y']),'of 844')
    pg.screenshot(path=sys.argv[2]+'/ol_steps.png')
    cur.click(); pg.wait_for_timeout(500); print('back on map:',pg.locator('#view-map').is_visible(),'|',pg.locator('#stepbar .barinfo b').inner_text())
    print('errors',errs); b.close()
