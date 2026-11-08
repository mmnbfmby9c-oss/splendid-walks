import sys
from playwright.sync_api import sync_playwright
with sync_playwright() as p:
    b=p.chromium.launch(executable_path='/usr/bin/google-chrome',args=['--no-sandbox'])
    for sch in ['light','dark']:
        pg=b.new_context(viewport={'width':390,'height':844},has_touch=True,is_mobile=True,device_scale_factor=2,color_scheme=sch).new_page(); errs=[]; pg.on('pageerror',lambda e:errs.append(str(e)))
        pg.goto('file://'+sys.argv[1]); pg.wait_for_timeout(900)
        print(sch,'badges on map:',pg.locator('#mapsvg .cupbadge').count())
        pg.locator('#tab-steps').click(); li=pg.locator('#steplist li[data-i]').nth(12); li.scroll_into_view_if_needed(); li.click(); pg.wait_for_timeout(700)
        bb=pg.locator('#mapsvg .pin[data-k="13"] .cupbadge').bounding_box()
        pg.touchscreen.tap(bb['x']+bb['width']/2,bb['y']+bb['height']/2); pg.wait_for_timeout(400)
        print(sch,'tap badge -> card:',pg.locator('#mapcard h2').inner_text(),'| row:',pg.locator('#mapcard a.coffeerow .ct').inner_text(),'| href ok:','google.com/maps/search/coffee' in pg.locator('#mapcard a.coffeerow').get_attribute('href'))
        pg.evaluate('scrollTo(0,0)'); pg.wait_for_timeout(200)
        pg.screenshot(path=f'{sys.argv[2]}/cf_map_{sch}.png')
        pg.locator('#mapcard .direction').scroll_into_view_if_needed(); pg.evaluate('window.scrollBy(0,-240)'); pg.wait_for_timeout(200)
        pg.screenshot(path=f'{sys.argv[2]}/cf_card_{sch}.png')
        pg.locator('#stepbar [data-act=next]').click(); pg.wait_for_timeout(300)
        print(sch,'non-coffee stop has row:',pg.locator('#mapcard a.coffeerow').count(),'| errors',errs)
    b.close()
