#!/bin/bash
cfy deployment create --skip-plugins-validation vb-1 -b virtual-branch -i ../inputs/vb-1-input.txt
cfy executions start -d vb-1 install
