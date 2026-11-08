import sys,time
from playwright.sync_api import sync_playwright
INIT="""(()=>{ let q=[], cur=null; window.__silent=false;
 window.SpeechSynthesisUtterance=class{constructor(t){this.text=t;this.voice=null;this.lang='';this.rate=1}};
 const fire=(u,ev,arg)=>{ if(u&&u[ev]) u[ev](arg||{}); };
 window.__step=()=>{ if(cur){ const u=cur; cur=null; fire(u,'onend'); } if(q.length){ cur=q.shift(); fire(cur,'onstart'); } };
 window.__iosInterrupt=()=>{ const all=(cur?[cur]:[]).concat(q); q=[]; cur=null; all.forEach(u=>fire(u,'onend')); };   // iPhone-style: everything reports 'end'
 window.__qlen=()=>q.length+(cur?1:0); window.__cur=()=>cur&&cur.text.slice(0,48);
 const ss={getVoices:()=>[],speak:u=>{ q.push(u); if(!cur) window.__step(); },
   cancel:()=>{ const c=cur; const rest=q; q=[]; cur=null; if(c) fire(c,'onerror',{error:'interrupted'}); rest.forEach(u=>fire(u,'onerror',{error:'canceled'})); }, onvoiceschanged:null};
 Object.defineProperty(ss,'speaking',{get:()=>!!cur}); Object.defineProperty(ss,'pending',{get:()=>q.length>0});
 Object.defineProperty(window,'speechSynthesis',{value:ss,configurable:true}); })()"""
with sync_playwright() as p:
    b=p.chromium.launch(executable_path='/usr/bin/google-chrome',args=['--no-sandbox'])
    ctx=b.new_context(viewport={'width':390,'height':844},has_touch=True,is_mobile=True,device_scale_factor=2); ctx.add_init_script(INIT)
    pg=ctx.new_page(); errs=[]; pg.on('pageerror',lambda e:errs.append(str(e)))
    pg.goto('file://'+sys.argv[1]); pg.wait_for_timeout(900)
    pg.locator('#guidebtn').click(); pg.locator('#bookbtn').click(); pg.locator('#bookpaste').fill(open(sys.argv[3]).read()); pg.locator('#booksort').click(); pg.wait_for_timeout(400); pg.locator('#guideclose').click()
    pg.locator('#tab-steps').click(); li=pg.locator('#steplist li[data-i]').nth(10); li.scroll_into_view_if_needed(); li.click(); pg.wait_for_timeout(600)
    P=lambda: pg.locator('#mapcard [data-act=listen]'); SUB=lambda: pg.locator('#mapcard .playsub').inner_text()
    print('idle:',P().inner_text(),'|',SUB())
    P().click(); [pg.evaluate('__step()') for _ in range(4)]
    print('playing:',P().inner_text(),'|',SUB(),'| strip:',pg.locator('#nowbar .nbinfo b').inner_text(),'| pin mark:',pg.locator('#mapsvg .pin.speaking').count())
    pg.locator('#mapcard [data-act=readtoggle]').click(); pg.wait_for_timeout(150)
    print('text open, highlighted:',repr((pg.locator('#mapcard .readtext span.now').inner_text() or '')[:45]),'| reading:',pg.evaluate('__cur()'))
    pg.locator('#mapcard .audiobox').scroll_into_view_if_needed(); pg.evaluate('window.scrollBy(0,-120)'); pg.screenshot(path=sys.argv[2]+'/ag_playing.png')
    pg.evaluate('__iosInterrupt()'); pg.wait_for_timeout(3500)
    print('after iPhone-style interrupt: strip visible',pg.locator('#nowbar').is_visible(),'|',pg.locator('#nowbar .nbinfo b').inner_text(),'| card',P().inner_text())
    pg.locator('#nowbar [data-act=resumeaudio]').click(); pg.wait_for_timeout(100); print('resume from:',pg.evaluate('__cur()'))
    for _ in range(80):
        if pg.evaluate('__qlen()')<=1: break
        pg.evaluate('__step()')
    print('last chunk:',pg.evaluate('__cur()'))
    pg.evaluate('__step()'); pg.wait_for_timeout(100)
    print('finished: strip hidden',pg.locator('#nowbar').is_hidden(),'| btn',P().inner_text())
    pg.locator('#stepbar [data-act=next]').click(); pg.wait_for_timeout(300)
    print('Next in guide mode -> playing', pg.locator('#nowbar .nbinfo b').inner_text(), '| first words:', pg.evaluate('__cur()'))
    pg.locator('#nowbar [data-act=stopaudio]').click(); pg.locator('#stepbar [data-act=next]').click(); pg.wait_for_timeout(300)
    print('after Stop, Next does not auto-play: strip hidden',pg.locator('#nowbar').is_hidden())
    pg.locator('#tab-steps').click(); pg.wait_for_timeout(100); P2=None
    pg.locator('#tab-map').click(); pg.locator('#mapcard [data-act=listen]').click(); pg.locator('#tab-steps').click(); pg.wait_for_timeout(150)
    print('steps list speaking mark:',pg.locator('#steplist li.speaking .stopname').inner_text())
    pg.screenshot(path=sys.argv[2]+'/ag_steps.png')
    print('errors',errs); b.close()
