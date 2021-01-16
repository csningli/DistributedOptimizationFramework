#! /bin/bash

CONENV="disto"

CONCON=$(which conda)
CONBIN=${CONCON%/*}
CONPATH=${CONBIN%/*}

OUT=$(conda --version)
VER=${OUT#*\ }
PRI_SEC=${VER%\.*}
PRI=${PRI_SEC%%\.*}
SEC=${PRI_SEC##*\.}

if [ $PRI -lt 5 ] && [ $SEC -lt 4 ]
then
  source activate $CONENV
else
  source $CONPATH"/etc/profile.d/conda.sh"
  conda deactivate
  conda activate $CONENV
fi

export PYTHONPATH="C:\\cygwin64\\"`pwd`

if [ $# -gt 0 ]
then
  python $1.py $2 $3
else
  for file in "tests/test_"*".py"
  do
    python $file 
  done
fi
