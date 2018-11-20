# Drucker

[![Build Status](https://travis-ci.com/drucker/drucker.svg?branch=master)](https://travis-ci.com/drucker/drucker)
[![PyPI version](https://badge.fury.io/py/drucker.svg)](https://badge.fury.io/py/drucker)
[![codecov](https://codecov.io/gh/drucker/drucker/branch/master/graph/badge.svg)](https://codecov.io/gh/drucker/drucker "Non-generated packages only")
[![pypi supported versions](https://img.shields.io/pypi/pyversions/drucker.svg)](https://pypi.python.org/pypi/drucker)

Drucker is a framework of serving machine learning module. Drucker makes it easy to serve, manage and integrate your ML models into your existing services. Moreover, Drucker can be used on Kubernetes.

## Parent Project
https://github.com/drucker/drucker-parent

## Components
- [Drucker](https://github.com/drucker/drucker) (here): Serving framework for a machine learning module.
- [Drucker-dashboard](https://github.com/drucker/drucker-dashboard): Management web service for the machine learning models to the drucker service.
- [Drucker-client](https://github.com/drucker/drucker-client): SDK for accessing a drucker service.
- [Drucker-example](https://github.com/drucker/drucker-example): Example of how to use drucker.

## Installation
From source:

```
git clone --recursive https://github.com/drucker/drucker.git
cd drucker
python setup.py install
```

From [PyPi](https://pypi.org/project/drucker/) directly:

```
pip install drucker
```

## Example
Example is available [here](https://github.com/drucker/drucker-example).

### Create settings.yml (Not necessary)
Write your server configurations. The spec details are [here](./template/settings.yml)

### Create app.py
Implement `Drucker` class.

Necessity methods are following.

#### load_model
ML model loading method.

```python
def load_model(self) -> None:
    try:
        self.predictor = joblib.load(self.model_path)
    except Exception as e:
        self.logger.error(str(e))
        self.logger.error(traceback.format_exc())
        self.predictor = None
        if not self.is_first_boot():
            os._exit(-1)
```

If you need to load more than two files to your ML module, you need to create a compressed file which includes the files it requires. You can load the file like the below.

```python
def joblib_load_from_zip(self, zip_name: str, file_name: str):
    with zipfile.ZipFile(zip_name, 'r') as zf:
        with zf.open(file_name, 'r') as zipmodel:
            return joblib.load(io.BufferedReader(io.BytesIO(zipmodel.read())))

def load_model(self) -> None:
    try:
        file_name = 'default.model'
        self.predictor = self.joblib_load_from_zip(self.model_path, file_name)
    except Exception as e:
        self.logger.error(str(e))
        self.logger.error(traceback.format_exc())
        self.predictor = None
        if not self.is_first_boot():
            os._exit(-1)
```

#### predict
Predicting/inferring method.

```python
def predict(self, input: PredictLabel, option: dict = None) -> PredictResult:
    try:
        label_predict = self.predictor.predict(
            np.array([input], dtype='float64')).tolist()
        return PredictResult(label_predict, [1] * len(label_predict), option={})
    except Exception as e:
        self.logger.error(str(e))
        self.logger.error(traceback.format_exc())
        raise e
```

Input/output specs are below.

##### Input format
*V* is the length of feature vector.

|Field |Type |Description |
|:---|:---|:---|
|input <BR>(required) |One of below<BR>- string<BR>- bytes<BR>- string[*V*]<BR>- int[*V*]<BR>- double[*V*] |Input data for inference.<BR>- "Nice weather." for a sentiment analysis.<BR>- PNG file for an image transformation.<BR>- ["a", "b"] for a text summarization.<BR>- [1, 2] for a sales forcast.<BR>- [0.9, 0.1] for mnist data. |
|option |string| Option field. Must be json format. |

The "option" field needs to be a json format. Any style is Ok but we have some reserved fields below.

|Field |Type |Description |
|:---|:---|:---|
|suppress_log_input |bool |True: NOT print the input and output to the log message. <BR>False (default): Print the input and outpu to the log message.

##### Output format
*M* is the number of classes. If your algorithm is a binary classifier, you set *M* to 1. If your algorithm is a multi-class classifier, you set *M* to the number of classes.

|Field |Type |Description |
|:---|:---|:---|
|label<BR>(required) |One of below<BR> -string<BR> -bytes<BR> -string[*M*]<BR> -int[*M*]<BR> -double[*M*] |Result of inference.<BR> -"positive" for a sentiment analysis.<BR> -PNG file for an image transformation.<BR> -["a", "b"] for a multi-class classification.<BR> -[1, 2] for a multi-class classification.<BR> -[0.9, 0.1] for a multi-class classification. |
|score<BR>(required) |One of below<BR> -double<BR> -double[*M*] |Score of result.<BR> -0.98 for a binary classification.<BR> -[0.9, 0.1] for a multi-class classification. |
|option |string |Option field. Must be json format. |

#### evaluate (TODO)
Evaluating method.

This method is under construction.

##### Input format
|Field |Type |Description |
|:---|:---|:---|
|file<BR>(required) |bytes |Data for performance check |

##### Output format
*N* is the number of evaluation data. *M* is the number of classes. If your algorithm is a binary classifier, you set *M* to 1. If your algorithm is a multi-class classifier, you set *M* to the number of classes.

|Field |Type |Description |
|:---|:---|:---|
|num<BR>(required)|int |Number of evaluation data. |
|accuracy<BR>(required) |double |Accuracy. |
|precision<BR>(required) |double[*N*][*M*] |Precision. |
|recall<BR>(required) |double[*N*][*M*] |Recall. |
|fvalue<BR>(required) |double[*N*][*M*] |F1 value. |

### Create server.py
Create a boot script.

```python
from concurrent import futures
import grpc
import time

from drucker import DruckerDashboardServicer, DruckerWorkerServicer
from drucker.logger import JsonSystemLogger, JsonServiceLogger
from drucker.protobuf import drucker_pb2_grpc
from app import MyApp

_ONE_DAY_IN_SECONDS = 60 * 60 * 24


def serve():
    app = MyApp("./settings.yml")
    system_logger = JsonSystemLogger(app.config)
    service_logger = JsonServiceLogger(app.config)
    system_logger.info("Wake-up drucker worker.")

    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))

    drucker_pb2_grpc.add_DruckerDashboardServicer_to_server(
        DruckerDashboardServicer(logger=system_logger, app=app), server)
    drucker_pb2_grpc.add_DruckerWorkerServicer_to_server(
        DruckerWorkerServicer(logger=service_logger, app=app), server)
    server.add_insecure_port("[::]:{0}".format(app.config.SERVICE_PORT))
    server.start()
    try:
        while True:
            time.sleep(_ONE_DAY_IN_SECONDS)
    except KeyboardInterrupt:
        system_logger.info("Shutdown drucker worker.")
        server.stop(0)


if __name__ == '__main__':
    serve()
```

### Create logger (Not necessary)
If you want to use your own format logger, please implement the drucker [logger interface class](./drucker/logger/logger_interface.py).

### Create start.sh
Create a boot script.

```sh
#!/usr/bin/env bash

ECHO_PREFIX="[drucker example]: "

set -e
set -u

echo "$ECHO_PREFIX Start.."

pip install -r requirements.txt
python ./server.py

```

### Run
```
$ sh start.sh
```

### Test
```
$ python -m unittest drucker/test/test_worker_servicer.py
$ python -m unittest drucker/test/test_dashboard_servicer.py
```

## Drucker on Kubernetes
Drucker can be run on Kubernetes and can be managed by Drucker dashboard.

You must read the followings.

1. https://github.com/drucker/drucker-parent/tree/master/docs/Installation.md
1. https://github.com/drucker/drucker-dashboard/README.md
