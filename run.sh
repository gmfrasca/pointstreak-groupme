#!/bin/bash

cd {{ HOME_DIRECTORY }}/prod/pointstreak-groupme
python psgroupme/main.py -l /var/logs/psgroupme.prod.log
