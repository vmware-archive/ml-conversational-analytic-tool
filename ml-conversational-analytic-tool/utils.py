import ast
import os
from pathlib import Path

import pandas as pd

EXPORTS_DIR = "exports"


def export_to_cvs(export_df: pd.DataFrame, name):
    """
    Export DataFrame into csv file with name constructed based on the given name or default_name
    """

    if not os.path.exists(EXPORTS_DIR):
        os.mkdir(EXPORTS_DIR)

    file = os.path.join(EXPORTS_DIR, name)

    export_df.to_csv(file, index=False)
    print("Output file: ", os.path.abspath(file))


def construct_file_name(name, raw_datafile, suffix):
    if name:
        _, file_extension = os.path.splitext(name)
        if not file_extension:
            name = name + ".csv"
        return name
    else:
        return Path(raw_datafile).stem + suffix + ".csv"


def string_to_dict(string):
    """Function to convert json strings to dictionary"""
    string = ast.literal_eval(string)
    for i in range(len(string)):
        string[i] = ast.literal_eval(string[i])
    return string
