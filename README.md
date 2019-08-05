
Vuejs-python brings the concepts of vuejs to Python.
You can write your model/data as a Python object and your HTML UI/view with the very convenient vuejs syntax.
As soon as part of your model changes, all dependent variables are updated and the HTML UI is automatically refreshed.

The goal is to use not only Python the language but Python the platform (with numpy, system APIs, and other "native" things).

## Installation

~~~
pip install vuejspython
~~~

## Tiny Example

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


## Similar projects?

If you're interested only in using Python the language with Vue.js, you can try [brython](http://brython.info/) and the [brython vue demo](http://brython.info/gallery/test_vue.html)

There are projects that try to help integrating Vue.js with different Python web frameworks. The goal is different: Vuejs-python makes python and vue tightly integrated, in a common, reactive model.

----
<!-- the line above delimits the end of pypi long_description -->

(to be updated)

## Requirements

~~~ bash
pip install asyncio
pip install websockets
~~~

Currently requires some "observable collections", with modifications (just local import "from .stuff import Thing".

~~~ bash
git clone https://github.com/fousteris-dim/Python-observable-collections.git observablecollections
patch -d observablecollections/ < 0001-Local-imports.patch
~~~

And for some better styling of some examples you might want to download picnicss.

~~~
wget https://raw.githubusercontent.com/franciscop/picnic/master/picnic.min.css -O lib/picnic.min.css
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

- test (in venv) and set proper dependencies in the pip installable module
- see why example-8 is slow with the python-only server
- test atomic in components
- make it an all-components (no too-special ROOT', with also js that tells what class and  package/file (import everything manually in a main.py if not easy)  is the root -> this way we can run a single python and have multiple demos
- have a clean solution for the observable collections (integrate and clean minimal code or find another lib)
