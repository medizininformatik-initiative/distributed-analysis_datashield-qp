# DS common library
A library with common functionality for poll-queue mechanism.
This library includes different packages which contains mechanisms 

## Prerequisites
You need the following tools to get this to work on you own machine.

- python3
- pip
- twine
- bumpversion

## Packages
There is now one package supported in ds-common.
- http

### HTTP
The http package includes some basic http-methods which are used to setup and serve a http client?

## Building and publishing
Install necessary packages;

```bash
# install necessary packages
pip install bumpversion
pip install twine
```

Building the package and publishing it on the registry includes a series of commands:

```bash
# cleanup workspace
rm -rf dist
rm -rf ds_common.egg-info
```

```bash
# bump the version to 1.0.0 if you are at a 0.x.x range
# create a tag v1.0.0
# create a version commit
bumpversion major setup.py

# push changes to remote
git push origin master
```

Create a PR on Github to bump the version.

```bash
# install the package on you local environment
[sudo] pip install .
```

```bash
# create the distribution to upload to PyPi
python3 setup.py sdist
```

Publish your package to PyPi. First of all you need to install ```twine``` and secondly upload it into PyPi.

```bash
# specify the upload directory or use a wildcard
# login with the credentials for PyPi
twine upload dist/*
```

Use the credentials for the DataSHIELD account.


