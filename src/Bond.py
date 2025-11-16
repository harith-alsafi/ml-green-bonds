import pandas as pd
class Bond:
    bond_data: pd.DataFrame
    holders: pd.DataFrame
    def __init__(self, bond_data: pd.DataFrame, holders: pd.DataFrame):
        self.bond_data = bond_data
        self.holders = holders
