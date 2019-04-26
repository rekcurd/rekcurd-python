# Rekcurd

[![Build Status](https://travis-ci.com/rekcurd/rekcurd-python.svg?branch=master)](https://travis-ci.com/rekcurd/rekcurd-python)
[![PyPI version](https://badge.fury.io/py/rekcurd.svg)](https://badge.fury.io/py/rekcurd)
[![codecov](https://codecov.io/gh/rekcurd/rekcurd-python/branch/master/graph/badge.svg)](https://codecov.io/gh/rekcurd/rekcurd-python "Non-generated packages only")
[![pypi supported versions](https://img.shields.io/pypi/pyversions/rekcurd.svg)](https://pypi.python.org/pypi/rekcurd)

Rekcurd is the Project for serving ML module. This is a gRPC micro-framework and it can be used like [Django](https://docs.djangoproject.com/) and [Flask](http://flask.pocoo.org/).


## Parent Project
https://github.com/rekcurd/community


## Components
- [Rekcurd](https://github.com/rekcurd/rekcurd-python): Project for serving ML module.
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
Example is available [here](https://github.com/rekcurd/rekcurd-example/tree/master/python/sklearn-digits). You can generate Rekcurd template and implement necessary methods.

```bash
$ rekcurd startapp {Your application name}
$ cd {Your application name}
$ vi app.py
$ python app.py
```


## Unittest
```
$ python -m unittest
```


## Kubernetes support
Rekcurd can be run on Kubernetes. See [community repository](https://github.com/rekcurd/community).


## Type definition
### `PredictLabel` type
*V* is the length of feature vector.

|Field |Type |Description |
|:---|:---|:---|
|input <BR>(required) |One of below<BR>- string<BR>- bytes<BR>- string[*V*]<BR>- int[*V*]<BR>- double[*V*] |Input data for inference.<BR>- "Nice weather." for a sentiment analysis.<BR>- PNG file for an image transformation.<BR>- ["a", "b"] for a text summarization.<BR>- [1, 2] for a sales forcast.<BR>- [0.9, 0.1] for mnist data. |
|option |string| Option field. Must be json format. |

The "option" field needs to be a json format. Any style is Ok but we have some reserved fields below.

|Field |Type |Description |
|:---|:---|:---|
|suppress_log_input |bool |True: NOT print the input and output to the log message. <BR>False (default): Print the input and outpu to the log message. |
|YOUR KEY |any |YOUR VALUE |

### `PredictResult` type
*M* is the number of classes. If your algorithm is a binary classifier, you set *M* to 1. If your algorithm is a multi-class classifier, you set *M* to the number of classes.

|Field |Type |Description |
|:---|:---|:---|
|label<BR>(required) |One of below<BR> -string<BR> -bytes<BR> -string[*M*]<BR> -int[*M*]<BR> -double[*M*] |Result of inference.<BR> -"positive" for a sentiment analysis.<BR> -PNG file for an image transformation.<BR> -["a", "b"] for a multi-class classification.<BR> -[1, 2] for a multi-class classification.<BR> -[0.9, 0.1] for a multi-class classification. |
|score<BR>(required) |One of below<BR> -double<BR> -double[*M*] |Score of result.<BR> -0.98 for a binary classification.<BR> -[0.9, 0.1] for a multi-class classification. |
|option |string |Option field. Must be json format. |

### `EvaluateResult` type
`EvaluateResult` is the evaluation score. *N* is the number of evaluation data. *M* is the number of classes. If your algorithm is a binary classifier, you set *M* to 1. If your algorithm is a multi-class classifier, you set *M* to the number of classes.

|Field |Type |Description |
|:---|:---|:---|
|num<BR>(required)|int |Number of evaluation data. |
|accuracy<BR>(required) |double |Accuracy. |
|precision<BR>(required) |double[*M*] |Precision. |
|recall<BR>(required) |double[*M*] |Recall. |
|fvalue<BR>(required) |double[*M*] |F1 value. |

### `EvaluateDetail` type
`EvaluateDetail` is the details of evaluation result.

|Field |Type |Description |
|:---|:---|:---|
|result<BR>(required) |PredictResult |Prediction result. |
|is_correct<BR>(required) |bool |Correct or not. |
