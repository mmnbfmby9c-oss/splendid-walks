import os, sys
from playwright.sync_api import sync_playwright
# What you SEE in the photo panel: cut-out pictures visible and inside the panel, and "Add to stops" not covered.
app=os.path.abspath(sys.argv[1]); out=sys.argv[2]
up=os.path.join(os.environ.get('GUIDE_PHOTOS',''),'Screenshot_2026-11-02_at_1_21_18AM.png')
if not os.path.exists(up): print('skipped: no GUIDE_PHOTOS'); print('errors []'); sys.exit(0)
with sync_playwright() as p:
    b=p.chromium.launch(executable_path='/usr/bin/google-chrome',args=['--no-sandbox']); errs=[]
    for name,vp,scheme in [('mac',{'width':1440,'height':900},'dark'),('phone',{'width':390,'height':844},'light')]:
        pg=b.new_context(viewport=vp,color_scheme=scheme).new_page(); pg.on('pageerror',lambda e:errs.append(str(e)))
        pg.goto('file://'+app); pg.wait_for_timeout(1000)
        pg.locator('#guidebtn').click(); pg.locator('#photobtn').click(); pg.set_input_files('#photofile',up); pg.wait_for_timeout(2200)
        r=pg.evaluate("""(()=>{ const sheet=document.querySelector('#guidesheet .frame').getBoundingClientRect();
          const imgs=[...document.querySelectorAll('#phototiles img')];
          const vis=imgs.filter(i=>{const b=i.getBoundingClientRect(), cs=getComputedStyle(i); return +cs.opacity>0.9 && b.width>40 && b.left>=sheet.left-1 && b.right<=sheet.right+1;}).length;
          const btn=document.querySelector('#photoadd'); btn.scrollIntoView({block:'center'}); const bb=btn.getBoundingClientRect();
          const top=document.elementFromPoint(bb.left+bb.width/2, bb.top+bb.height/2);
          return [imgs.length, vis, top===btn || btn.contains(top)]; })()""")
        print(name,'pictures cut out:',r[0],'| visible inside the panel:',r[1],'| Add to stops reachable:',r[2])
        if not (r[0]>0 and r[1]==r[0] and r[2]): errs.append(f'{name}: photo panel layout broken')
        pg.screenshot(path=os.path.join(out,f'photopanel_{name}.png'))
    print('errors',errs); b.close()
