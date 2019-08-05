from aiohttp import web
from pathlib import Path
from glob import glob
from collections import defaultdict
import re

async def index(request):
    index_page = """
<!DOCTYPE html>
<html>
<head>
<title>Vuejspython</title>
<link rel=stylesheet href="/static/picnic.min.css">
<style>
body { margin: 2em; }
</style>
</head>
<body>
<h1>HTML files for Vuejspython</h1>
<ul>
""" + '\n'.join([
    '<li><a href="{}">{}</a></li>'.format(p, p) for p in sorted(glob('**/*.html', recursive=True))
]) + """
</ul>
</body>
</html>
    """
    return web.Response(text=index_page, content_type='text/html')

async def patched_html(request):
    print("# HTTP, filesystem:", request.path)
    f = request.path
    if f.startswith('/'): f = f[1:]
    with open(f, 'r') as myfile:
        data = myfile.read()
        #data = data.replace(r'src="vuejspython.js"', 'src="/static/vuejspython.js"')
    return web.Response(text=data, content_type='text/html')

type_from_extension = defaultdict(lambda:'text/html')
type_from_extension['css'] = 'text/css'
type_from_extension['js'] = 'text/javascript'

async def embedded_static(request):
    print("# HTTP, embedded:", request.path)
    static_dir = Path(__file__).with_name('static')
    f = str(static_dir) + '/' + re.sub(r'.*/lib/', '', request.path)
    with open(f, 'r') as myfile:
        data = myfile.read()
    ext = re.sub(r'.*[.]', '', f)
    ct = type_from_extension[ext]
    return web.Response(text=data, content_type=ct)

def run_http_server(port, host='localhost'):
    #static_dir = Path(__file__).with_name('static')
    app = web.Application()
    app.router.add_get('/', index)
    app.router.add_get('/{file:.*[.]html}', patched_html)
    app.router.add_get('/{file:.*lib/.*}', embedded_static)
    app.router.add_static('/', '.', show_index=True)
    web.run_app(app, host=host, port=port)
