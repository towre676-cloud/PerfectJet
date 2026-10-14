"""Download official competition files after enrollment. Credential stays in memory."""
import argparse,getpass,json,urllib.request,urllib.error,urllib.parse,hashlib,tempfile,zipfile,shutil,os
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor
COMP='nfl-big-data-bowl-2027'
def fetch(destination):
    dest=Path(destination);dest.mkdir(parents=True,exist_ok=True)
    token=getpass.getpass('Kaggle API token (not saved): ')
    def request(url):
        r=urllib.request.Request(url,headers={'Accept':'application/json'})
        r.add_unredirected_header('Authorization','Bearer '+token)
        return urllib.request.urlopen(r,timeout=120)
    with request(f'https://www.kaggle.com/api/v1/competitions/data/list/{COMP}') as r: metadata=json.load(r)
    records=metadata['files']
    def download(rec):
        name=rec['name'];leaf=Path(name).name;target=dest/leaf
        if target.exists() and target.stat().st_size==rec['totalBytes']:
            print('Already present:',leaf,flush=True)
        else:
            print('Downloading:',leaf,flush=True)
            url=f'https://www.kaggle.com/api/v1/competitions/data/download/{COMP}/'+urllib.parse.quote(name,safe='')
            fd,temp=tempfile.mkstemp(prefix='download-',dir=dest);os.close(fd)
            try:
                with request(url) as r,open(temp,'wb') as f:shutil.copyfileobj(r,f,8*1024*1024)
                if zipfile.is_zipfile(temp):
                    with zipfile.ZipFile(temp) as z:
                        entries=[i for i in z.infolist() if Path(i.filename).name==leaf]
                        if len(entries)!=1:raise ValueError('unexpected archive member')
                        with z.open(entries[0]) as source,target.open('wb') as f:shutil.copyfileobj(source,f,8*1024*1024)
                else:os.replace(temp,target)
                if target.stat().st_size!=rec['totalBytes']:raise ValueError('size mismatch for '+leaf)
            finally:Path(temp).unlink(missing_ok=True)
        h=hashlib.sha256()
        with target.open('rb') as f:
            for b in iter(lambda:f.read(8*1024*1024),b''):h.update(b)
        result={'file':leaf,'bytes':target.stat().st_size,'sha256':h.hexdigest(),'source':'official Kaggle competition API'}
        print('Verified:',leaf,result['bytes'],'bytes',flush=True)
        return result
    try:
        with ThreadPoolExecutor(max_workers=3) as pool:results=list(pool.map(download,records))
        manifest={'competition':COMP,'files':results,'total_bytes':sum(r['bytes'] for r in results),'credentials_stored':False}
        (dest/'acquisition.json').write_text(json.dumps(manifest,indent=2))
        print(json.dumps({'downloaded_files':len(results),'total_bytes':manifest['total_bytes']},indent=2))
    finally:token=None
if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--destination',default='data');a=p.parse_args()
    try:fetch(a.destination)
    except urllib.error.HTTPError as e:print(json.dumps({'status':e.code,'reason':e.reason}));raise SystemExit(1)
