import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read().split('----')[0]

setuptools.setup(
    name="vuejspython",
    version="1.0.0",
    author="Rémi Emonet",
    author_email="remi+242-e2f8@heeere.com",
    description="Vuejs runner, with filesystem, and allowing python extension (e.g., to leverage numpy)",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/twitwi/vuejs-python/",
    install_requires=['fastapi', 'uvicorn'],
    packages=setuptools.find_packages(),
    package_data={
        #'vuejspython': ['builtin/*.vue', 'builtin/*.js']
    },
    entry_points = {
        'console_scripts': [
            'vjspy = vuejspython.run:cli',                  
        ],              
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)
