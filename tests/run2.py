import sys
from playwright.sync_api import sync_playwright
def tap_pin(pg,k,touch=True):
    pg.locator(f'#mapsvg .pin[data-k="{k}"]').scroll_into_view_if_needed()
    box=pg.locator(f'#mapsvg .pin[data-k="{k}"]').bounding_box(); x=box['x']+box['width']/2; y=box['y']+box['height']/2
    (pg.touchscreen.tap(x,y) if touch else pg.mouse.click(x,y)); pg.wait_for_timeout(700); return round(box['width'])
with sync_playwright() as p:
    b=p.chromium.launch(executable_path='/usr/bin/google-chrome',args=['--no-sandbox'])
    for name,vp,touch in [('phone',{'width':390,'height':844},True),('desktop',{'width':1280,'height':860},False)]:
        ctx=b.new_context(viewport=vp,has_touch=touch,is_mobile=touch)
        pg=ctx.new_page(); errs=[]; pg.on('pageerror',lambda e:errs.append(str(e)))
        pg.goto('file://'+sys.argv[1]); pg.wait_for_timeout(900)
        pg.locator('#zfit').click(); pg.wait_for_timeout(300)
        w=tap_pin(pg,'32',touch); print(name,'pin px',w,'| tap 32 ->',pg.locator('#mapcard h2').inner_text())
        pg.evaluate('window.scrollTo(0,0)'); pg.locator('#zfit').click(); pg.wait_for_timeout(300)
        tap_pin(pg,'18',touch); first=pg.locator('#mapcard h2').inner_text()
        tap_pin(pg,'18',touch); print(name,'tap 18 (crowded) ->',first,'then ->',pg.locator('#mapcard h2').inner_text())
        if name=='phone': pg.screenshot(path=sys.argv[2]+'/phone_pin.png')
        pg.locator('#tab-steps').click(); pg.wait_for_timeout(300)
        li=pg.locator('#steplist li[data-i]').nth(26); li.scroll_into_view_if_needed(); li.locator('div').nth(1).click(); pg.wait_for_timeout(700)
        print(name,'step 27 tap -> map shown',pg.locator('#view-map').is_visible(),'| card',pg.locator('#mapcard h2').inner_text(),'| bar',pg.locator('#stepbar .barinfo b').inner_text())
        if name=='phone': pg.screenshot(path=sys.argv[2]+'/phone_step.png')
        print(name,'errors',errs); ctx.close()
    b.close()
