# importing required modules 
from PyPDF2 import PdfReader 
import csv

def split2list(string: str):
    
    lines = string.split('\n')  # Splitting the string into lines

    # Splitting the lines further to extract the desired elements
    list_a = [
        lines[2],  # Index 2 contains '83576774'
        lines[1].split(' / ')[1],  # Splitting index 1 using ' / ' and taking the second part 'H-90001'
        lines[0],  # Index 0 contains 'Finish Line Check High Waisted Bottoms'
        lines[1].split(' / ')[0]  # Splitting index 1 using ' / ' and taking the first part 'XXS'
    ]

    return list_a

if __name__ == '__main__':
    # creating a pdf reader object 
    reader = PdfReader('Tops_Suits.pdf') 
    
    # printing number of pages in pdf file 
    print(len(reader.pages)) 
    
    final_list = []
    for index in range(len(reader.pages)):
        # getting a specific page from the pdf file 
        page = reader.pages[0]       
        # extracting text from page 
        text = page.extract_text()

        temp_list = split2list(text)

        final_list.append(temp_list)
    
    print(final_list)

    # Define the file name to save the CSV
    file_name = 'temp.csv'

    # Writing the data to a CSV file
    with open(file_name, mode='w', newline='') as file:
        writer = csv.writer(file)
        writer.writerows(final_list)

    print(f"CSV file '{file_name}' has been created successfully.")