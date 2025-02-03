
If you're looking for "Vuejs-python that brings the concepts of vuejs to Python", see our V0 branch (and readme, and V0.* on pypi).

The goal of vuejs-python (starting from V1) is to
- easily run standalone Vue.js components / micro-apps,
- give them access to the working directory,
- allow (unsafe) extensions to be written in Python (including numpy, local resource access, etc)


## Installation

~~~
pip install vuejspython
~~~

## Usage

~~~
vjspy [--trust-python] [--port=...] [--host=...] myfile.vue more arbitrary parameters
~~~


You can run the bundled tools using their `:` prefixed names instead of the vue file.
These files are in https://github.com/twitwi/vuejs-python/tree/main/vuejspython/builtin

Here are some example usage, that can be followed as a tutorial:

~~~
vjspy :create-demo-files demo
vjspy :view-file demo/file1.txt
vjspy :edit-file demo/file1.txt
vjspy --trust-python :rotate-files demo/file*.txt
vjspy :exam-toggle demo/exam/*

# hosting the current folder with a video player
vjspy :video-serve
~~~

## Snippets

### HTML head

To add something in the HTML head (change title, icon, load library, etc):

~~~html
<template>
    <add-in-head>
        <title>View File</title>
        <!-- an SVG icon emoji -->
        <link rel="icon" type="image/svg+xml"
        href="data:image/svg+xml,%3Csvg%20xmlns='http://www.w3.org/2000/svg'%20viewBox='0%200%2016%2016'%3E%3Ctext%20style='filter:hue-rotate(60deg)'%20x='0'%20y='14'%3E👍%3C/text%3E%3C/svg%3E" />
    </add-in-head>
    ...
</template>
~~~

### Accessing Vue

To import elements from the bundled Vue (you can remove `lang="ts"` to use plain js, and setup to use a traditional component writing):

~~~html
<script setup lang="ts">
import { ref, computed } from "#vue"
...
</script>
~~~

### Accessing files

To use the custom filesystem API ([asynchronously](https://developer.mozilla.org/en-US/docs/Learn_web_development/Extensions/Async_JS/Promises)):

~~~javascript
<script...
const { fs } = window.VueRunner

const content = await fs.readFile('path/to/file')

await fs.writeFile('path/to/file', 'hello content')

await fs.deleteFile('path/to/file')

const allFilesRecursively = (await fs.listFiles()).files
~~~

It allows only access to files in the folder where the program has been started (Warning: with `--trust-python`, this limitation can be worked around easily).

### Accessing command line parameters

~~~javascript
<script...
const { args } = window.VueRunner
// NB: starts at index 0, no parameters ⇒ args==[]
alert(JSON.stringify(args))
</script>
~~~


### Adding Python code

This requires the program to be launched with `--trust-python`.
You can add python code in a script element and FastAPI:

~~~javascript
<script...
alert(await((await fetch('/.path')).text()))
</script>

<script lang="python">
@app.get("/.path")
def get_path():
    import sys
    return sys.path
</script>
~~~

See also the [rotate-files example](https://github.com/twitwi/vuejs-python/tree/main/vuejspython/builtin/rotate-files.vue) that uses command line arguments (in python) too.


### Handling url hash

~~~javascript
<script...
const { onHash, setHash } = window.VueRunner

onHash((h) => {
    // also triggers on first load (with empty hash or the hash from the initial URL)
    if (h !== '') {
        alert('you changed the address to '+h)
    }
})

function showAbout() {
    ...
    setHash('about')
}
setTimeout(showAbout, 1000)

</script>
~~~



----
<!-- the line above delimits the end of pypi long_description -->



## Pypi stuff

(in a clean clone, to be sure that not too much thing are copied)

~~~
python3 -m pip install --upgrade setuptools wheel
python3 -m pip install --upgrade twine


# update the version number in setup.py and then
./update-static.sh
rm -rf dist/
python3 setup.py sdist bdist_wheel
python3 -m twine upload --repository-url https://test.pypi.org/legacy/ dist/*
# OR: python3 -m twine upload dist/*

python3 -m pip install --index-url https://test.pypi.org/simple/ --no-deps vuejspython

pip uninstall vuejspython

python3 -m pip install  .. ; ll $VENV/lib/python3.6/site-packages/vuejspython
~~~



## TODO


- [ ] maybe integrate zod?
- [ ] doc that some thing are bunlded or with e.g. /.runner/builtin/diff.min.js ... consider e.g. #diff in addition for these... yes, like the #fsapi (which is built-in too)
- [ ] example: exam, diff does not update/clear on save
- [ ] Allow --online to get latest libs from cdn
- [ ] Allow --open-browser to open the file
- [ ] Allow opening an existing instance if the port is taken (already running)
- [ ] Allow a random port
- [ ] Warn if some python but no --trust-python (and neither --no-pyton)
- [ ] Allow some config section, e.g. with prefered port etc
- [ ] Update build system... python setup.py is deprecated
- [ ] When trust-python, expose an api to run shell commands too (maybe proto in trailtools)
- [ ] consider integration of .quit (from trailtools logdown / sport)

BETTER FS API

- [ ] Allow --allow-all-files
- [ ] Nicer not-all-recursive listing... for perfs
- [ ] Also add watcher option (need websockets probably, or add a polling e.g. /.changed)
- [ ] consider use as vite-based projects too? and/or a version that hosts a build page but allows the fs api etc? and/or an fsapi that works similarly but in vite? see https://github.com/StarLederer/vite-plugin-fs (for inspiration or direct use) or 4y https://github.com/antfu/vite-fs

