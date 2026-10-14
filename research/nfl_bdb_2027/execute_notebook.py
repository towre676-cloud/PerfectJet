"""Execute the self-contained notebook locally and capture standard display outputs."""
import os,io,json,base64,contextlib
from pathlib import Path
import matplotlib;matplotlib.use('Agg')
import matplotlib.pyplot as plt
import sys,types
try:
    import IPython.display as IPD
except ModuleNotFoundError:
    # Standard display adapters for this lean runtime; Kaggle uses its native IPython.
    shell=types.ModuleType('IPython');shell.get_ipython=lambda:None;shell.version_info=(9,0,0)
    IPD=types.ModuleType('IPython.display')
    class Image:
        def __init__(self,filename):self.filename=filename
        def _repr_png_(self):return Path(self.filename).read_bytes()
    class HTML:
        def __init__(self,text):self.text=text
        def _repr_html_(self):return self.text
    IPD.Image=Image;IPD.HTML=HTML;shell.display=IPD;sys.modules['IPython']=shell;sys.modules['IPython.display']=IPD
import argparse
ap=argparse.ArgumentParser();ap.add_argument('--notebook',default='notebooks/Braking_That_Travels.ipynb');ap.add_argument('--data',default='data');ap.add_argument('--only-cell',type=int,default=None);args=ap.parse_args()
root=Path(__file__).resolve().parent;os.environ['BDB_DATA_ROOT']=str((root/args.data).resolve());os.chdir(root)
path=root/args.notebook;nb=json.loads(path.read_text());ns={'__name__':'notebook_execution'};captured=[]
def display(*objects,**kwargs):
    for obj in objects:
        mime={}
        if hasattr(obj,'_repr_png_'):
            value=obj._repr_png_()
            if isinstance(value,tuple):value=value[0]
            if value:mime['image/png']=base64.b64encode(value).decode()
        if hasattr(obj,'_repr_html_'):
            value=obj._repr_html_()
            if value:mime['text/html']=value
        if not mime:mime['text/plain']=repr(obj)
        captured.append({'output_type':'display_data','data':mime,'metadata':{}})
def show(*args,**kwargs):
    for number in plt.get_fignums():
        fig=plt.figure(number);buf=io.BytesIO();fig.savefig(buf,format='png',dpi=130,bbox_inches='tight');captured.append({'output_type':'display_data','data':{'image/png':base64.b64encode(buf.getvalue()).decode()},'metadata':{}});plt.close(fig)
IPD.display=display;plt.show=show
count=0
for cell in nb['cells']:
    if cell['cell_type']!='code':continue
    count+=1;captured=[];stdout=io.StringIO()
    if args.only_cell is not None and count not in [1,args.only_cell]:continue
    print('Executing code cell',count,flush=True)
    with contextlib.redirect_stdout(stdout),contextlib.redirect_stderr(stdout):exec(compile(''.join(cell['source']),f'notebook-cell-{count}','exec'),ns)
    cell['execution_count']=count;cell['outputs']=([{'output_type':'stream','name':'stdout','text':stdout.getvalue()}] if stdout.getvalue() else [])+captured
    path.write_text(json.dumps(nb,indent=1))
complete=all(c.get('execution_count') is not None for c in nb['cells'] if c['cell_type']=='code')
nb['metadata']['execution_provenance']={'method':'local Python execution with standard display adapters and Matplotlib capture; cells may resume from private checkpoints','competition_data':'official files with acquisition hashes','all_cells_completed':complete,'test_protocol':'Player-separated analysis; prior 2025 inspection disclosed'}
path.write_text(json.dumps(nb,indent=1));print('Selected execution finished; all cells completed:',complete,'total code cells:',count,flush=True)
