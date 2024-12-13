
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
vjspy my.vue more arbitrary parameters
~~~


You can run the bundled tools using their `:` prefixed names instead of the vue file, for instance:

~~~
vjspy :create-demo-files demo
vjspy :view-file demo/file1.txt
vjspy :edit-file demo/file1.txt
vjspy :file-rotator demo/file1.txt demo/file2.txt
vjspy :exam-toggle demo/exam/*
vjspy --trust-python :view-file ~/.bashrc
~~~


----
<!-- the line above delimits the end of pypi long_description -->



## Pypi stuff

~~~
python3 -m pip install --upgrade setuptools wheel
python3 -m pip install --upgrade twine

# update the version number in setup.py and then
rm -rf dist/
python3 setup.py sdist bdist_wheel
python3 -m twine upload --repository-url https://test.pypi.org/legacy/ dist/*
# OR: python3 -m twine upload dist/*

python3 -m pip install --index-url https://test.pypi.org/simple/ --no-deps vuejspython

pip uninstall vuejspython

python3 -m pip install  .. ; ll $VENV/lib/python3.6/site-packages/vuejspython
~~~

