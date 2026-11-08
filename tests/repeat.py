import sys
import os
from playwright.sync_api import sync_playwright
txt=open(sys.argv[3]).read()
with sync_playwright() as p:
    b=p.chromium.launch(executable_path='/usr/bin/google-chrome',args=['--no-sandbox'])
    pg=b.new_context(viewport={'width':390,'height':844}).new_page(); errs=[]; pg.on('pageerror',lambda e:errs.append(str(e)))
    pg.goto('file://'+os.path.abspath(sys.argv[1])); pg.wait_for_timeout(1000)
    pg.locator('#guidebtn').click(); pg.locator('#bookbtn').click(); pg.locator('#bookpaste').fill(txt); pg.locator('#booksort').click(); pg.wait_for_timeout(500); pg.locator('#guideclose').click()
    res=pg.evaluate("""(()=>{ const out=[]; const ks=walk.steps.map(s=>s.to);
      ks.forEach((k,i)=>{ const c=buildChunks(k); out.push([k, bookParts(k).lead.slice(0,60), c.chunks[1].slice(0,60)]); }); return out; })()""")
    for k,skip,first in res: print(f'{k:>9} skip {skip}  starts: {first}')
    print('errors',errs)
    b.close()
