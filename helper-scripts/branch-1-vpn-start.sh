#!/bin/bash
#cfy blueprint upload -b branch-vpn-service ./branch-vpn-service.yaml
#cfy deployment create --skip-plugins-validation branch-1-vpn -b branch-vpn-service -i branch-1-vpn-service-input.txt
#cfy executions start -d branch-1-vpn install
cfy install -d branch-1-vpn -b branch-vpn-service -i branch-1-vpn-service-input.txt ../branch-vpn-service.yaml
