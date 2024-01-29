import json
import paho.mqtt.client as mqtt
import time
import threading
import json
import src.top_module.db_top_module as NWDB
import src.utils.methods as umethods

class MiSensor():
    def __init__(self, modb, config, port_config):
        self.mqtt_broker = "192.168.1.33"
        self.mqtt_port = 1884
        self.mqtt_topic = "nw/get/mi"
        self.modb = modb
        self.time_interval = 60
        self.table_name = "data.thirdparty.mi"
        self.last_update_time = None
        self.key = ['sensor_name', 'temperature', 'humidity', 'voltage']

    # def __init__(self, mqtt_broker, mqtt_port, mqtt_topic, interval, mysql_handler, table_name):
    #     self.mqtt_broker = mqtt_broker
    #     self.mqtt_port = mqtt_port
    #     self.mqtt_topic = mqtt_topic
    #     self.interval = interval
    #     self.mysql_handler = mysql_handler
    #     self.table_name = table_name
    #     self.last_update_time = None

    def on_connect(self, client, userdata, flags, rc):
        print("Connected with result code " + str(rc))
        client.subscribe(self.mqtt_topic)

    def on_message(self, client, userdata, msg):
        if time.time() - self.last_update_time >= self.time_interval:
            self.last_update_time = time.time()
            print(f"Message received on topic {msg.topic}: {msg.payload.decode()}")

            sensor_data = json.loads(msg.payload.decode())

            mapped_data = {
                'sensor_name': 'MiSensor1',  # Example sensor name
                'temperature': sensor_data['Temp'],
                'humidity': sensor_data['Humidity'],
                'voltage': sensor_data['Voltage']
            }

            keys = list(mapped_data.keys())
            values = [f'"{mapped_data[k]}"' if isinstance(mapped_data[k], str) 
                      else str(mapped_data[k]) for k in keys]

            # Insert data into the database
            self.modb.insert_mi_sensor_data(self.table_name, keys, values)


    def start(self):
        self.last_update_time = time.time()
        client = mqtt.Client()
        client.on_connect = self.on_connect
        client.on_message = self.on_message

        client.connect(self.mqtt_broker, self.mqtt_port, 60)
        client.loop_start()
        while True:
            time.sleep(self.time_interval)

if __name__ == '__main__':

    def status_summary():
        status = '{"battery": 97.996, "position": {"x": 105.40159891291846, "y": 67.38314149752657, "theta": 75.20575899303867}, "map_id": 2, "map_rm_guid": "277c7d6f-2041-4000-9a9a-13f162c9fbfc"}'
        return status

    config = umethods.load_config('../../../conf/config.properties')
    port_config = umethods.load_config('../../../conf/port_config.properties')
    modb = NWDB.TopModuleDBHandler(config, status_summary)

    mi = MiSensor(modb, config, port_config)
    # print(iaq.parse_json())
    # iaq.set_task_id("")
    mi.start()
    # # time.sleep(5)
    # iaq.set_task_mode(True, task_id=-1)
    # iaq.set_task_mode(False)
    # #
    # time.sleep(1800)

# # Usage
# mqtt_broker = "192.168.1.33"
# mqtt_port = 1884
# mqtt_topic = "nw/get/mi"

# mysql_host = 'localhost'
# mysql_db = 'your_database_name'
# mysql_username = 'your_username'
# mysql_password = 'your_password'

# mqtt_to_mysql = MQTTToMySQL(mqtt_broker, mqtt_port, mqtt_topic, mysql_host, mysql_db, mysql_username, mysql_password)
# mqtt_to_mysql.start()
