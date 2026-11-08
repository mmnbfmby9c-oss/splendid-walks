import sys
import os,io,re,math
from playwright.sync_api import sync_playwright
from PIL import Image, ImageDraw
def fake_tile(z,x,y,dark):
    im=Image.new('RGB',(512,512),(40,44,60) if dark else (236,233,226)); d=ImageDraw.Draw(im)
    d.rectangle([0,0,511,511],outline=(200,190,170) if not dark else (70,74,95),width=2)
    # draw a "street" along true lat/lng lines to check alignment: the latitude line 51.5070 and longitude -0.1350
    n=2**z
    def px(lat,lng):
        s=math.sin(math.radians(lat)); X=(lng+180)/360*n*512; Y=(0.5-math.log((1+s)/(1-s))/(4*math.pi))*n*512; return X-x*512, Y-y*512
    for lat in [51.5050,51.5070,51.5090]:
        a=px(lat,-0.15); b=px(lat,-0.11); d.line([a,b],fill=(255,255,255) if not dark else (90,95,120),width=6)
    for lng in [-0.1400,-0.1350,-0.1300,-0.1250]:
        a=px(51.52,lng); b=px(51.49,lng); d.line([a,b],fill=(255,255,255) if not dark else (90,95,120),width=6)
    d.text((10,10),f'{z}/{x}/{y}',fill=(150,140,120))
    buf=io.BytesIO(); im.save(buf,'PNG'); return buf.getvalue()
def handler(route):
    m=re.search(r'()/(\d+)/(\d+)/(\d+)\.png',route.request.url)
    route.fulfill(status=200,content_type='image/png',body=fake_tile(int(m[2]),int(m[3]),int(m[4]),False))
with sync_playwright() as p:
    b=p.chromium.launch(executable_path='/usr/bin/google-chrome',args=['--no-sandbox'])
    for sch in ['light','dark']:
        ctx=b.new_context(viewport={'width':390,'height':844},device_scale_factor=2,color_scheme=sch,is_mobile=True,has_touch=True,
            geolocation={'latitude':51.50660,'longitude':-0.13200,'accuracy':15},permissions=['geolocation'])
        ctx.route(re.compile(r'tile\.openstreetmap\.org'),handler)
        pg=ctx.new_page(); errs=[]; pg.on('pageerror',lambda e:errs.append(str(e)))
        pg.goto('file://'+os.path.abspath(sys.argv[1])); pg.wait_for_timeout(1500)
        for i in range(25): pg.locator('.navbtn.next').click(); pg.wait_for_timeout(30)
        pg.evaluate('scrollTo(0,0)'); pg.wait_for_timeout(300)
        pg.locator('#zme').tap(); pg.wait_for_timeout(1500)
        print(sch,'chip:',pg.locator('#nearchip').inner_text(),'| tiles loaded:',pg.locator('#tiles img.ok').count(),'| sketch hidden:',pg.evaluate("getComputedStyle(document.querySelector('.sketch')).display"))
        pg.screenshot(path=f'MP_{sch}.png')
        # move to stop 27 (Scott) -> should say at next stop
        ctx.set_geolocation({'latitude':51.50690,'longitude':-0.13190,'accuracy':10}); pg.wait_for_timeout(1500)
        print(sch,'at Scott, chip:',pg.locator('#nearchip').inner_text())
        pg.locator('#nearchip').tap(); pg.wait_for_timeout(400); print(sch,'after tapping chip:',pg.locator('.barinfo').inner_text().replace('\n',' | '),'| chip:',pg.locator('#nearchip').inner_text())
        pg.locator('#zfit').tap(); pg.wait_for_timeout(1200); pg.screenshot(path=f'MP_fit_{sch}.png')
        print(sch,'errors',errs)
    b.close()
