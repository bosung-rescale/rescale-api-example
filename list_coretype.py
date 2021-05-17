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
        print("usage: list_coretype.py [-h] [--key KEY] [--platform PLATFORM]")
        exit(1)

# System variables for API run
    my_token = 'Token ' + api_key

# Core check
    coretypes_url = rescale_platform + '/api/v2/coretypes/'
    current_page = 1
    last_page = False

    while (not(last_page)):
        core_info = requests.get(
            coretypes_url,
            params = {'page' : current_page},
            headers = {'Authorization': my_token}
        )
        core_info_dict = json.loads(core_info.text)
#        print(json.dumps(core_info_dict, indent=2, separators=(',',': ')))

        for label in core_info_dict['results'] :
            print('Coretype name:       ',label['name'].strip())
            print('         spec:       ',label['processorInfo'])
            print('         code:       ',label['code'])
            print('         cores:      ',label['cores'])
            print('         gpuCounts:  ',label['gpuCounts'])
#            print('  io : ', label['io'])
#            print('  requiresTempSshAuth : ', label['requiresTempSshAuth'])
#            print('  features : ', label['features'])
#            print('  remoteVizAllowed : ', label['remoteVizAllowed'])
#            print('  mustBeRequested : ', label['mustBeRequested'])
            print()

        current_page += 1

        if (core_info_dict['next'] == None):
            last_page = True

