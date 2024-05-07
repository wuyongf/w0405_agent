import configparser  # config file
from datetime import datetime
import time
import requests

def load_config(config_addr):
        # Load config file
        configs = configparser.ConfigParser()
        try:
            configs.read(config_addr)
        except:
            print("Error loading properties file, check the correct directory")
        return configs

def get_current_time():
    now = datetime.utcnow()
    return now.strftime("%Y-%m-%dT%H:%M:%SZ")

def get_current_date():
    now = datetime.utcnow()
    return now.strftime("%Y%m%d")

def is_future_time(scheduled, current):
    # Compare the datetime objects
    if scheduled is not None:
        if scheduled > current: return True
    return False

def check_network_connection(url = ''):
    try:
        res = requests.get('https://prod.robotmanager.com/')
        if (res.status_code):
            print('Success')
    except:
        print('[check_network_connection] Error. Please check IPC network connection...')

def get_unix_timestamp():
    # Get the current time as a datetime object
    current_time = datetime.now()

    # Convert the datetime object to a Unix timestamp (seconds since January 1, 1970)
    unix_timestamp = int(current_time.timestamp())

    return unix_timestamp

def convert_timestamp2date(timestamp):
    formatted_date = datetime.fromtimestamp(timestamp).strftime('%Y-%m-%d %H:%M:%S')
    return formatted_date

def convert_list2txt(list, output_file_dir):
    # Save the results to a file
    # output_file_dir = 'gyro_compact_info.txt'
    with open(output_file_dir, 'w') as output_file:
        for idx, result in enumerate(list):
            if(idx is len(list)-1): output_file.write(str(result))
            else:output_file.write(str(result) + '\n')
    return output_file_dir

def count_duration(sleep_sec):
    start_time = time.time()
    
    # your method
    time.sleep(sleep_sec)
    
    end_time = time.time()

    execution_time = end_time - start_time
    print(f"Execution time: {execution_time} seconds")

if __name__ == '__main__':

    # ## method 1 - load config file and then retrieve data
    # config_addr = '../conf/config.properties'
    # config = load_config(config_addr)
    # res = config.get('RV','X-API-Key')
    # print(res)

    # ## method 2 - compare datetime
    # # Get the current time in UTC timezone
    # now = datetime.utcnow()
    # iso_time1 = now.strftime("%Y-%m-%dT%H:%M:%SZ")
    # print(iso_time1)
    # time.sleep(1)
    # now = datetime.utcnow()
    # iso_time2 = now.strftime("%Y-%m-%dT%H:%M:%SZ")
    # print(is_future_time(iso_time1, iso_time2))

    # ## method 3 - check network connection
    # while(True):
    #     check_network_connection()
    #     time.sleep(1)

    # timestamp = get_current_date()
    # print(timestamp)

    count_duration(5)