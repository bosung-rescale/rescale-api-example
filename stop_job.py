#!/usr/bin/python

import requests
import json
import time
import sys
import argparse
import os
import platform

if __name__ == '__main__':

    parser = argparse.ArgumentParser(description='help')

    parser.add_argument('--id', '-i', required=True, help='Job id')
    parser.add_argument('--key', '-k', required=False, help='API key')
    parser.add_argument('--platform', '-p', required=False, help='Platform address')

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
        print("usage: stop_job.py [-h] --id ID [--key KEY] [--platform PLATFORM]")
        exit(1)

    job_id = args.id
    my_token = 'Token ' + api_key

# Stop Job
    job_stop_url = rescale_platform + '/api/v2/jobs/' + job_id + '/stop/'
    job_status = requests.post(
        job_stop_url,
            headers={'Authorization': my_token} 
    )
  
# Monitoring Job
    job_status_url = rescale_platform + '/api/v2/jobs/' + job_id + '/statuses/'

    prev_status = None
    current_status = None
    job_completed = False

    while job_completed == False :
        prev_status = current_status
        job_status = requests.get(
            job_status_url,
            headers={'Authorization': my_token} 
        )
        job_status_dict = json.loads(job_status.text)
        current_status = job_status_dict['results'][0]['status']

        if current_status != prev_status :
            print ('Current status of Job ' + job_id + ' : ' + current_status)

        if current_status == 'Completed' : 
            job_completed = True

        time.sleep(5)   
