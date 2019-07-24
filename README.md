
# Requirements

~~~
pip install asyncio
pip install websockets
~~~

Currently requires some "observable collections", with modifications (just local import "from .stuff import Thing".

~~~
git clone https://github.com/fousteris-dim/Python-observable-collections.git observablecollections
patch -d observablecollections/ < 0001-Local-imports.patch
~~~

And for some better styling of some examples you might want to download picnicss.

~~~
wget https://raw.githubusercontent.com/franciscop/picnic/master/picnic.min.css -O lib/picnic.min.css
~~~

# Helper

(bash)
~~~
pvue() { (sleep .5;firefox ${1%.*}.html)& python3 ${1%.*}.py;}

pvue example-1
pvue example-1.
pvue example-1.html
pvue example-1.py
~~~
