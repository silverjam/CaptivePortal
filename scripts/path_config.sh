#!/bin/bash

DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

PATH=$DIR:$PATH
echo PATH=$PATH
export PATH

PYTHONPATH=$DIR/..:$PYTHONPATH
echo PYTHONPATH=$PYTHONPATH
export PYTHONPATH
