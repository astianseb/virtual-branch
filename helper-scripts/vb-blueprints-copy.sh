#!/bin/bash
cfy blueprints upload -b virtual-branch ../virtual-branch.yaml
cfy blueprints upload -b branch-rtr-baseline ../branch-rtr-baseline.yaml
cfy blueprints upload -b branch-vpn-service ../branch-vpn-service.yaml
cfy blueprints upload -b branch-fw-baseline ../branch-fw-baseline.yaml
cfy blueprints upload -b branch-fw-portforward ../branch-fw-portforward-service.yaml
cfy blueprints upload -b branch-webapplication ../branch-webapplication.yaml
