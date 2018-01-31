#!/bin/bash
#cfy blueprint upload -b branch-fw-baseline ./branch-fw-baseline.yaml
#cfy deployment create --skip-plugins-validation branch-1-fw -b branch-fw-baseline -i branch-1-fw-input.txt
#cfy executions start -d branch-1-fw install
cfy install -d branch-1-fw -b branch-fw-baseline -i branch-1-fw-input.txt ../branch-fw-baseline.yaml
