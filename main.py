import pandas as pd #used to load the csv files, manipulate and process data, etc.. (library used for data science)
import os #used to do deal with the operating system, eg input, output, save files, etc.. (Mac in this  case)
from concurrent.futures import ThreadPoolExecutor # same as above
from typing import List, Tuple, Dict # Python is a *not typed language*, meaning it understands basic units. used to classfy input variables (e.g a:List=[])
import networkx as nx # used to visualize nodes and edges
import matplotlib.pyplot as plt #visualisation library (e.g charts, plots, pie chart, etc.)
import numpy as np # library used for linear algebra (e.g matrices) (used to define the adjacency matrix below)

class Bond: #this class is used to store bond data seperately, each instance of the class represnts one bond
    id_number: str #string is the text
    bond_row: pd.Series  # this is the 'row' of  one bond - pd.Series means 'one single row' (this is for the Sustainable Debt Excel sheet)
    holders: pd.DataFrame # list of holders - the pd.DataFrame is the Pandas Library. DataFrame means 'table'- 'more than one row'. (this is for the holders excel for each bond, as represented in a table)
    def __init__(self, id_number:str, bond_row: pd.Series, holders: pd.DataFrame): # intiation of class ( Arguments: 1) Id number, then Bond data, then Holders) 
        self.id_number = id_number # 'self' is refering to the instance of the class (id number of class=id number)
        self.bond_row = bond_row
        self.holders = holders

    # make the class compatable with set()
    def __hash__(self): #this is used
        return hash(self.id_number)
    
    def __eq__(self, other): #this is used to compare two instances of the class
        return self.id_number == other.id_number
    
    def __repr__(self): #this is used to print the instance of the class
        return self.id_number
    
    def __str__(self): #this is used to print the instance of the class
        return self.id_number
    
holders_columns = [ #here, we added a new coloumn called "ID Type" since in the original sheet, ID CORP was together, as shown in the Holders-columns.png, and i thought that putting this info in a spereate column is better
    "ID number",
    "ID Type",
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
    "Country",
    "File Name" # we put this is order to located the csv file of the holder
]

def read_holder_file(file_path: str) -> pd.DataFrame: # function(input)=output....takes input of the file location. This reads one csv holder file
    # Initialize an empty list to store rows 
    rows = []
    
    with open(file_path, 'r', encoding='utf-8') as file: # open file ('r' means read) and i named it (file)
        for line in file: # used to go through each line in our file.
            try:
                # Split the line by comma since the data is comma seperatied (e.g'x,c,v,b,n..') we convert it to a list: [x,c,v]
                fields = line.strip().split(',')
                # remove quotation marks from each field because some of the holders name had a quotation mark, and this can cause ineffeciencies in collecting the data
                fields = [field.strip('"') for field in fields]
                #this below was used to re arrange the rows and columns, seperating the Id number and Id type
                [id_number, bond_type] = fields[0].split(' ') # split by (space bar) because it was (B1234 Corp) and we want to seperate them. Since they are initially seperated by a space, we used this function. And we named the  (id number) (id type)
                fields.insert(0, id_number) #put the new field that were done above (before column 0, we put Id_Number- so now ID number is column 0)
                fields[1] = bond_type # here we take column one and make it the (bond type)
                #this is used to fix the issue where so of the rows in the bond holders list was shifted to the right
                if len(fields) != len(holders_columns)-1: #(-1 is because we added a new column called 'File name' as seen above, but we did not add it yet)
                    fields[2] = fields[2] + ',' + fields[3] #some companies have their name as 'ABC,CO' (They are seperated by a comma), therefore, this line fixes this issue because without it, it would assume that they are two separate columns 
                    fields.pop(3) #removes item 3
                
                fields.append(file_path) #here we added the file name column. 
                
                rows.append(fields)# Add items to the fields to the list of rows to store the items in a table
            except Exception as e:
                print(f"Skipping row with error: {e}")
                continue
    
    # Create DataFrame from the list of rows with column names
    df = pd.DataFrame(rows, columns=holders_columns)

    return df

def read_all_holders(directory_name: str) -> pd.DataFrame:
    def process_file(filename: str) -> pd.DataFrame:
        file_path = os.path.join(directory_name, filename)
        return read_holder_file(file_path)

    filenames = [f for f in os.listdir(directory_name) if f.endswith('.csv')]

    with ThreadPoolExecutor() as executor:
        # Map the process_file function to the list of filenames
        results = list(executor.map(process_file, filenames))
    
    # Concatenate all dataframes into one
    return pd.concat(results, ignore_index=True)


