
from fastapi import FastAPI, Response, Request
from fastapi.staticfiles import StaticFiles
from starlette.responses import FileResponse

import os
import re
import sys
import json
import pathlib

import click

@click.command()
@click.argument('vue_file', default='simple.vue')
@click.option('--trust-python', is_flag=True, help='Trust Python code execution')
@click.option('--keep-params', is_flag=True, help='Keep parameters file (.params.json)')
@click.option('--port', default=42042, help='Port to run the server on')
@click.option('--host', default='localhost', help='Host/interface to run the server on')
@click.argument('params', nargs=-1)
def cli(vue_file, trust_python, keep_params, port, host, params):

    if not keep_params:
        json.dump([vue_file, *params], open(".params.json", "w"))

    sys.argv = []
    if trust_python:
        sys.argv.append('--trust-python')
    sys.argv = [*sys.argv, vue_file, *params]
    import uvicorn
    uvicorn.run('vuejspython.run:startup', reload=True, host=host, port=port)

if __name__ == "__main__":
    cli()

def startup():
    TRUST_PYTHON = False
    if sys.argv[0] == '--trust-python':
        TRUST_PYTHON = True
        sys.argv = sys.argv[1:]
    
    if len(sys.argv) == 0:
        return
    RUNNER_PATH = os.path.realpath(__file__)
    RUNNER_DIR = pathlib.Path(os.path.dirname(RUNNER_PATH))
    # if file does not exist AND name starts with :, it is a builtin file
    if not os.path.exists(sys.argv[0]) and sys.argv[0].startswith(":"):
        BUILTIN = RUNNER_DIR / "builtin"
        sys.argv[0] = str(BUILTIN / (sys.argv[0][1:] + ".vue"))
    VUE_PATH = os.path.realpath(sys.argv[0])
    VUE_DIR = pathlib.Path(os.path.dirname(VUE_PATH))

    # one can hack and redefine this function but anyway if we set --trust-python, everything is open
    def is_safe_path(relative_path):
        cwd = pathlib.Path.cwd()
        path = pathlib.PurePath(relative_path)
        joined_path = cwd / path
        return joined_path.is_relative_to(cwd)
    
    def create_parent_dirs(filename):
        pathlib.Path(filename).parent.mkdir(parents=True, exist_ok=True)

    app = FastAPI()

    @app.get("/", response_model=None)
    async def root():
        return FileResponse(RUNNER_DIR / "index.html", headers=NO_CACHE_HEADERS)

    @app.get("/__entrypoint.vue", response_model=None)
    async def vue():
        return FileResponse(VUE_PATH, headers=NO_CACHE_HEADERS)

    # API endpoint to list files in the cwd
    @app.get("/.files", response_model=None)
    async def list_files():
        files = []
        # path of all files, recursively
        for file in pathlib.Path(".").rglob("*"):
            if file.is_file():
                files.append(str(file))
            else:
                files.append(str(file) + "/")
        return {"files": files}

    # API endpoint to write a file
    @app.post("/.file/{filename:path}", response_model=None)
    async def write_file(filename: str, request: Request):
        if not is_safe_path(filename):
            return Response(status_code=400, content="Invalid path (good try!)")
        create_parent_dirs(filename)
        with open(filename, "wb") as f:
            f.write(await request.body())
        return "File written successfully"

    # API endpoint to delete a file
    @app.delete("/.file/{filename:path}", response_model=None)
    async def delete_file(filename: str):
        if not is_safe_path(filename):
            return Response(status_code=400, content="Invalid path (good try!)")
        pathlib.Path(filename).unlink()
        return "File deleted successfully"

    #app.mount("/", StaticFiles(directory='./'), name="static user local")
    #StaticFiles.is_not_modified = lambda *args, **kwargs: False
    NO_CACHE_HEADERS = {
        "Cache-Control": "max-age=0, no-cache, no-store, must-revalidate",
        "Pragma": "no-cache",
        "Expires": "0",
    }
    class NoCacheStaticFiles(StaticFiles):
        def file_response(self, *args, **kwargs) -> Response:
            resp = super().file_response(*args, **kwargs)
            for k, v in NO_CACHE_HEADERS.items():
                resp.headers.setdefault(k, v)
            return resp
    app.mount("/.runner", NoCacheStaticFiles(directory=RUNNER_DIR), name="static runner script")
    app.mount("/.assets", NoCacheStaticFiles(directory=VUE_DIR), name="static vue assets")

    if TRUST_PYTHON:
        with open(VUE_PATH) as f:
            vue = f.read()
            # all instances of <script lang="python">...</script>
            for m in re.finditer(r'<script  *lang="python">(.*?)</script>', vue, re.DOTALL):
                exec(m.group(1))

    @app.get("/{filename:path}")
    async def file(filename: str, response: Response):
        return FileResponse(filename, headers=NO_CACHE_HEADERS)

    print("###", VUE_DIR, RUNNER_DIR)

    return app


if __name__ == "__main__":
    exit(cli())

