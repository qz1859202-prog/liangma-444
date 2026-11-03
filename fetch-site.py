from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from urllib.parse import quote
import hashlib,json,time,urllib.request,zipfile
raw=Path('site-manifest.json').read_bytes()
assert hashlib.sha256(raw).hexdigest()=='65f60beb0f999dbec430fe28bdfaff2a240c55a81a1b556de15ca0e5aaea857c', 'Manifest does not match this release'
manifest=json.loads(raw)
archive=Path('site-code.zip')
assert hashlib.sha256(archive.read_bytes()).hexdigest()==manifest['code_sha256'], 'Code archive mismatch'
root=Path('_site');root.mkdir(exist_ok=True)
with zipfile.ZipFile(archive) as bundle:
 for item in bundle.infolist():
  target=root/item.filename
  assert target.resolve().is_relative_to(root.resolve()), 'Unsafe archive path'
 bundle.extractall(root)
def fetch(item):
 target=root/item['path'];target.parent.mkdir(parents=True,exist_ok=True)
 for attempt in range(5):
  try:
   req=urllib.request.Request(manifest['media_origin']+'/'+quote(item['path'],safe='/'),headers={'User-Agent':'Liangma-Pages-Release/1.0'})
   with urllib.request.urlopen(req,timeout=90) as response:data=response.read()
   assert len(data)==item['bytes'] and hashlib.sha256(data).hexdigest()==item['sha256'], 'Media checksum mismatch: '+item['path']
   target.write_bytes(data)
   return
  except Exception:
   if attempt==4:raise
   time.sleep(2**attempt)
with ThreadPoolExecutor(max_workers=6) as pool:list(pool.map(fetch,manifest['media']))
(root/'.nojekyll').touch()
assert len(list(root.glob('films/*/index.m3u8')))==10
print('Verified '+manifest['edition']+' portfolio: standalone site, 10 complete films, no ChatGPT dependency.')
