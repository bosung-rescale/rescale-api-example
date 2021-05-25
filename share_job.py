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
    parser.add_argument('--email', '-e', required=False, default='kr-support@rescale.com', help='e-mail address of sharer')
    parser.add_argument('--message', '-m', required=False, default='Share for support', help='Message for sharing')
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
        print("usage: share_job.py [-h] --id ID --email email@address -- message 'Message for sharing' [--key KEY] [--platform PLATFORM]")
        exit(1)

    job_id = args.id
    email = args.email
    message = args.message

    my_token = 'Token ' + api_key

# Share Job
    job_share_url = rescale_platform + '/api/v2/jobs/' + job_id + '/share/'
    job_share_status = requests.post(
        job_share_url,
        headers={'Authorization': my_token},
        json = {
            'email' : email,
            'message' : message,
        }
    )

    #job_share_status_dict = json.loads(job_share_status.text)
    #print(job_share_status_dict)
