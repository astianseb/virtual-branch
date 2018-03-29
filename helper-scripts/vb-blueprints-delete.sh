#!/bin/bash
cfy blueprints delete -b virtual-branch ../virtual-branch.yaml
cfy blueprints delete -b branch-rtr-baseline ../branch-rtr-baseline.yaml
cfy blueprints delete -b branch-vpn-service ../branch-vpn-service.yaml
cfy blueprints delete -b branch-fw-baseline ../branch-fw-baseline.yaml
cfy blueprints delete -b branch-fw-portforward ../branch-fw-portforward-service.yaml
cfy blueprints delete -b branch-webapplication ../branch-webapplication.yaml