def read_bonds(file_path: str, holders_directory: str) -> set[Bond]: # calls the function above (hodlers) with the bond names from the Sustainable Debt Excel
    bond_table = pd.read_csv(file_path) #read the csv with pandas
    holders = read_all_holders(holders_directory) #we created our own function and did not used pandas because the holders list had issues
    # Merge dataframes based on 'ID number'
    merged_data = bond_table.merge(holders, on='ID number', how='inner')
    # Group the merged data by "ID number"
    grouped_data = merged_data.groupby("ID number")
    result = set()
    for id_number, group in grouped_data:
        bond_row = group.iloc[0, :len(bond_table.columns)] 
        holders_df = group.iloc[:, len(bond_table.columns):] 
        bond = Bond(id_number, bond_row, holders_df) # we are adding the bonds with their holders
        result.add(bond)
    return result

bond_list = read_bonds('all-bonds.csv', 'holders/') # list of classes 'Bond'
total_bonds = len(bond_list)

unique_holders = set()
bond_type_dict: Dict[str, List[Bond]] = {}
issuer_industry_dict: Dict[str, List[Bond]] = {}

for bond in bond_list:
    holders = bond.holders['Holder Name']

    # push holders to unique holders set
    for holder in holders:
        unique_holders.add(holder)
    
    # Handle bond type dictionary
    bond_type = bond.bond_row['Bond type']

    if bond_type not in bond_type_dict:
        bond_type_dict[bond_type] = []
    bond_type_dict[bond_type].append(bond)

    # Handle issuer industry dictionary
    issuer_industry = bond.bond_row['Issuer industry']
    if issuer_industry not in issuer_industry_dict:
        issuer_industry_dict[issuer_industry] = []
    issuer_industry_dict[issuer_industry].append(bond)


holder_to_index = {holder: i for i, holder in enumerate(unique_holders)}
index_to_holder = {i: holder for i, holder in enumerate(unique_holders)}
bond_types = list(bond_type_dict.keys())
num_bond_types = len(bond_types)
num_unique_holders = len(unique_holders)
print(f"Total number of bonds: {total_bonds}")
print(f"Total number of unique holders: {num_unique_holders}")
print(f"Total number of unique bond types: {num_bond_types}")

# Create a dictionary to count bonds of each type
bond_type_counts = {bond_type: len(bonds) for bond_type, bonds in bond_type_dict.items()}

# Calculate percentage distribution of bond types
bond_type_percentages = {bond_type: (count / total_bonds) * 100 for bond_type, count in bond_type_counts.items()}
plt.figure(figsize=(8, 6))
plt.pie(bond_type_percentages.values(), labels=bond_type_percentages.keys(), autopct='%1.1f%%', startangle=140)
plt.title('Percentage Distribution of Bond Types')
plt.axis('equal')  # Equal aspect ratio ensures that pie is drawn as a circle.
plt.show()

# Create a dictionary to count bonds of each type
issuer_industry_counts = {issuer_type: len(bonds) for issuer_type, bonds in issuer_industry_dict.items()}

# Calculate percentage distribution of bond types
issuer_industry_percentages = {issuer_industry: (count / total_bonds) * 100 for issuer_industry, count in issuer_industry_counts.items()}
plt.figure(figsize=(8, 6))
plt.pie(issuer_industry_percentages.values(), labels=issuer_industry_percentages.keys(), autopct='%1.1f%%', startangle=140)
plt.title('Percentage Distribution of Issuer Industries')
plt.axis('equal')  # Equal aspect ratio ensures that pie is drawn as a circle.
plt.show()


# we want to present the data as a graph network using an adjacency matrix
# so basically the unique_holders will represent the nodes of the graph
# when two unique holders are present in the same bond, this indicates an edge meaning we will increment the value of the adjacency matrix at the corresponding index of the two holders
# we will use a dictionary to map the holder name to an index in the adjacency matrix
# Create a defaultdict to collect pairs of indices to be incremented
def create_adjacency_matrix(bond_list, holder_to_index, index_to_holder):
    num_unique_holders = len(holder_to_index)
    adjacency_matrix = np.zeros((num_unique_holders, num_unique_holders), dtype=np.int32)
    # holder name, [number of collaborations, bonds, collaborators]
    holder_info: Dict[str, Tuple[int, List[str], List[str]]] = {}
    for bond in bond_list:
        holders = bond.holders['Holder Name']
        indices = np.unique([holder_to_index[holder] for holder in holders])

        bond_id = bond.id_number
        for index in indices:
            holder = index_to_holder[index]
            if holder not in holder_info:
                holder_info[holder] = [0, [], []]
            holder_info[holder][0] += 1
            holder_info[holder][1].append(bond_id)
            collaborators = [index_to_holder[i] for i in indices if i != index]
            holder_info[holder][2].extend(collaborators)
        
        # adjacency matrix
        i, j = np.meshgrid(indices, indices, indexing='ij')

        # Filter out the diagonal elements (self-connections)
        mask = i != j

        # Update the adjacency matrix with the count of connections
        adjacency_matrix[i[mask], j[mask]] += 1

    # create a pandas dataframe to store the holder information
    holder_df = pd.DataFrame.from_dict(holder_info, orient='index', columns=['Collaborations', 'Bonds', 'Collaborators'])

    # Make the adjacency matrix symmetric
    # adjacency_matrix += adjacency_matrix.T

    return adjacency_matrix, holder_df

