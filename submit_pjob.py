#!/usr/bin/python

import requests
import json
import sys
import argparse
import time
import os
import platform
import signal

def hps_info(api_key, hps_id, rescale_platform):
    my_token = 'Token ' + api_key

# Job Info 
    hps_info_url = rescale_platform + '/api/v2/storage-devices/'+hps_id+'/statuses'

    hps_info = requests.get(
        hps_info_url,
        headers = {'Authorization': my_token}
    )

    if (hps_info.status_code != 200) :
        print('There is no HPS storage '+hps_id)
        sys.exit(1)

    hps_info_dict = json.loads(hps_info.text)
    hps_status = (hps_info_dict['results'][0]['status'])

    if (hps_status != 'Started') :
        print('HPS storage '+ hps_id + ' is not active')
        sys.exit(1)

    return hps_info.status_code, hps_status

if __name__ == '__main__':

    rescale_platform = None
    job_id = None
    my_token = None

    parser = argparse.ArgumentParser(description='help')

    parser.add_argument('--input', '-i', required=True, help='Job setup file')
    parser.add_argument('--key', '-k', required=False, help='API key')
    parser.add_argument('--platform', '-p', required=False, help='Platform address')

    args = parser.parse_args()
    job_setup_filename = args.input
    api_key = ''
    rescale_platform = '' 

    if (platform.system() == 'Windows' ):
        apiconfig_file = os.environ['USERPROFILE']+"\\.config\\rescale\\apiconfig"
    else:
        apiconfig_file = os.environ['HOME']+"/.config/rescale/apiconfig"

    if (os.path.isfile(apiconfig_file)):
        f = open(apiconfig_file, 'r')
        lines = f.readlines()
        f.close()

        rescale_platform = lines[1].split('=')[1].rstrip('\n').lstrip().replace("'","")
        api_key = lines[2].split('=')[1].rstrip('\n').lstrip().replace("'","")

    if (args.key != None):
        api_key = args.key
    if (args.platform != None):
        rescale_platform = args.platform

# Read user input variables for Job
    try:
        f = open(job_setup_filename,'r')
        lines = f.readlines()
        f.close()
    except FileNotFoundError as e:
        print (e)
        sys.exit(1) 

    hps_id = lines[0].split('=')[1].rstrip('\n').lstrip().replace("'","")
    input_file = lines[1].split('=')[1].rstrip('\n').lstrip().replace("'","")
    code_name = lines[2].split('=')[1].rstrip('\n').lstrip().replace("'","")
    version_code = lines[3].split('=')[1].rstrip('\n').lstrip().replace("'","")
    license_file = lines[4].split('=')[1].rstrip('\n').lstrip().replace("'","")
    license_info = lines[5].split('=')[1].rstrip('\n').lstrip().replace("'","")
    coretype_name = lines[6].split('=')[1].rstrip('\n').lstrip().replace("'","")
    core_per_slot = lines[7].split('=')[1].rstrip('\n').lstrip().replace("'","")
    price_option = lines[8].split('=')[1].rstrip('\n').lstrip().replace("'","")
    job_name = lines[9].split('=')[1].rstrip('\n').lstrip().replace("'","")
    job_command = lines[10].split('=')[1].rstrip('\n').lstrip().replace("'","")

    print('Job Information')
    print('')
    print('#PLATFORM_ADDRESS : ' + rescale_platform)
    print('#HPS_ID : ' + hps_id)
    print('#INPUT_FILE_NAME : ' + input_file)
    print('#ANALYSIS_SOFTWARE : ' + code_name)
    print('#ANALYSIS_SOFTWARE_VERSION : ' + version_code)
    print('#LICENSE_FILE : ' + license_file)
    print('#LICENSE_INFO : ' + license_info)
    print('#CORETYPE : ' + coretype_name)
    print('#NUM_OF_CORES : ' + core_per_slot)
    print('#CORE_PRICE_OPTION : ' + price_option) 
    print('#JOB_NAME : ' + job_name)
    print('#JOB_COMMAND : ' + job_command)
    print('#EOF : ' + lines[11].split(' ')[0].rstrip('\n'))

    print('')

    if (lines[11].split(' ')[0].rstrip('\n') != '#EOF'):
        print (job_setup_filename + ' has incorrect format')
        sys.exit(1)

    slot = 1

# System variables for API run
    my_token = 'Token ' + api_key

