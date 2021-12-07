#!/bin/env python

# openssl pkcs8 -in ~/.globus/userkey.pem -out ~/.globus/userkey_pkcs8.pem

import os, sys
sys.path.append('/afs/cern.ch/cms/PPD/PdmV/tools/McM/')
from urllib2 import Request, urlopen
from rest import McM

from optparse import OptionParser

def setup():
    
    os.system('cern-get-sso-cookie --url https://cms-pdmv-dev.cern.ch/mcm/ -o dev-cookie.txt')
    os.system('cern-get-sso-cookie --url https://cms-pdmv.cern.ch/mcm/ -o prod-cookie.txt')
    os.system('rm -rf ~/private/prod-cookie.txt')
    os.system('rm -rf ~/private/dev-cookie.txt')
    os.system('mv prod-cookie.txt ~/private/.')
    os.system('mv dev-cookie.txt ~/private/.')

def main(argv = None):
    
    if argv == None:
        argv = sys.argv[1:]
        
    usage = "usage: %prog [options]\n Change priority of McM requests starting from tickets"

    parser = OptionParser(usage)
    
    parser.add_option("--tickets", type=str, default="HIG-2021Feb17-00003", help="List of tickets [default: %default]")
    parser.add_option("--block", type=int, default=2, help="Block id [default: %default]")
    parser.add_option("--requests", type=str, default="", help="List of requests [default: %default]")

    (options, args) = parser.parse_args(sys.argv[1:])
    
    return options

if __name__ == '__main__':
        
    options = main()
    
    setup()
        
    mcm = McM(dev=False)
    
    cert = '--key ~/.globus/userkey_pkcs8.pem --cert ~/.globus/usercert.pem'

    ts = options.tickets.split(',')
    rs = options.requests.split(',')
    
    blockId = options.block
        
    prio = -1
    if blockId == 0: prio = 130000
    elif blockId == 1: prio = 110000
    elif blockId == 2: prio = 90000
    elif blockId == 3: prio = 85000
    elif blockId == 4: prio = 80000
    elif blockId == 5: prio = 70000
    elif blockId == 6: prio = 63000
    else: prio = blockId # custom

    if options.requests != '': data = ['']
    else: data = ts
    
    for t in data:
        if options.requests == '':
            print 'Ticket: ' + '\033[34m' + t + '\033[m'
            res = mcm.get('mccms', query='prepid='+t)
            reqs = res[0]['requests']                    
            if len(reqs[0]) == 2:
                id1 = reqs[0][0].split('-')[-1]
                id2 = reqs[0][1].split('-')[-1]
                name = reqs[0][0].split(id1)[0]
                reqs = []
                id1, id2 = int(id1), int(id2)
                for ir in range(id1, id2+1):
                    reqs.append(name+str(str(ir).zfill(5)))
        else: reqs = rs
        for r in reqs:

            requests = mcm.get('requests', query='prepid='+r)
            
            if len(requests) == 1:
                request = requests[0]
                reqmgr_name = request['reqmgr_name']
                if len(reqmgr_name) == 0:
                    print 'Request does not have a registered workflow, please change the corresponding block priority for:', r
                    continue
                else:
                    print r, request['priority']
#                    result = mcm._McM__post('restapi/requests/priority_change', [{'prepid': request['prepid'], 'priority_raw': prio}])
#                    print(result)
                    result = os.system("wmpriority.py "+cert+" %s %s" % (request['reqmgr_name'][-1]['name'], prio))
                    if result != 0:
                        print('Change of priority failed for: %s. Exit code: %s' % (request['prepid'], result))
            else:
                print '\033[31m' + '>>> Please change the priority manually for ' + r + '\033[m'
