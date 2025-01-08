import pandas as pd
import os

def detect_similar_columns(column_names):
    """
    Detect groups of similar column names.
    Replace this with your custom similarity logic.
    """
    groups = {column_names[0]: [column_names[0]]}
    for col in column_names[1: ]:
        base_name = col[6: col.index(".raw") - 2]
        if base_name not in groups:
            groups[base_name] = []
        groups[base_name].append(col)
    return groups

def apply_column_renames(df, similar_columns, renames, original_path):
    """
    Rename columns in the dataframe based on user input.
    """
    for group, columns in similar_columns.items():
        if group in renames:
            new_name = renames[group]
            for col in columns:
                df.rename(columns={col: new_name}, inplace=True)

    # Move column names down into the first row
    df.loc[-1] = df.columns  # Add column names as the first row
    df.index = df.index + 1  # Shift index to start from 1
    df = df.sort_index()     # Sort by index to properly arrange

    # Set new column titles
    df.columns = ['Metabolite'] + [''] * (len(df.columns) - 1)
    
    # Save the updated CSV
    new_file_path = original_path.replace('.csv', '_renamed.csv')
    df.to_csv(new_file_path, index=False)

    return new_file_path
