import configparser  # config file
import datetime
import time

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

if __name__ == '__main__':

    # ## method 1 - load config file and then retrieve data
    # config_addr = '../conf/config.properties'
    # config = load_config(config_addr)
    # res = config.get('RV','X-API-Key')
    # print(res)

    ## method 2 - compare datetime
    # Get the current time in UTC timezone
    now = datetime.datetime.utcnow()
    iso_time1 = now.strftime("%Y-%m-%dT%H:%M:%SZ")
    print(iso_time1)
    time.sleep(1)
    now = datetime.datetime.utcnow()
    iso_time2 = now.strftime("%Y-%m-%dT%H:%M:%SZ")

    print(is_future_time(iso_time1, iso_time2))