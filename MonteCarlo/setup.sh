#!/bin/bash

voms-proxy-init --voms cms -valid 192:00

export PYTHONPATH=/afs/cern.ch/cms/PPD/PdmV/tools/wmcontrol:${PYTHONPATH}
export PATH=/afs/cern.ch/cms/PPD/PdmV/tools/wmcontrol:${PATH}
source /afs/cern.ch/cms/PPD/PdmV/tools/wmclient/current/etc/wmclient.sh