# print me the two holders with the highest number of collaborations and their names 
def print_top_collaborations(adjacency_matrix, unique_holders):
    # Get the indices of the top 2 holders with the highest number of collaborations
    i, j = np.unravel_index(np.argsort(adjacency_matrix, axis=None), adjacency_matrix.shape)
    # Get the holder names corresponding to the indices
    holder_names = np.array(list(unique_holders))
    holder_i = holder_names[i[-1]]
    holder_j = holder_names[j[-1]]
    # Get the number of collaborations
    collaborations = adjacency_matrix[i[-1], j[-1]]
    print(f"Top 2 holders with the highest number of collaborations:\n{holder_i} and {holder_j} with {collaborations} collaborations")

adjacency_matrix, holders_df = create_adjacency_matrix(bond_list, holder_to_index, index_to_holder)
G = nx.from_numpy_array(adjacency_matrix, create_using=nx.Graph())
print_top_collaborations(adjacency_matrix, unique_holders)

print(adjacency_matrix[0:20, 0:20]) # TODO: prints the first 20 rows and columns of the adjacency matrix 

# sort the holders with the highest number of collaborations
holders_df = holders_df.sort_values(by='Collaborations', ascending=False)

holders_df.head(20) # TODO: prints the top 20 holders with the highest number of collaborations

# only select part of adjacency matrix that is non zero to make the plot more readable

cax = plt.matshow(adjacency_matrix[0:15, 0:15], cmap='coolwarm', vmin=0, vmax=15) # TODO: visuaize the adjacency matrix with the first 15 rows and columns, (vmax is max number of collaborations to show)

# Adding color bar
plt.colorbar(cax)

# Adding labels
plt.title('Adjacency Matrix Heatmap')
plt.xlabel('Node')
plt.ylabel('Node')


plt.show()


# Function to find 10 nodes each having at least 2 connections within the subset
def find_suitable_nodes(G, num_nodes=10, min_connections=2):

    # Start with nodes sorted by degree (descending)
    sorted_nodes = sorted(G.nodes(), key=lambda n: G.degree(n), reverse=True)

    for start_node in sorted_nodes:
        # Begin with the highest-degree node and attempt to build a suitable subset
        sub_nodes = [start_node]
        for node in sorted_nodes:
            if node not in sub_nodes and all(G.degree(n) >= min_connections for n in sub_nodes):
                sub_nodes.append(node)
            if len(sub_nodes) == num_nodes:
                break
        
        subgraph = G.subgraph(sub_nodes)
        if len(subgraph) == num_nodes and all(subgraph.degree(n) >= min_connections for n in sub_nodes):
            return sub_nodes

    return None

# Find 10 suitable nodes
suitable_nodes = find_suitable_nodes(G, num_nodes=10, min_connections=1) # TODO: extracts 10 nodes to visualize in the following block of code

print(f"Suitable nodes: {suitable_nodes}")


if suitable_nodes:
    subgraph = G.subgraph(suitable_nodes)
    number_of_nodes = len(suitable_nodes)
    # plot each node with its own color so we can add it to the legend
    node_colors = np.linspace(0, 1, number_of_nodes)
    node_color_map = plt.get_cmap('coolwarm')
    node_colors = [node_color_map(c) for c in node_colors]

    nx.draw(subgraph, with_labels=False, node_color=node_colors, node_size=700, edge_color='gray') #The False is used to hide the node names(indices) 
    plt.title(f'Subgraph with {number_of_nodes} Nodes')
    # now add a legend for each node color with its corresponding holder name 
    plt.legend(handles=[plt.Line2D([0], [0], marker='o', color='w', label=index_to_holder[node], markerfacecolor=color, markersize=10) for node, color in zip(suitable_nodes, node_colors)], loc='upper left', bbox_to_anchor=(1.05, 1)) 

    plt.show()
else:
    print("No suitable nodes found with the given criteria.")