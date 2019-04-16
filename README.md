
# Requirements

~~~
pip install asyncio
pip install websockets
~~~

Currently requires some "observable collections", with modifications (just local import "from .stuff import Thing".

~~~
git clone https://github.com/fousteris-dim/Python-observable-collections.git observablecolections
cd observablecolections
# 0001-Local-imports.patch
~~~

# Helper

(bash)
~~~
pvue() { (sleep .5;firefox ${1%.*}.html)& python3 ${1%.*}.py;}
~~~