# Input File upload
    upload_url = rescale_platform + '/api/v2/files/contents/'

    input_files = input_file.split()
    inputfile_id = {}
    inputfiles_list = []

    for i in range(len(input_files)) :
        try:
            upload_file = requests.post(
                upload_url,
                headers={'Authorization' : my_token},
                    files={'file': open(input_files[i], 'rb')}
            )

            if (upload_file.status_code == 201) :
                print('Input file ' + input_files[i] + ' uploaded')
                upload_file_dict = json.loads(upload_file.text)
                inputfile_id[i] = upload_file_dict['id']
                inputfiles_list.append({'id':inputfile_id[i]})
            else:
                print('Input file ' + input_files[i] + ' upload failed')
                exit(1)

        except FileNotFoundError as e:
            print (e)
            exit(1)

#    json = json.dumps(upload_file_dict, indent=2, separators=(',',': '))
#    print(json)

# Analysis software check 
    analyses_url = rescale_platform + '/api/v2/analyses/'

    current_page = 1
    last_page = False
    code_name_check = False
    version_code_check = False

#    json = json.dumps(software_info_dict, indent=2, separators=(',',': '))
#    print(json)

    while (not(last_page)):
        software_info = requests.get(
            analyses_url,
            params = {'page' : current_page},
            headers = {'Authorization': my_token}
        )
        software_info_dict = json.loads(software_info.text)

        for label in software_info_dict['results'] :
            if label['code'].strip() == code_name:
               code_name_check = True
            for label_version in label['versions'] :
               if label_version['versionCode'].strip() == version_code:
                   version_code_check = True

        current_page += 1

        if (code_name_check and version_code_check) :
            print (code_name + ' ' + version_code + ' is used for analysis')
            break

        if (software_info_dict['next'] == None):
            last_page = True

    if (code_name_check and version_code_check) == False :
        print (code_name + ' or ' + version_code + ' is not supported. check the analysis software')
        sys.exit(1)

# Core check
    coretypes_url = rescale_platform + '/api/v2/coretypes/'
    current_page = 1
    coretype_check = False
    last_page = False

    while (not(last_page)):
        core_info = requests.get(
            coretypes_url,
            params = {'page' : current_page},
            headers = {'Authorization': my_token}
        )
        core_info_dict = json.loads(core_info.text)

        for label in core_info_dict['results'] :
            if label['name'].strip().lower() == coretype_name.lower() :
                coretype_code = label['code'].strip()
                coretype_check = True
                
        current_page += 1

        if (coretype_check == True) :
            print (coretype_name + ' is used for analysis')
            break

        if (core_info_dict['next'] == None):
            last_page = True

    if (coretype_check == False) :
        print (coretype_name + ' is not supported. check the core type name')
        sys.exit(1)

# Job setup
    job_url = rescale_platform + '/api/v2/jobs/'
    
    if price_option == 'on-demand-pro':
        low_priority = False
    else:
        low_priority = True

    job_setup = requests.post(
        job_url,
        json = {
            'isLowPriority' : low_priority,
            'name' : job_name,
            'jobanalyses' : [
                {
                    'envVars' : {
                        license_file : license_info
                    },
                    'useMPI' : False,
                    'command' : job_command,
                    'analysis' : {
                        'code' : code_name,
                        'version' : version_code
                    },
                    'hardware' : {
                        'coresPerSlot' : core_per_slot,
                        'slots' : slot,
                        'coreType' : coretype_code,
                    },
                    'inputFiles' : inputfiles_list
                }
            ]
        },
        headers={'Content-Type' : 'application/json',
                 'Authorization' : my_token}
    )

    if (job_setup.status_code != 201) :
        print (job_setup.text)
        print ('Job creation failed')
        sys.exit(1)

    job_setup_dict = json.loads(job_setup.text)
    job_id = job_setup_dict['id'].strip()

#    print(json.dumps(job_setup_dict, indent=2, separators=(',',': ')))

# Attach HPS
    if (hps_id != '') :
        hps_info_status_code, hps_status = hps_info(api_key, hps_id, rescale_platform)
        
        attach_storage_url = rescale_platform + '/api/v2/jobs/' + job_id + '/storage-devices/'
        attach_storage =  requests.post(
            attach_storage_url,
            headers={'Content-Type' : 'application/json',
                     'Authorization' : my_token},
            json={
                'storageDevice': { 'id': hps_id }
            }
        )
        print('HPS storage '+ hps_id + ' is attached')

# Submit Job
    job_submit_url = rescale_platform + '/api/v2/jobs/' + job_id + '/submit/'
    submit_job = requests.post(
        job_submit_url,
        headers={'Authorization': my_token} 
    )
    if (submit_job.status_code == 200) :
        print ('Job ' + job_id + ' : submitted')
    else:
        print ('Job submission failed', submit_job.status_code)
