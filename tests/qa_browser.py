from playwright.sync_api import sync_playwright
from pathlib import Path
import json, urllib.request, urllib.error, zipfile, io
ROOT=Path(__file__).resolve().parents[1]
BASE='http://127.0.0.1:8765'
def api(path,data=None,raw=None,headers={}):
 req=urllib.request.Request(BASE+path,data=raw if raw is not None else (json.dumps(data).encode() if data is not None else None),headers=headers)
 try:
  with urllib.request.urlopen(req) as r:return r.status,r.read()
 except urllib.error.HTTPError as e:return e.code,e.read()
def select(page,start,end):
 page.locator('#reader').evaluate('''(el,p)=>{const t=el.firstChild;let r=document.createRange();r.setStart(t,p[0]);r.setEnd(t,p[1]);let s=window.getSelection();s.removeAllRanges();s.addRange(r);el.dispatchEvent(new MouseEvent('mouseup',{bubbles:true}))}''',[start,end])
with sync_playwright() as p:
 browser=p.chromium.launch(executable_path='/usr/bin/chromium',headless=True,args=['--no-sandbox'])
 page=browser.new_page(viewport={'width':1440,'height':1000}); errors=[];page.on('pageerror',lambda e:errors.append(str(e)))
 page.goto(BASE)
 for sample in ['A-small-reading-experiment.pdf','带着问题读书.epub']:
  page.locator('#file').set_input_files(str(ROOT/'samples'/sample));page.wait_for_function('(t)=>document.querySelector("#title").textContent===t',arg=sample.rsplit('.',1)[0]);page.wait_for_timeout(100)
  text=page.locator('#reader').inner_text();select(page,0,min(30,len(text)))
  page.locator('#capture').click();page.locator('#question').fill('QA: What does this mean?');page.locator('#save').click();page.locator('.note').last.wait_for()
  note=page.locator('.note').last
  for action,txt in [('followup','QA follow-up'),('answer','QA manual answer'),('insight','QA new insight')]:
   note.locator('textarea').fill(txt);note.locator('[data-action='+action+']').click();page.wait_for_timeout(150)
  note.locator('[data-action=ai]').click();page.wait_for_timeout(100);assert 'AI 尚未配置' in page.locator('#toast').inner_text()
  note.locator('[data-anchor]').click();assert page.locator('#reader mark').inner_text()==text[:30]
  page.reload();page.locator('.note').last.wait_for();assert 'QA new insight' in page.locator('#notes').inner_text()
  with page.expect_download() as d:page.locator('#export').click()
  dl=d.value; dest=ROOT/'tests'/('qa-'+sample+'.zip');dl.save_as(str(dest));z=zipfile.ZipFile(dest);md=z.read('阅读笔记.md').decode();assert 'QA new insight' in md and 'source.html#note-' in md and 'attachments/' in md
  print('PASS',sample,'import, selection, save, followup, manual answer, insight, missing AI, restore, highlight, export',flush=True)
 page.screenshot(path=str(ROOT/'tests'/'reading-screenshot.png'),full_page=True)
 # Verify draft quote cannot silently change its meaning when another passage is selected.
 select(page,0,8);page.locator('#capture').click();old=page.locator('#draftquote').inner_text();page.locator('#question').fill('QA stale draft');select(page,10,20);page.locator('#save').click();page.wait_for_timeout(150);new=page.locator('.note').last.locator('.quote').inner_text()
 print('DRAFT_SELECTION',json.dumps({'displayed':old,'saved':new,'match':old==new},ensure_ascii=False),flush=True)
 print('BROWSER_ERRORS',errors,flush=True)
 browser.close()
books=json.loads(api('/api/books')[1]);bid=books[0]['id'];notes=json.loads(api('/api/books/'+bid+'/notes')[1]);nid=notes[0]['id']
for label,path,data,raw,headers,expected in [
 ('bad json','/api/notes',None,b'{',{},400),('invalid PDF','/api/import',None,b'not a pdf',{'X-Filename':'broken.pdf'},400),('invalid EPUB','/api/import',None,b'not epub',{'X-Filename':'broken.epub'},400),('wrong type','/api/import',None,b'txt',{'X-Filename':'text.txt'},400),('empty followup','/api/notes/'+nid+'/followup',{'text':''},None,{},400),('missing AI','/api/notes/'+nid+'/ai',{'consent':True},None,{},503),('cross origin','/api/notes',{},None,{'Origin':'https://evil.example'},403),('missing book','/api/books/notfound',None,None,{},404),('wrong quote','/api/notes',{'book_id':bid,'section':0,'start':0,'end':2,'quote':'wrong','question':'x'},None,{},400)]:
 status,body=api(path,data,raw,headers);assert status==expected,(label,status,body);print('PASS',label,status,flush=True)
