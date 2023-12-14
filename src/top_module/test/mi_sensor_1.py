from lywsd03mmc import Lywsd03mmcClient
client = Lywsd03mmcClient("A4:C1:38:9E:E2:B8")

data = client.data
print('Temperature: ' + str(data.temperature))
print('Humidity: ' + str(data.humidity))
print('Battery: ' + str(data.battery))
print('Display units: ' + client.units)