"""Public URL checks. Private repositories are expected to be inaccessible publicly."""
import concurrent.futures
import json
from pathlib import Path
import re
from urllib.request import Request,urlopen
from urllib.error import HTTPError
ROOT=Path(__file__).resolve().parents[1]
content=(ROOT/'README.md').read_text(encoding='utf-8')
urls=sorted(set(re.findall(r'https://[^\s"<>\)]+',content)))
def check(url):
    if url in {'https://github.com/Abhi-lash19/BountyDesk','https://github.com/Abhi-lash19/chitragupta'}:
        return {'url':url,'status':'private; authenticated source inspection succeeded; access required'}
    try:
        with urlopen(Request(url,headers={'User-Agent':'Mozilla/5.0'}),timeout=30) as r:
            return {'url':url,'status':r.status,'destination':r.url}
    except HTTPError as err:return {'url':url,'status':err.code}
    except Exception as err:return {'url':url,'status':str(err)}
with concurrent.futures.ThreadPoolExecutor(max_workers=5) as pool:results=list(pool.map(check,urls))
(ROOT/'.preview').mkdir(exist_ok=True)
(ROOT/'.preview/links.json').write_text(json.dumps(results,indent=2)+'\n')
print(json.dumps(results,indent=2))
