
# Requirements

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

# Helpers

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


# TODO

- make components working (more than a single top level one, or make it easy to pass linked-state to js components)
- have a clean solution for the observable collections (integrate and clean minimal code or find another lib)
