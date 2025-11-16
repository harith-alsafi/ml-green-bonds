import pandas as pd 
import os 
from multiprocessing import Pool

from Bond import Bond

holders_columns = [
    "Id Number",
    "Bond Type",
    "Holder Name",
    "Porfolio Name",
    "Parent Holder Id",
    "Holder Id",
    "Portfolio Number",
    "Position",
    "Position Change",
    "Filling Date",
    "Filling Source",
    "Insider Status",
    "Percent Outstanding",
    "Percent of Portfolio",
    "Institution Type",
    "Metro Area",
    "Country"
]

def read_holder_file(file_path: str) -> pd.DataFrame:    
    # Initialize an empty list to store rows
    rows = []
    
    with open(file_path, 'r', encoding='utf-8') as file:
        for line in file:
            try:
                # Split the line by comma
                fields = line.strip().split(',')
                # remove quotation makrs from each field
                fields = [field.strip('"') for field in fields]
                
                [id_number, bond_type] = fields[0].split(' ')
                fields.insert(0, id_number)
                fields[1] = bond_type
                if len(fields) != len(holders_columns):
                    fields[2] = fields[2] + ',' + fields[3]
                    fields.pop(3)
                    print(f"Row with {len(fields)} fields: {fields}")
                # Append the fields to the list of rows
                rows.append(fields)
            except Exception as e:
                print(f"Skipping row with error: {e}")
                continue
    
    # Create DataFrame from the list of rows with column names
    df = pd.DataFrame(rows, columns=holders_columns)

    return df

def read_all_holders(directory_name: str) -> pd.DataFrame:
    dfs = []
    for filename in os.listdir(directory_name):
        if filename.endswith('.csv'):
            file_path = os.path.join(directory_name, filename)
            df = read_holder_file(file_path)
            dfs.append(df)

    return pd.concat(dfs, ignore_index=True)

def read_bonds(file_path: str, holders_directory: str) -> list[Bond]:
    pass