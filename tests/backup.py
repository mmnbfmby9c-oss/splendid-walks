import os, sys, json, tempfile
from playwright.sync_api import sync_playwright
# Backup round trip: set up "device A", save a backup, load it on a fresh "device B".
app=os.path.abspath(sys.argv[1]); out=sys.argv[2]; txt=open(sys.argv[3]).read()
up=os.path.join(os.environ.get('GUIDE_PHOTOS',''),'Screenshot_2026-11-02_at_')
with sync_playwright() as p:
    b=p.chromium.launch(executable_path='/usr/bin/google-chrome',args=['--no-sandbox'])
    A=b.new_context(viewport={'width':1200,'height':900},accept_downloads=True); pa=A.new_page(); errs=[]; pa.on('pageerror',lambda e:errs.append(str(e)))
    pa.goto('file://'+app); pa.wait_for_timeout(1000)
    pa.locator('#guidebtn').click(); pa.locator('#bookbtn').click(); pa.locator('#bookpaste').fill(txt); pa.locator('#booksort').click(); pa.wait_for_timeout(500)
    pa.locator('#photobtn').click()
    for f in [x for x in ['1_21_18AM','1_21_35AM','1_21_50AM'] if os.path.exists(up+x+'.png')]:
        pa.set_input_files('#photofile', up+f+'.png'); pa.wait_for_timeout(2000); pa.locator('#photoadd').click(); pa.wait_for_timeout(800)
    pa.locator('#photocancel').click(); pa.locator('#guideclose').click()
    for i in range(14): pa.locator('.navbtn.next').click(); pa.wait_for_timeout(30)
    pa.wait_for_timeout(1200); pa.locator('#guidebtn').click(); pa.locator('#backupbtn').click()
    with pa.expect_download() as d: pa.locator('#backupsave').click()
    path=os.path.join(out,'backup.json'); d.value.save_as(path)
    B=b.new_context(viewport={'width':390,'height':844},is_mobile=True,has_touch=True); pb=B.new_page(); pb.on('pageerror',lambda e:errs.append(str(e)))
    pb.goto('file://'+app); pb.wait_for_timeout(1000); pb.locator('#guidebtn').click(); pb.locator('#backupbtn').click()
    pb.set_input_files('#backupfile', path); pb.wait_for_timeout(600); pb.locator('#backupyes').click(); pb.wait_for_timeout(1500)
    print('loaded:',pb.locator('#textstatus').inner_text(),'|',pb.locator('#photostatus').inner_text(),'|',pb.locator('.barinfo').inner_text().split('\n')[0])
    if 'Step 15' not in pb.locator('.barinfo').inner_text(): errs.append('place not restored')
    print('errors',errs); b.close()
