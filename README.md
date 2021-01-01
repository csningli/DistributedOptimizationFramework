# DistributedOptimizationFramework (Disto)
Disto is a framework in Python for the implementation of the distributed optimization algorithms.

## Conda Environment

    conda env create -f env.yml

## Run A Script

    ./run.sh relative_path_to_script_without_extention_py

To run an example in the directory "examples", call

    ./run.sh examples/directory_of_example/file_name_without_extention_py

For example, the following command runs "examples/SyncBT/main.py".

    ./run.sh examples/SyncBT/main


## Run Test

    ./run.sh tests/test_name_without_extension_py

For example, the following command runs "tests/test_agent.py".

    ./run.sh tests/test_agent

By default, calling "run.sh" without any arguments runs all the tests.

    ./run.sh

## Run on Windows
On Windows, use "run_win.sh" in stead of "run.sh".
