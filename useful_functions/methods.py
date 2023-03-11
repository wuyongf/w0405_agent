import configparser  # config file

def load_config(config_addr):
        # Load config file
        configs = configparser.ConfigParser()
        try:
            configs.read(config_addr)
        except:
            print("Error loading properties file, check the correct directory")
        return configs

if __name__ == '__main__':

    ## method 1 - load config file and then retrieve data
    config_addr = '../conf/config.properties'
    config = load_config(config_addr)
    res = config.get('RV','X-API-Key')
    print(res)