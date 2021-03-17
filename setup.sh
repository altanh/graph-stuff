#!/bin/bash

# just a setup script for if I ever need to reinit my environment
conda create -n graphs -c conda-forge graph-tool
conda activate graphs

pip install pylint
pip install black
pip install python-sat
