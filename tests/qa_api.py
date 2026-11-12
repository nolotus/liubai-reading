import os,tempfile,sys,json,io,zipfile,hashlib
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
os.environ['READING_DATA']=tempfile.mkdtemp(prefix='reading-qa-');os.environ.pop('OPENAI_API_KEY',None);sys.path.insert(0,str(ROOT));import app
class Harness(app.Handler):
 def __init__(self,path,raw=b'',headers=None):
  self.path=path;self.headers={'Content-Length':str(len(raw)),'Host':'127.0.0.1:8765',**(headers or {})};self.rfile=io.BytesIO(raw);self.result=None
 def send(self,status,data,typ='application/json; charset=utf-8'):self.result=(status,data,typ)
def req(path,data=None,raw=None,headers=None):
 h=Harness(path,raw if raw is not None else (json.dumps(data).encode() if data is not None else b''),headers);h.do_GET() if data is None and raw is None else h.do_POST();return h.result
for filename in ['A-small-reading-experiment.pdf','带着问题读书.epub']:
 raw=(ROOT/'samples'/filename).read_bytes();status,d,_=req('/api/import',raw=raw,headers={'X-Filename':filename});assert status==201,(status,d);bid=d['id'];assert req('/api/import',raw=raw,headers={'X-Filename':filename})[1]['duplicate']
 book=req('/api/books/'+bid)[1];assert len(book['sections'])==2
 text=book['sections'][0]['text'];start=text.index('📖') if '📖' in text else 0;end=min(len(text),start+30)
 status,d,_=req('/api/notes',{'book_id':bid,'section':0,'start':start,'end':end,'quote':text[start:end],'question':'First question'});assert status==201,(status,d);nid=d['id']
 for action,txt in [('followup','Follow-up'),('answer','Manual answer'),('insight','New understanding')]:assert req('/api/notes/'+nid+'/'+action,{'text':txt})[0]==200
 notes=req('/api/books/'+bid+'/notes')[1];assert len(notes)==1 and len(notes[0]['turns'])==3 and notes[0]['insights'][0]['text']=='New understanding';assert notes[0]['quote']==text[start:end]
 assert req('/api/notes/'+nid+'/ai',{'consent':True})[0]==503;assert len(req('/api/books/'+bid+'/notes')[1][0]['turns'])==3
 z=zipfile.ZipFile(io.BytesIO(req('/api/books/'+bid+'/export')[1]));md=z.read('阅读笔记.md').decode();source=z.read('source.html').decode();assert 'source.html#note-'+nid in md and 'id="note-'+nid+'"' in source;assert z.read('attachments/'+bid+'.'+book['kind'])==raw;assert json.loads(z.read('anchors.json'))['notes'][0]['quote']==text[start:end]
 print('PASS',filename,'import, duplicate, 2 sections, codepoint anchor, question, followup, manual answer, insight, missing AI retains data, ZIP markdown/attachment/anchor integrity',flush=True)
for label,path,data,raw,headers,expected in [
 ('bad json','/api/notes',None,b'{',{},400),('invalid PDF','/api/import',None,b'not a pdf',{'X-Filename':'broken.pdf'},400),('invalid EPUB','/api/import',None,b'not epub',{'X-Filename':'broken.epub'},400),('wrong type','/api/import',None,b'txt',{'X-Filename':'text.txt'},400),('empty followup','/api/notes/'+nid+'/followup',{'text':''},None,{},400),('missing AI','/api/notes/'+nid+'/ai',{'consent':True},None,{},503),('cross origin','/api/notes',{},None,{'Origin':'https://evil.example'},403),('missing book','/api/books/notfound',None,None,{},404),('wrong quote','/api/notes',{'book_id':bid,'section':0,'start':0,'end':2,'quote':'wrong','question':'x'},None,{},400),('negative section','/api/notes',{'book_id':bid,'section':-1,'start':0,'end':2,'quote':'ab','question':'x'},None,{},400)]:
 status,body,_=req(path,data,raw,headers);assert status==expected,(label,status,body);print('PASS',label,status,flush=True)
# Host-header validation protects loopback apps against DNS rebinding.
print('HOST_CHECK',req('/api/books',headers={'Host':'attacker.example'})[0],flush=True)
print('ALL API CHECKS FINISHED; isolated data:',os.environ['READING_DATA'])
from concurrent.futures import ThreadPoolExecutor
before=len(req('/api/books/'+bid+'/notes')[1][0]['turns'])
with ThreadPoolExecutor(max_workers=8) as pool:
 results=list(pool.map(lambda i:req('/api/notes/'+nid+'/followup',{'text':f'Concurrent {i}'})[0],range(20)))
assert results==[200]*20,results
latest=req('/api/books/'+bid+'/notes')[1][0]
assert len(latest['turns'])==before+20
assert {t['text'] for t in latest['turns'] if t['text'].startswith('Concurrent ')}=={f'Concurrent {i}' for i in range(20)}
print('PASS 20 simultaneous follow-ups without lost writes',flush=True)
for payload in ([],None):
 assert req('/api/notes',raw=json.dumps(payload).encode())[0]==400
for action in ('followup','answer','insight'):
 assert req('/api/notes/'+nid+'/'+action,{'text':None})[0]==400
assert req('/api/notes',{'book_id':bid,'section':0,'start':0,'end':1,'quote':text[0],'question':None})[0]==400
print('PASS object and string payload validation',flush=True)
# Simulate an in-flight AI response locally: never call a provider.
import threading
ready=threading.Event();release=threading.Event();original_urlopen=app.urllib.request.urlopen
class FakeResponse(io.BytesIO):
 def __enter__(self):return self
 def __exit__(self,*args):self.close()
def fake_urlopen(*args,**kwargs):
 ready.set();assert release.wait(5),'AI simulation timed out'
 return FakeResponse(json.dumps({'choices':[{'message':{'content':'QA MOCK RESPONSE ONLY'}}]}).encode())
app.urllib.request.urlopen=fake_urlopen;os.environ['OPENAI_API_KEY']='qa-local-placeholder'
try:
 with ThreadPoolExecutor(max_workers=2) as pool:
  pending=pool.submit(req,'/api/notes/'+nid+'/ai',{'consent':True})
  assert ready.wait(5)
  assert req('/api/notes/'+nid+'/followup',{'text':'Question during simulated AI'})[0]==200
  release.set();assert pending.result()[0]==200
 latest=req('/api/books/'+bid+'/notes')[1][0]['turns']
 assert latest[-2]['text']=='Question during simulated AI' and latest[-1]['text']=='QA MOCK RESPONSE ONLY'
 print('PASS follow-up survives concurrent simulated AI response; no external request',flush=True)
finally:
 release.set();app.urllib.request.urlopen=original_urlopen;os.environ.pop('OPENAI_API_KEY',None)
blank=app.fitz.open();blank.new_page();blank_raw=blank.tobytes()
assert req('/api/import',raw=blank_raw,headers={'X-Filename':'scan.pdf'})[0]==400
locked=app.fitz.open();p=locked.new_page();p.insert_text((50,50),'Protected sample')
locked_raw=locked.tobytes(encryption=app.fitz.PDF_ENCRYPT_AES_256,owner_pw='qa-owner',user_pw='qa-reader')
assert req('/api/import',raw=locked_raw,headers={'X-Filename':'locked.pdf'})[0]==400
assert req('/api/import',raw=b'',headers={'X-Filename':'large.pdf','Content-Length':'30000001'})[0]==413
print('PASS no-text PDF, password-protected PDF, oversized declared body',flush=True)
