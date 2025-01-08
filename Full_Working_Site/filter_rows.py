import pandas as pd
import os

def filter_rows(cd_df, val_df):
    # Create set of names where Main Category == 'Metabolite'
    metabolite_names = set(val_df[val_df['Main Category'] == 'Metabolite']['Name'])
    metabolite_names.add('Class')

    # Delete rows from cd_df if not row 0 or have name in metabolite_names
    df = cd_df[cd_df['Metabolite'].isin(metabolite_names)]
    df_qc = df.drop_duplicates(subset=['Metabolite'])
    
    # Remove QC's for heatmaps
    df_no_qc = df_qc.loc[:, ~df_qc.iloc[0].str.contains('QC', case=False)]

    # Create set of names where General Classification == 'Flavonoid'
    flavonoid_names = set(val_df[val_df['General Classification'] == 'Flavonoid']['Name'])
    flavonoid_names.add('Class')

    # Create flavonoid version
    flav_qc = df_qc[df_qc['Metabolite'].isin(flavonoid_names)]

    # hopefully self explanatory
    flav_no_qc = flav_qc.loc[:, ~flav_qc.iloc[0].str.contains('QC', case=False)]

    return [df_qc, df_no_qc, flav_qc, flav_no_qc]

