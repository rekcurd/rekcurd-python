# Rekcurd

[![Build Status](https://travis-ci.com/rekcurd/rekcurd-python.svg?branch=master)](https://travis-ci.com/rekcurd/rekcurd-python)
[![PyPI version](https://badge.fury.io/py/rekcurd.svg)](https://badge.fury.io/py/rekcurd)
[![codecov](https://codecov.io/gh/rekcurd/rekcurd-python/branch/master/graph/badge.svg)](https://codecov.io/gh/rekcurd/rekcurd-python "Non-generated packages only")
[![pypi supported versions](https://img.shields.io/pypi/pyversions/rekcurd.svg)](https://pypi.python.org/pypi/rekcurd)

Rekcurd is the Project for serving ML module. This is a gRPC micro-framework and it can be used like [Flask](http://flask.pocoo.org/). 


## Parent Project
https://github.com/rekcurd/community


## Components
- [Rekcurd](https://github.com/rekcurd/rekcurd-python) (here): Project for serving ML module.
- [Rekcurd-dashboard](https://github.com/rekcurd/dashboard): Project for managing ML model and deploying ML module.
- [Rekcurd-client](https://github.com/rekcurd/python-client): Project for integrating ML module. 


## Installation
From source:

```bash
$ git clone --recursive https://github.com/rekcurd/rekcurd-python.git
$ cd rekcurd-python
$ pip install -e .
```

From [PyPi](https://pypi.org/project/rekcurd/) directly:

```bash
$ pip install rekcurd
```

## How to use
Example code is available [here](https://github.com/rekcurd/rekcurd-example/tree/master/python/sklearn-digits). You can generate Rekcurd application template by a following command.

```bash
$ rekcurd startapp {Your application name}
```


## Unittest
```
$ python -m unittest
```

## Kubernetes support
Rekcurd can be run on Kubernetes. See [here](https://github.com/rekcurd/community).
