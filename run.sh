#!/bin/bash

basedir=`dirname $0`
cd $basedir
pipenv shell
python -m psgroupme -l ./log/psgroupme.log
