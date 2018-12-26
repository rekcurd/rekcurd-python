# Rekcurd

[![Build Status](https://travis-ci.com/rekcurd/drucker.svg?branch=master)](https://travis-ci.com/rekcurd/drucker)
[![PyPI version](https://badge.fury.io/py/rekcurd.svg)](https://badge.fury.io/py/rekcurd)
[![codecov](https://codecov.io/gh/rekcurd/drucker/branch/master/graph/badge.svg)](https://codecov.io/gh/rekcurd/drucker "Non-generated packages only")
[![pypi supported versions](https://img.shields.io/pypi/pyversions/rekcurd.svg)](https://pypi.python.org/pypi/rekcurd)

Rekcurd is the Project for serving ML module. This is a gRPC micro-framework and it can be used like [Flask](http://flask.pocoo.org/). 


## Parent Project
https://github.com/rekcurd/drucker-parent


## Components
- [Rekcurd](https://github.com/rekcurd/drucker) (here): Project for serving ML module.
- [Rekcurd-dashboard](https://github.com/rekcurd/drucker-dashboard): Project for managing ML model and deploying ML module.
- [Rekcurd-client](https://github.com/rekcurd/drucker-client): Project for integrating ML module. 


## Installation
From source:

```bash
$ git clone --recursive https://github.com/rekcurd/drucker.git
$ cd drucker
$ python setup.py install
```

From [PyPi](https://pypi.org/project/rekcurd/) directly:

```bash
$ pip install rekcurd
```

## How to use
Example code is available [here](https://github.com/rekcurd/drucker-example).


## Unittest
```
$ python -m unittest
```

## Kubernetes support
Rekcurd can be run on Kubernetes. See [here](https://github.com/rekcurd/drucker-parent).
