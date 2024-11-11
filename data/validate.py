from pathlib import Path,os
from django.core.exceptions import ValidationError
import io
import csv
import pandas as pd


def validate_csv_file(file):
    """
    Reads and validates the uploaded CSV file.

    Args:
        file: The uploaded CSV file object.

    Returns:
        A String buffer containing the cleaned CSV data.

    Raises:
        Exception: If the file cannot be decoded using any of the specified encodings.
    """

    encodings = ['utf-8', 'latin1', 'iso-8859-1']  # Common encodings to try
    for encoding in encodings:
        try:
            # Read the CSV data using pandas
            file.seek(0)  # Rewind the file pointer
            df = pd.read_csv(file, encoding=encoding)

            # Perform your validation logic here if needed
            # Example: Check for required columns, data types, etc.

            # Assuming you don't need to modify the DataFrame, create a StringIO object for cleaned data
            cleaned_csv_file = io.StringIO()
            df.to_csv(cleaned_csv_file, index=False, encoding='utf-8')
            cleaned_csv_file.seek(0)  # Rewind the buffer for reading
            return cleaned_csv_file

        except UnicodeDecodeError as e:
            print(f"Failed to decode with encoding {encoding}, trying next...")

    raise Exception("Unable to read CSV file with any of the specified encodings")


def validate_file_extension(value):
    """
    Validates the file extension of the uploaded file.

    Args:
        value: The uploaded file object.

    Raises:
        ValidationError: If the file extension is not allowed.
    """
    ext = value.name.split('.')[-1].lower()
    valid_extensions = ['csv', 'xlsx', 'xls']
    if ext not in valid_extensions:
        raise ValidationError("Only CSV, Excel (.xlsx, .xls) files are allowed")
