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
    current_dir = os.getcwd()

    list_output_files = requests.get(
        list_output_files_url,
        headers={'Authorization': my_token}
    )   
    list_output_files_dict = json.loads(list_output_files.text)
    uploaded_date = (list_output_files_dict['results'][0]['dateUploaded'].replace(':','-',2)).replace('T','_').split('.',1)[0]
    files_count = list_output_files_dict['count']
    files_size = list_output_files_dict['size']
    #print ('Start to download', files_count, 'files (', files_size, 'MB )' )

    top_dir = uploaded_date + '/'
    if not(os.path.exists(top_dir)) :
        os.makedirs(top_dir)
    os.chdir(top_dir)

    while (not(last_page)):

        list_output_files = requests.get(
            list_output_files_url,
            params = {'page' : current_page},
            headers={'Authorization': my_token}
        )
        list_output_files_dict = json.loads(list_output_files.text)

        for label in list_output_files_dict['results'] :
            file_count += 1
        
            #run_path = label['pathParts']['path'].split('/',4)[4].rsplit('/',1)[0]
            #path = uploaded_date+'/'+run_path
            
            relative_path = label['relativePath'].rsplit('/',1)[0]

            if relative_path != label['relativePath'] :
                if not(os.path.exists(top_dir+relative_path)) :
                    os.makedirs(top_dir+relative_path)
                os.chdir(top_dir+relative_path)

            downloadUrl = label['downloadUrl']
            filename = os.path.basename(label['relativePath'])

            response = requests.get(
                downloadUrl,
                headers={'Authorization': my_token}
            )
            with open(filename, 'wb') as fd:
                for chunk in response.iter_content(chunk_size=100):
                    fd.write(chunk)
            print (file_count, label['path']+' downloaded')
            os.chdir(current_dir)

        #print(json.dumps(list_output_files_dict, indent=2, separators=(',',': ')))

        current_page += 1
        if (list_output_files_dict['next'] == None):
            last_page = True

    total_file_size = list_output_files_dict['size']
    print ('Total ' + str(file_count) + ' files, ' + str(total_file_size) + 'MB downloaded')
