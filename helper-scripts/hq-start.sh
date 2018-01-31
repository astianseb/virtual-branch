#!/bin/bash
#cfy blueprint upload -b hq-baseline ./hq-baseline.yaml
#cfy deployment create --skip-plugins-validation hq -b hq-baseline
#cfy executions start -d hq install
cfy install -d hq -b hq-baseline ../hq-baseline.yaml
