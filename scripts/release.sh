#!/usr/bin/env bash

echo 'git clean -xdf'
echo 'python setup.py sdist'
echo 'python setup.py bdist_wheel --universal'
echo 'twine upload dist/* -r https://upload.pypi.org/legacy/ -u drucker'
