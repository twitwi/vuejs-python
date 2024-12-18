
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


You can run the bundled tools using their `:` prefixed names instead of the vue file, for instance:

~~~
vjspy :create-demo-files demo
vjspy :view-file demo/file1.txt
vjspy :edit-file demo/file1.txt
vjspy --trust-python :file-rotator demo/file*.txt
vjspy :exam-toggle demo/exam/*
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

- [ ] Allow --online to get latest libs from cdn
- [ ] Allow --open-browser to open the file
- [ ] Allow a random port
- [ ] Update build system...
- [ ] Allow --allow-all-files
- [ ] Nicer not-all-recursive listing... for perfs
- [ ] Also add watcher option (need websockets probably)
- [ ] example: exam, diff does not update/clear on save

