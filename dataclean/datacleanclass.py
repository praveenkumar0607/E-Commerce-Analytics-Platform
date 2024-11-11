import pandas as pd
import numpy as np
from sklearn.preprocessing import MinMaxScaler

class DataCleaner:
    def __init__(self, file_path):
        """
        Initialize DataCleaner object with a file path and load the CSV into a DataFrame.

        Args:
        - file_path (str): Path to the CSV file.

        Attributes:
        - file_path (str): Path to the CSV file.
        - df (pandas.DataFrame): DataFrame containing the data from the CSV file.
        """
        self.file_path = file_path
        self.df = pd.read_csv(file_path)
    
    def DataInfo(self):
        info = {
            'columns': list(self.df.columns),
            'null_values': self.df.isnull().sum().to_dict(),
            'total_rows': len(self.df),
            'total_columns': len(self.df.columns),
            'data_types': self.df.dtypes.to_dict()
        }
        return info

    def fill_null_values(self):
        """
        Fill null values in the DataFrame using forward fill (ffill) and backward fill (bfill).
        """
        self.df.ffill(inplace=True)
        self.df.bfill(inplace=True)
    
    def remove_columns(self, columns_list):
        """
        Remove specified columns from the DataFrame.

        Args:
        - columns_list (list): List of column names to remove.
        """
        print(f"DataFrame before removing columns: {self.df.shape}")
        print(f"Columns before removal: {self.df.columns}")
        # Check if each column exists before attempting to drop it
        existing_columns = [column for column in columns_list if column in self.df.columns]
        if not existing_columns:
            print(f"No columns from {columns_list} found in the DataFrame.")
        else:
            self.df.drop(columns=existing_columns, inplace=True)
        print(f"DataFrame after removing columns: {self.df.shape}")
        print(f"Columns after removal: {self.df.columns}")
        
    def remove_duplicates(self):
        """
        Remove duplicate rows from the DataFrame.
        """
        self.df.drop_duplicates(inplace=True)
    
    def save_changes_to_csv(self):
        """
        Save the cleaned DataFrame back to the original CSV file.
        """
        self.df.to_csv(self.file_path, index=False)
        
    def convert_data_type(self, column_name, data_type):
        """
        Convert the data type of a column in the DataFrame.

        Args:
        - column_name (str): Name of the column to convert.
        - data_type (type or list of types): Desired data type(s) to convert the column to.
        """
        for dtype in data_type:
            try:
                self.df[column_name] = self.df[column_name].astype(dtype)
                break
            except ValueError:
                continue
    
    def normalize_data(self, column_name):
        """
        Normalize numerical data in the specified column using Min-Max scaling.

        Args:
        - column_name (str): Name of the numerical column to normalize.
        """
        scaler = MinMaxScaler()
        self.df[column_name] = scaler.fit_transform(self.df[column_name].values.reshape(-1,1))
        
    def filter_data(self, column_name, condition):
        """
        Filter the DataFrame based on a condition applied to a column.

        Args:
        - column_name (str): Name of the column to apply the filter on.
        - condition (function): Function defining the filtering condition.
        """
        self.df = self.df[self.df[column_name].apply(condition)]
        
    def lowercase_string(self, column_name):
        """
        Convert strings in the specified column to lowercase.

        Args:
        - column_name (str): Name of the column containing strings to convert.
        """
        self.df[column_name] = self.df[column_name].str.lower()
        
    def trim_whitespace(self, column_name):
        """
        Remove leading and trailing whitespace from strings in the specified columns.

        Args:
        - column_name (str or list of str): Name of the column(s) containing strings to trim whitespace from.
        """
        if isinstance(column_name, str):
            column_name = [column_name]
        for column in column_name:
            self.df[column] = self.df[column].str.strip()
    
    def export_to_csv(self, output_file):
        self.df.to_csv(output_file, index=False)
        
    def clean_data(self):
        """
        Perform a sequence of cleaning operations on the DataFrame and save changes.
        """
        self.fill_null_values()
        self.remove_duplicates()
        columns_to_remove = ['Customer_Email', 'Customer_Password', 'Product_Description', 'Product_Image', 'Product_Status']
        self.remove_columns(columns_to_remove)
        self.save_changes_to_csv()
