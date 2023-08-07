import configparser  # config file
import datetime
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
    now = datetime.datetime.utcnow()
    return now.strftime("%Y-%m-%dT%H:%M:%SZ")

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
    current_time = datetime.datetime.now()

    # Convert the datetime object to a Unix timestamp (seconds since January 1, 1970)
    unix_timestamp = int(current_time.timestamp())

    return unix_timestamp

if __name__ == '__main__':

    # ## method 1 - load config file and then retrieve data
    # config_addr = '../conf/config.properties'
    # config = load_config(config_addr)
    # res = config.get('RV','X-API-Key')
    # print(res)

    # ## method 2 - compare datetime
    # # Get the current time in UTC timezone
    # now = datetime.datetime.utcnow()
    # iso_time1 = now.strftime("%Y-%m-%dT%H:%M:%SZ")
    # print(iso_time1)
    # time.sleep(1)
    # now = datetime.datetime.utcnow()
    # iso_time2 = now.strftime("%Y-%m-%dT%H:%M:%SZ")
    # print(is_future_time(iso_time1, iso_time2))

    # ## method 3 - check network connection
    # while(True):
    #     check_network_connection()
    #     time.sleep(1)

    timestamp = get_unix_timestamp()
    print(timestamp)