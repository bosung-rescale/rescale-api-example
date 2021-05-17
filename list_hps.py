#!/usr/bin/python

import requests
import json
import sys
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
        print("usage: list_hps.py [-h] [--key KEY] [--platform PLATFORM]")
        exit(1)

    my_token = 'Token ' + api_key

# Endpoint
    storage_info_url = rescale_platform + '/api/v2/storage-devices/'

    current_page = 1
    last_page = False

    while (not(last_page)):
    
        storage_list = requests.get(
            storage_info_url,
            params = {'page': current_page},
            headers = {'Authorization': my_token}
        )
        storage_list_dict = json.loads(storage_list.text)
#        json_obj = json.dumps(storage_list_dict, indent=2, separators=(',',': '))
#        print(json_obj)

        for label in storage_list_dict['results'] :
            
            status_info_url = label['urls']['statuses']
            status_list = requests.get(
                status_info_url,
                headers = {'Authorization': my_token}
            )
            status_list_dict = json.loads(status_list.text)

            print(' hps id :            ', label['id'].strip())
            print('     name :          ', label['name'].strip())
            print('     size(GB) :      ', str(label['storageSize']))
            print('     creation date : ', label['dateInserted'].split('T')[0],label['dateInserted'].split('T')[1].split('.')[0])
            print('     walltime :      ', str(label['hardware']['walltime']))
            print('     status :        ', status_list_dict['results'][0]['status'])
#            print(' owner : '+ label['owner'].strip())
            print(' ')

        current_page +=1

        if (storage_list_dict['next'] == None):
            last_page = True
