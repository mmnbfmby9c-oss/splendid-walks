import sys
from playwright.sync_api import sync_playwright
def swipe(cdp,x,y0,y1,x1=None,steps=12):
    x1=x if x1 is None else x1
    cdp.send('Input.dispatchTouchEvent',{'type':'touchStart','touchPoints':[{'x':x,'y':y0}]})
    for i in range(1,steps+1):
        cdp.send('Input.dispatchTouchEvent',{'type':'touchMove','touchPoints':[{'x':x+(x1-x)*i/steps,'y':y0+(y1-y0)*i/steps}]})
    cdp.send('Input.dispatchTouchEvent',{'type':'touchEnd','touchPoints':[]})
VB="document.getElementById('mapsvg').getAttribute('viewBox')"
with sync_playwright() as p:
    b=p.chromium.launch(executable_path='/usr/bin/google-chrome',args=['--no-sandbox'])
    ctx=b.new_context(viewport={'width':390,'height':844},has_touch=True,is_mobile=True)
    pg=ctx.new_page(); pg.goto('file://'+sys.argv[1]); pg.wait_for_timeout(1200)
    cdp=ctx.new_cdp_session(pg)
    pg.evaluate('scrollTo(0,0)'); swipe(cdp,195,230,60); pg.wait_for_timeout(500); print('off-map swipe scrollY',pg.evaluate('scrollY'))
    pg.evaluate('scrollTo(0,0)'); pg.wait_for_timeout(200); bx=pg.locator('#mapbox').bounding_box(); y=bx['y']+bx['height']*0.6
    v=pg.evaluate(VB); swipe(cdp,195,y,y-250); pg.wait_for_timeout(500); print('on-map thumb swipe scrollY',pg.evaluate('scrollY'),'| map unchanged',pg.evaluate(VB)==v)
    pg.evaluate('scrollTo(0,0)'); pg.wait_for_timeout(200); bx=pg.locator('#mapbox').bounding_box(); y=bx['y']+bx['height']*0.5
    v=pg.evaluate(VB); swipe(cdp,120,y,y+5,x1=300); pg.wait_for_timeout(150)
    print('sideways one-finger: hint', 'on' in (pg.locator('#maphint').get_attribute('class') or ''),'| map unchanged',pg.evaluate(VB)==v)
    b.close()
