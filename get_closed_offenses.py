#!/usr/bin/python

import logging.handlers
import requests
import json
import time
from datetime import datetime, timedelta
import csv

LOG_FILE='get_closed_offenses.log'
LOG_LEVEL=logging.INFO
QRADAR_IP=''
QRADAR_TOKEN=''
OUTPUT_FILE='closed_offenses.csv'
DAYS=30

logging.basicConfig(format='%(asctime)s %(levelname)s: %(message)s', datefmt='%Y/%m/%d %H:%M:%S', filename=LOG_FILE,level=LOG_LEVEL)

logging.info('Starting get_closed_offenses')

headers = {'SEC': 'ddd', 'content-type': 'application/json', 'Accept': 'application/json'}
headers['SEC'] = QRADAR_TOKEN  
offenses_closing_data_json={}
try:
    logging.info('Connecting to get offense closing reasons')
    offenses_closing_data = requests.get( "https://"+QRADAR_IP+"/api/siem/offense_closing_reasons" ,headers = headers , verify=False)
    offenses_closing_data_json=offenses_closing_data.json()
    print ('############################')
    print (offenses_closing_data_json)
except Exception as e:
    logging.error('Falling getting offense closing reasons')
    logging.error(e)



consultas = []
offenses_data={}
try:
    logging.info('Connecting to get offense info')
    yday = datetime.strftime(datetime.now() - timedelta(DAYS), '%d.%m.%Y %H:%M:%S,%f')
    date_obj = datetime.strptime (yday, '%d.%m.%Y %H:%M:%S,%f')
    milliseconds = date_obj.timestamp() * 1000
    time_mil = round(milliseconds)
    offenses_data = requests.get( "https://"+QRADAR_IP+"/api/siem/offenses?fields=id%2C%20description%2C%20event_count%2C%20flow_count%2C%20assigned_to%2Cclosing_user%2C%20close_time%2C%20last_updated_time%2C%20start_time%2Cclosing_reason_id%20%2C%20domain_id&filter=status%3D'CLOSED'%20and%20close_time%20%3E%3D%20" + str(time_mil) ,headers = headers , verify=False)
    print(offenses_data.json())
    print (time_mil)
except Exception as e:
    logging.error('Falling getting offense info')
    logging.error(e)

with open(OUTPUT_FILE, 'w') as outfile:
    wr = csv.writer(outfile, quoting=csv.QUOTE_ALL)
    for ofensa in offenses_data.json():
        ofensa['closing_reason_desc']=[y['text'] for y in offenses_closing_data_json if ofensa['closing_reason_id'] == y['id']][0]
        consultas.append(ofensa)
        print(ofensa)
        offense_row=[]
        for property in ofensa:
            offense_row.append(str(ofensa[property]).replace('\n', '--'))
        wr.writerow(offense_row)
    outfile.close()
