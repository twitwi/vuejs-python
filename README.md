
Vuejs-python brings the concepts of vuejs to Python.
You can write your model/data as a Python object and your HTML UI/view with the very convenient vuejs syntax.
As soon as part of your model changes, all dependent variables are updated and the HTML UI is automatically refreshed.

The goal is to use not only Python the language but Python the platform (with numpy, system APIs, and other "native" things).

## Installation

~~~
pip install vuejspython
~~~

## Tiny Example

You need to create two files: one Python model and an HTML UI.
A good convention (to help tools) is to use the same name, with the `.py` and `.html` extensions, respectively.

<div style="display: flex">
  <div style="flex: 50%;">

  `# example.py`

```python
    ...
    @model
    class App:
      radius = 5
      def computed_area(self):
        return pi * self.radius ** 2

    vuejspython.start(App())
```

  </div>
  <div style="flex: 50%;">

  `# example.html`

```html
    <div id="main">
      Fill the radius in the text field: <input v-model.number="radius"/>.
      (or with <button @click="radius += 1">+1</button> <br/>
      A disk with radius {{ radius }} has an area of {{ area }}.
    </div>
     
    <script src="lib/vuejspython.js"></script>
    <script>vuejspython.start()</script>
```

  </div>
</div>

## Running, option 1: only with Python

~~~bash
python3 example.py

# or a tiny shell function helper
pvue() { (sleep .5;firefox ${1%.*}.html)& python3 ${1%.*}.py;}
pvue example.py
~~~

This will give you an address to which you should append your HTML file name, here `example.html`.
In this example, you will visit <http://localhost:4260/example.html>
(or visit the given address `http://localhost:4260` and click your file).

NB: you need to stop the command with `Ctrl+C` if you want to run another example.


## Running, option 2: with hot reload on file change

Here we will start two processes, one for the HTML part (with live reload, and another only for the Python).

Terminal 1, hosting the HTML files with hot reload:

~~~bash
# one-time install
pip install watchdog
npm install -g simple-hot-reload-server
# in terminal 1 (hot html reload, for all files)
hrs .
~~~
(this gives you the address to open, after appending your file name, e.g., <http://localhost:8082/example.html>)

Terminal 2, running the python server

~~~bash
# in terminal 2 (start or restart python)
NOSERVE=1 python3 example.py
# OR, for live restart
NOSERVE=1 watchmedo auto-restart --patterns="*.py" python3 example.py
~~~
NB: `NOSERVE=1` tells vuejspython to not serve the HTML files (it is handled by `hrs` above)

NB: when changing the .py, a manual browser refresh is still needed, see below for a more complete solution

### Helper for complete live reload (live restart for python)

~~~bash
pvue() { if test "$1" = open ; then shift ; (sleep 1 ; firefox "http://localhost:8082/${1%.*}.html") & fi; watchmedo auto-restart --patterns="*.py" --ignore-patterns="*/.#*.py" bash -- -c '(sleep .250 ; touch '"${1%.*}"'.html) & python3 '"${1%.*}"'.py' ; }
# Then
pvue example
# OR to also open firefox
pvue open example
# OR some convenient variations
NOSERVE=1 pvue open example
pvue open example.
pvue open example.py
pvue open example.html
# it always runs the file with the .py extension
~~~


## Other, different projects

If you're interested only in using Python the language with Vue.js, you can try [brython](http://brython.info/) and the [brython vue demo](http://brython.info/gallery/test_vue.html)

There are projects that try to help integrating Vue.js with different Python web frameworks. The goal is different: Vuejs-python makes python and vue tightly integrated, in a common, reactive model.

----
<!-- the line above delimits the end of pypi long_description -->

## Development

### Requirements

~~~ bash
pip install aiohttp
pip install websockets
~~~

You also need to get a few libraries:

~~~
cd vuejspython
./update-static.sh # or manually download the files
~~~

### Notes

Currently, the project uses requires some "observable collections", with some modifications.
They are included in the package, in `vuejspython/observablecollections`.
They have been obtained with:

~~~ bash
git clone https://github.com/fousteris-dim/Python-observable-collections.git observablecollections
patch -d observablecollections/ < 0001-Local-imports.patch
~~~



## Helpers

### Simply launch python and open a browser (firefox) at the right address.

~~~ bash
# bash function
pvue() { (sleep .5;firefox ${1%.*}.html)& python3 ${1%.*}.py;}

# examples
pvue example-1
pvue example-1.
pvue example-1.html
pvue example-1.py
~~~


### OR, to develop with auto-reload.

~~~ bash
# one-time install
pip install watchdog
npm install -g simple-hot-reload-server


# in terminal 1 (hot html reload, for all files)
hrs .

# in terminal 2 (start and restart python
pvue() { if test "$1" = open ; then shift ; (sleep 1 ; firefox "http://localhost:8082/${1%.*}.html") & fi; watchmedo auto-restart --patterns="*.py" --ignore-patterns="*/.#*.py" bash -- -c '(sleep .250 ; touch '"${1%.*}"'.html) & python3 '"${1%.*}"'.py' ; }
pvue open example-1
pvue example-1
# the first opens firefox initially
~~~


## Pypi stuff

~~~
python3 -m pip install --upgrade setuptools wheel
python3 -m pip install --upgrade twine

rm -rf dist/
python3 setup.py sdist bdist_wheel
python3 -m twine upload --repository-url https://test.pypi.org/legacy/ dist/*

python3 -m pip install --index-url https://test.pypi.org/simple/ --no-deps vuejspython

pip uninstall vuejspython

python3 -m pip install  .. ; ll $VENV/lib/python3.6/site-packages/vuejspython
~~~


## TODO

- see why example-8 is slow with the python-only server
- test atomic in components
- make it an all-components (no too-special ROOT', with also js that tells what class and  package/file (import everything manually in a main.py if not easy)  is the root -> this way we can run a single python and have multiple demos
- have a clean solution for the observable collections (integrate and clean minimal code or find another lib)
