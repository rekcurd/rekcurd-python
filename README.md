# Drucker
Drucker is a framework of serving machine learning module. Drucker makes it easy to serve, manage and integrate your ML models into your existing services. Moreover, Drucker can be used on Kubernetes.

## Parent Project
https://github.com/drucker/drucker-parent

## Components
- [Drucker](https://github.com/drucker/drucker) (here): Serving framework for a machine learning module.
- [Drucker-dashboard](https://github.com/drucker/drucker-dashboard): Management web service for the machine learning models to the drucker service.
- [Drucker-client](https://github.com/drucker/drucker-client): SDK for accessing a drucker service.
- [Drucker-example](https://github.com/drucker/drucker-example): Example of how to use drucker.

## Example
Example is available [here](https://github.com/drucker/drucker-example).

## Procedures
### Git Submodule Add
```
$ git submodule add https://github.com/drucker/drucker.git drucker
$ git submodule add https://github.com/drucker/drucker-grpc-proto.git drucker-grpc-proto
$ cp ./drucker/template/settings.yml .
$ cp ./drucker/template/predict.py .
$ cp ./drucker/template/server.py .
$ cp ./drucker/template/start.sh .
```

### When update comes
```
$ git submodule update --recursive
```

Check the files above and if they had updates, merge them to your files.

### Edit settings.yml
```
$ vi settings.yml
```

### Edit predict.py
```
$ vi predict.py
```

Write the following methods.

#### load_model
Loading ML model to your ML module. This method is called on the wakeup or switch model.

Argument `model_path` is the path of a ML model. You can load the model like this.

```
self.predictor = joblib.load(model_path)
```

We recommend the architecture of "1 Drucker loads 1 file" but sometimes your module needs a several files to load. In that case you need to create a compressed file including the files it requires. `model_path` will be your compressed file and you decompress it by yourself.

#### predict
Predicting or inferencing from the input. The definitions of input or output are described below. `bytes` can be a byte data of a file.

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
Evaluating the precision, recall and f1value of your ML model. The definitions of input or output are described below.

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

### Edit server.py
```
$ vi server.py
```

Since `drucker_pb2_grpc` is automatically generated from `drucker.proto`, you don't need to care about it. You need to implement the interface class of `SystemLoggerInterface` and `ServiceLoggerInterface` if you customize the log output.

### Edit start.sh
```
$ vi start.sh
```

Write the necessity script to boot your Drucker service. Minimum requirement is below.

```
pip install -r ./drucker-grpc-proto/requirements.txt
sh ./drucker-grpc-proto/run_codegen.sh

python server.py
```

### Run it!
```
$ sh start.sh
```

## Drucker on Kubernetes
Drucker dashboard makes it easy to launch Drucker service on Kubernetes.

You must read followings.

1. https://github.com/drucker/drucker-parent/tree/master/docs/Installation.md
1. https://github.com/drucker/drucker-dashboard/README.md
