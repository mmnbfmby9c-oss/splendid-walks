# Walk 2: switch from the walk list, sort the chapter text, check the split, parts, map and switch back.
import sys, os
from playwright.sync_api import sync_playwright
app=os.path.abspath(sys.argv[1]); txt=open(sys.argv[2]).read() if len(sys.argv)>2 and os.path.exists(sys.argv[2]) else None
with sync_playwright() as p:
    b=p.chromium.launch(executable_path='/usr/bin/google-chrome',args=['--no-sandbox'])
    pg=b.new_context(viewport={'width':390,'height':844},device_scale_factor=1,is_mobile=True,has_touch=True).new_page(); errs=[]; pg.on('pageerror',lambda e:errs.append(str(e)))
    pg.goto('file://'+app); pg.wait_for_timeout(900)
    pg.locator('#banner').click(); pg.wait_for_timeout(300)
    print('list:', pg.locator('#walklist').inner_text().replace('\n',' | ')[:400])
    pg.locator('#walklist .pt[data-w="2"]').first.click(); pg.wait_for_timeout(1200)
    print('now walk', pg.evaluate('walk.id'), 'step', pg.evaluate('walkIdx'), pg.locator('#bkick').inner_text(), '/', pg.locator('#btitle').inner_text())
    assert pg.evaluate('walk.id')==2
    print('parts', pg.evaluate("walk.parts.map(x=>{const p=partOf(x.from);return [p.n,p.title,p.from,p.to,partMinutes(p)]})"))
    # steps reference real stops, every stop has a step
    print('check', pg.evaluate("[walk.steps.every(s=>stopBy(s.to)), walk.stops.every(s=>stepFor(s.k)>=0), walk.steps.length, walk.stops.length]"))
    if txt:
        pg.locator('#guidebtn').click(); pg.locator('#bookbtn').click(); pg.locator('#bookpaste').fill(txt); pg.locator('#booksort').click(); pg.wait_for_timeout(600)
        pg.locator('#guideclose').click()
        rows=pg.evaluate("walk.steps.map(s=>{const t=bookFor(s.to); const bp=bookParts(s.to); return [s.to, t.length, (bp.lead||'').slice(0,70), t.slice(0,50)]})")
        for r in rows: print('  ',r)
        print('empty:', [r[0] for r in rows if r[1]==0])
        print('end part1:', pg.evaluate("buildChunks('9').chunks.slice(-1)[0].slice(0,100)"))
    print('route0', pg.evaluate("decodeURIComponent(routeInfo(0).url)")[:300])
    pg.evaluate('window.scrollTo(0,0)'); pg.wait_for_timeout(500); pg.screenshot(path="W2_card.png"); pg.locator("#tab-steps").click(); pg.wait_for_timeout(400); pg.screenshot(path="W2_steps.png", full_page=True); pg.locator("#tab-map").click(); pg.wait_for_timeout(300)
    # back to walk 1
    pg.locator('#banner').click(); pg.wait_for_timeout(300); pg.locator('#walklist .pt[data-w="1"]').first.click(); pg.wait_for_timeout(1200)
    print('back to walk', pg.evaluate('walk.id'), 'book keys w1', pg.evaluate("Object.keys(book).length"))
    assert pg.evaluate('walk.id')==1
    print('errors', errs); assert not errs
    b.close()
