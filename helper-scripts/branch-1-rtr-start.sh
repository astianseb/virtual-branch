#!/bin/bash
#cfy blueprint upload -b branch-baseline ./branch-baseline.yaml
#cfy deployment create --skip-plugins-validation branch-1 -b branch-baseline -i branch-1-input.txt
#cfy executions start -d branch-1 install
cfy install -d branch-1-rtr -b branch-rtr-baseline -i branch-1-rtr-input.txt ../branch-rtr-baseline.yaml
