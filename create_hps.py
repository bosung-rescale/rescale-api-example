#!/usr/bin/python

import requests
import json
import sys
import os
import argparse
import platform

if __name__ == '__main__':

    parser = argparse.ArgumentParser(description='help')

    parser.add_argument('--key', '-k', required=False, help='API key')
    parser.add_argument('--platform', '-p', required=False, help='Platform address')
    parser.add_argument('--name', '-n', required=True, help='HPS name')
    parser.add_argument('--size', '-s', required=True, help='Size of HPS')
    parser.add_argument('--coretype', '-t', required=False, default='hpc-3', help='HPS coretype, default=hpc-3, hpc-3/emerald')
    parser.add_argument('--ncore', '-nc', required=False, default='1', help='Number of cores, default=1, 1/2/4/8/18')
    parser.add_argument('--walltime', '-wt', required=False, default='750', help='HPS walltime (hours), default=750 hours')
    parser.add_argument('--walert', '-wat', required=False, default='36', help='HPS walltime Alert, default=36')
    parser.add_argument('--region', '-r', required=True, help='AWS:ap-northeast-2/us-east-1, Azure:seoul/busan')
    parser.add_argument('--alert1', '-a1', required=False, default='60', help='1st Alert when the disk space reaches the percentage of HPS size, default = 60')
    parser.add_argument('--alert2', '-a2', required=False, default='80', help='2nd Alert when the disk space reaches the percentage of HPS size, default = 80')
    parser.add_argument('--autoextend', '-auto', required=False, default='0', help='HPS size auto increase starts when the disk space reaches the percentage of HPS size, default = 0 : disable auto-extend')

    args = parser.parse_args()
    api_key = None
    rescale_platform = None

    if (platform.system() == 'Windows' ):
        apiconfig_file = os.environ['USERPROFILE']+"\\.config\\rescale\\apiconfig"
    else:
        apiconfig_file = os.environ['HOME']+"/.config/rescale/apiconfig"

    if (os.path.isfile(apiconfig_file)):
        f = open(apiconfig_file, 'r')
        lines = f.readlines()
        f.close()

        rescale_platform =lines[1].split('=')[1].rstrip('\n').lstrip().replace("'","")
        api_key =lines[2].split('=')[1].rstrip('\n').lstrip().replace("'","")

    if (args.key != None):
        api_key = args.key
    if (args.platform != None):
        rescale_platform = args.platform

    if (api_key == None) or (rescale_platform == None) :
        print("usage: create_hps.py [-h] [--key KEY] [--platform PLATFORM] <option>")
        exit(1)

    hps_name = args.name
    hps_size = int(args.size)
    hps_coretype = args.coretype
    hps_corenum = int(args.ncore)
    hps_walltime = int(args.walltime)
    hps_region = args.region
    region = args.region
    hps_firstalert = int(args.alert1)
    hps_secondalert = int(args.alert2)
    hps_autoextendpercent = int(args.autoextend)
    if (hps_autoextendpercent == 0):
        hps_autoextend = False
        hps_autoextendpercent = 1
    else:
        hps_autoextend = True
    hps_walltimealert = int(args.walert)

    my_token = 'Token ' + api_key

    if (hps_region == 'us-east-1'):
        region = "pCTMk" # pCTMk is us-east1
    elif (hps_region =='ap-northeast-2'):
        region = "OLjea" # ap-northeast-2
    elif (hps_region == 'seoul'):
        region = "cHewo"
    elif (hps_region == 'busan'):
        region = "Dwuia"

#    zCTMk : Texas 
#    kaaaa : California

# Job setup
    job_url = rescale_platform + '/api/v2/storage-devices/'
    job_setup = requests.post (
        job_url,
        headers={'Content-Type' : 'application/json',
                 'Authorization' : my_token},

        json = {
            "name": hps_name,
            "storageSize": hps_size,
            "hardware": {
                "walltime": hps_walltime,
                "coresPerSlot": hps_corenum,
                "coreType": hps_coretype
            },
            "firstAlert": hps_firstalert,
            "secondAlert": hps_secondalert,
            "autoextend": hps_autoextend,
            "autoextendPercent": hps_autoextendpercent,
            "walltimeAlert" : True,
            "walltimeAlertHours" : hps_walltimealert,
            "region": {
                "id": region
            },
        }
    )

    if (job_setup.status_code != 201) :
        print ('HPS creation failed')
        print (job_setup.status_code)
        print (job_setup.text)
        exit(1)

    job_setup_dict = json.loads(job_setup.text)
    job_id = job_setup_dict['id'].strip()

#    print(json.dumps(job_setup_dict, indent=2, separators=(',',': ')))

#HPS Creation submit

    submit_url = rescale_platform + '/api/v2/storage-devices/'+job_id+'/submit/'

    submit_hps = requests.post (
       submit_url,
       headers={'Content-Type' : 'application/json',
                'Authorization' : my_token},
    )

    print(submit_hps)

    if (submit_hps.status_code == 200) :
        print ('HPS ' + job_id + ' submitted')
        print ('Number of HPS cores is '+ str(hps_corenum))
        print ('Size of HPS is ' + str(hps_size))
    else:
        print ('HPS ' + job_id + ' submit failed')
        print (submit_hps.status_code)
        exit(1)
