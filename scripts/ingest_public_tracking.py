import urllib.request, json, hashlib, gzip, csv, io, pathlib, concurrent.futures, time, argparse
parser=argparse.ArgumentParser(description='Download public NFL regional-event tracking inputs outside the git checkout.')
parser.add_argument('--output',required=True,type=pathlib.Path)
args=parser.parse_args()
OUT=args.output;OUT.mkdir(parents=True,exist_ok=True)
REPO='ThompsonJamesBliss/nfl-big-data-bowl-regional-event-data'
def api(p):
 req=urllib.request.Request('https://api.github.com/repos/'+REPO+p,headers={'User-Agent':'PerfectJet-public-research'})
 with urllib.request.urlopen(req,timeout=45) as r:return json.load(r)
sha='85da22eeff2f1d5be106faa9dfe06a1205f2defd'
tree=api('/git/trees/'+sha+'?recursive=1')['tree']
files=[x for x in tree if x['type']=='blob']
def get(item):
 name=item['path'];url='https://raw.githubusercontent.com/'+REPO+'/'+sha+'/'+name
 target=OUT/name;target.parent.mkdir(parents=True,exist_ok=True)
 target=target.with_suffix(target.suffix+'.gz') if name.endswith('.csv') else target
 for attempt in range(4):
  try:
   with urllib.request.urlopen(url,timeout=90) as r:raw=r.read()
   if len(raw)!=item['size']:raise ValueError('size mismatch')
   if name.endswith('.csv'):
    target.write_bytes(gzip.compress(raw,compresslevel=6,mtime=0))
    reader=csv.reader(io.StringIO(raw.decode('utf-8-sig')));columns=next(reader);records=sum(1 for row in reader)
   else:target.write_bytes(raw);columns=None;records=None
   result={'source_path':name,'local_path':str(target.relative_to(OUT)),'source_url':url,'git_blob_sha':item['sha'],'sha256':hashlib.sha256(raw).hexdigest(),'source_bytes':len(raw),'stored_bytes':target.stat().st_size,'records':records,'columns':columns}
   print(json.dumps({'done':name,'records':records,'stored_bytes':result['stored_bytes']}),flush=True)
   return result
  except Exception:
   if attempt==3:raise
   time.sleep(2*(attempt+1))
with concurrent.futures.ThreadPoolExecutor(max_workers=6) as pool:
 results=list(pool.map(get,files))
manifest={'source_repository':REPO,'source_commit':sha,'retrieved_utc':time.strftime('%Y-%m-%dT%H:%M:%SZ',time.gmtime()),'provenance':'Public repository posted by the dataset publisher; no repository LICENSE present. Raw input retained for analysis, not relicensed.','files':results}
(OUT/'manifest.json').write_text(json.dumps(manifest,indent=2))
print(json.dumps({'complete':True,'commit':sha,'files':len(results),'raw_bytes':sum(x['source_bytes'] for x in results),'stored_bytes':sum(x['stored_bytes'] for x in results),'tracking_records':sum(x['records'] or 0 for x in results if '/tracking/' in x['source_path'])}),flush=True)
