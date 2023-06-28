import pandas as pd
import os
from openpyxl.utils.exceptions import IllegalCharacterError
import re

# Set the path to the directory containing the CSV files
csv_directory = r'C:\Users\ricca\Documents\Università\Big Data Engineering\Final_project\WINCARE_CHALLENGE'

# Set the output directory for the Excel files
output_directory = r'C:\Users\ricca\Documents\Università\Big Data Engineering\Final_project\excel_files'

# Specify the delimiter used in the CSV files
delimiter = '\t'  # Replace with your desired delimiter

# Get a list of all CSV files in the directory
csv_files = [file for file in os.listdir(csv_directory) if file.endswith('.csv')]

def clean_data(value):
    if isinstance(value, (str, bytes)):
        # Remove any non-printable characters and line breaks
        cleaned_value = re.sub(r'[^ -~]', '', value)
        return cleaned_value
    else:
        return value

for csv_file in csv_files:
    csv_path = os.path.join(csv_directory, csv_file)
    try:
        df = pd.read_csv(csv_path, delimiter=delimiter, low_memory=False)
        
        # Clean the data in all columns
        df = df.applymap(clean_data)
        
        excel_file_name = os.path.splitext(csv_file)[0]
        excel_file_path = os.path.join(output_directory, excel_file_name + '.xlsx')
        df.to_excel(excel_file_path, index=False)
        print(f"Converted '{csv_file}' to '{excel_file_path}'")
    except pd.errors.ParserError:
        print(f"Error parsing '{csv_file}'. Skipping the file.")
    except IllegalCharacterError:
        print(f"Illegal characters found in '{csv_file}'. Skipping the file.")
