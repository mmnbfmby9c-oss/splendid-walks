import sys
import os,sys
from playwright.sync_api import sync_playwright
INIT="""(()=>{ window.__spoken=[]; window.SpeechSynthesisUtterance=class{constructor(t){this.text=t;this.voice=null;this.lang='';this.rate=1}};
 Object.defineProperty(window,'speechSynthesis',{value:{getVoices:()=>[{name:'Daniel',lang:'en-GB',voiceURI:'d'}],speak:u=>__spoken.push([u.voice?'named':'device',u.lang,u.rate]),cancel:()=>{},onvoiceschanged:null},configurable:true}); })()"""
with sync_playwright() as p:
    b=p.chromium.launch(executable_path='/usr/bin/google-chrome',args=['--no-sandbox'])
    ctx=b.new_context(viewport={'width':390,'height':844},device_scale_factor=2); ctx.add_init_script(INIT)
    pg=ctx.new_page(); errs=[]; pg.on('pageerror',lambda e:errs.append(str(e)))
    pg.goto('file://'+sys.argv[1]); pg.wait_for_timeout(800)
    pg.locator('#guidebtn').click(); print('status:',pg.locator('#voicestatus').inner_text(),'| btn:',pg.locator('#voicebtn').inner_text())
    pg.locator('#voicebtn').click(); pg.wait_for_timeout(200); print('open btn:',pg.locator('#voicebtn').inner_text())
    pg.locator('#vrate').fill('1.1'); pg.locator('#vrate').dispatch_event('input'); pg.locator('#vpreview').click()
    pg.locator('#voiceform').scroll_into_view_if_needed(); pg.screenshot(path=sys.argv[2]+'/voice_simple.png')
    pg.locator('#guideclose').click(); pg.locator('#mapcard [data-act=listen]').click(); pg.wait_for_timeout(100)
    print('spoken:',pg.evaluate('__spoken')[:2]); print('errors',errs); b.close()
