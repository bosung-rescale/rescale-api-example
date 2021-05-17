#!/usr/bin/python

import requests
import json
import argparse
import os
import platform

if __name__ == '__main__':

    parser = argparse.ArgumentParser(description='help')

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
        print("usage: list_jobs.py [-h] [--key KEY] [--platform PLATFORM]")
        exit(1)

# System variables for API run
    my_token = 'Token ' + api_key

# List jobs
    list_jobs_url = rescale_platform + '/api/v2/jobs/'

    current_page = 1
    last_page = False

    while (not(last_page)):
        jobs_info = requests.get(
            list_jobs_url,
            params = {'page' : current_page},
            headers = {'Authorization': my_token}
        )
        jobs_info_dict = json.loads(jobs_info.text)

#        json = json.dumps(jobs_info_dict, indent=2, separators=(',',': '))
#        print(json)

        for label in jobs_info_dict['results'] :
             print(' ')
             print('Job ID : '+ label['id'].strip())
             print('  name : '+ label['name'].strip())
             print('  analysisNames : ', label['analysisNames'])
             print('  jobStatus : ',label['jobStatus']['content'])

        current_page += 1

        if (jobs_info_dict['next'] == None):
            last_page = True
