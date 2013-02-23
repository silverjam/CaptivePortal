DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd $DIR

PYTHONPATH=$DIR/..:$PYTHONPATH
export PYTHONPATH

echo PYTHONPATH=$PYTHONPATH

nosetests .
