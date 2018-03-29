#!/bin/bash
cfy deployment create --skip-plugins-validation vb-2 -b virtual-branch -i ../inputs/vb-2-input.txt
cfy executions start -d vb-2 install
