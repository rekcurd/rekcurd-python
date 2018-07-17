#!/usr/bin/env bash

ECHO_PREFIX="[drucker example]: "

set -e
set -u

echo "$ECHO_PREFIX Start.."

pip install -r ./drucker-grpc-proto/requirements.txt
python ./drucker-grpc-proto/run_codegen.py

pip install -r ./drucker/requirements.txt

pip install -r requirements.txt
python server.py
