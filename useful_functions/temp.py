# data = [
#     [8, 0.0, 21.1], [9, 21.1, 26.7], [11, 26.7, 26.9], [11, 26.9, 33.7], [11, 33.7, 35.6], [7, 35.6, 39.9], 
#     [8, 39.9, 52.1], [9, 52.1, 55.6], [11, 55.6, 57.9], [11, 57.9, 58.3], [11, 58.3, 59.1], [11, 59.1, 59.5], 
#     [11, 59.5, 59.6], [7, 59.6, 63.7], [8, 63.7, 75.2], [9, 75.2, 78.5], [11, 78.5, 82.3], [7, 82.3, 86.8], 
#     [8, 86.8, 98.5], [9, 98.5, 101.6], [11, 101.6, 102.5], [11, 102.5, 103.1], [11, 103.1, 103.6], 
#     [7, 103.6, 110.1], [8, 110.1, 143.5], [9, 143.5, 147.1], [11, 147.1, 147.2], [11, 147.2, 147.7], 
#     [11, 147.7, 148.1], [11, 148.1, 149.3], [11, 149.3, 149.5], [7, 149.5, 154.7], [8, 154.7, 166.3], 
#     [11, 166.3, 172.8]
# ]

# # Convert the list to a text format
# text_data = '\n'.join([','.join(map(str, sublist)) for sublist in data])

# # Write the text data to a file
# with open('test.txt', 'w') as file:
#     file.write(text_data)


def read_data_from_txt(file_path):
    data = []
    with open(file_path, 'r') as file:
        lines = file.readlines()
        for line in lines:
            # Split each line by comma and convert values to the appropriate type
            values = line.strip().split(',')
            values = [int(values[0])] + [int(float(value)*1000) for value in values[1:]]
            data.append(values)
    return data

file_path = 'test.txt'  # Change this to the path of your text file
data = read_data_from_txt(file_path)
print(data)

print(len(data))

for i in data:
    print(i)