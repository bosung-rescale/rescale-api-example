#!/usr/bin/python

import requests
import json
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
        print("usage: job_files.py [-h] --id ID [--key KEY] [--platform PLATFORM]")
        exit(1)

    job_id = args.id
    my_token = 'Token ' + api_key

# Job File List 
    list_output_files_url = rescale_platform + '/api/v2/jobs/' + job_id + '/files/'

    current_page = 1
    file_count = 0
    last_page = False

    while (not(last_page)):
        list_output_files = requests.get(
            list_output_files_url,
            params = {'page' : current_page},
            headers = {'Authorization': my_token}
        )
        list_output_files_dict = json.loads(list_output_files.text)

        for label in list_output_files_dict['results'] :
            #print(label['path'].split('/')[-1])
            print(label['path'])

        current_page += 1
        if (list_output_files_dict['next'] == None):
            last_page = True

    #json = json.dumps(list_output_files_dict, indent=2, separators=(',',': '))
    #print(json)

