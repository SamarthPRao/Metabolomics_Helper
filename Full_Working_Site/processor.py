import pandas as pd
import numpy as np
from openpyxl import load_workbook
from openpyxl.styles import PatternFill, Font, Alignment
from openpyxl.formatting.rule import CellIsRule
from openpyxl.formatting.rule import FormulaRule

def process_files(cs, mz, ml, database):

    df_cs = pd.read_excel(cs)
    df_mz = pd.read_excel(mz)
    df_ml = pd.read_excel(ml)
    df_database = pd.read_excel(database)

    # function for removing nan's
    def remove_nans(inp):
        out = []
        for i in inp:
            if type(i) == str:
                out.append(i)
        return out

    # finds row of lower bar
    lower_bar_cs_init = df_cs.iloc[1]
    lower_bar_mz_init = df_mz.iloc[1]
    lower_bar_ml_init = df_ml.iloc[1]

    # remove nan's
    lower_bar_cs = remove_nans(lower_bar_cs_init)
    lower_bar_mz = remove_nans(lower_bar_mz_init)
    lower_bar_ml = remove_nans(lower_bar_ml_init)

    # finds where the compounds are
    compound_locations_cs = []
    for i in range(df_cs.shape[0]):
        if remove_nans(df_cs.iloc[i]) == lower_bar_cs:
            compound_locations_cs.append(i - 1)

    # Gets information about where data is located
    cs_id_location = df_cs.iloc[1].to_list().index('CSID')
    cs_ref_location = df_cs.iloc[1].to_list().index('# References')
    cs_structure_location = df_cs.iloc[1].to_list().index('Structure')
    if 'Match Type' in lower_bar_cs:
        cs_match_type_location = df_cs.iloc[1].to_list().index('Match Type')
    else:
        cs_match_type_location = None

    csid_list = []
    cs_structure_list = []
    compound_locations_cs_set = set(compound_locations_cs)

    if cs_match_type_location:
        for i, val in enumerate(np.array(compound_locations_cs) + 2):
            if val in compound_locations_cs_set:
                csid_list.append('')
                cs_structure_list.append('')
            else:
                idx = val
                candidates = {}
                while idx < df_cs.shape[0] and idx not in compound_locations_cs_set:
                    if df_cs.iloc[idx, cs_match_type_location] == 'Full match':
                        candidates[df_cs.iloc[idx, cs_ref_location]] = [df_cs.iloc[idx, cs_id_location],
                                                            df_cs.iloc[idx, cs_structure_location]]
                    idx += 1
                if len(candidates) == 0:
                    csid_list.append('')
                    cs_structure_list.append('')
                else:
                    csid_list.append(candidates[max(candidates.keys())][0])
                    cs_structure_list.append(candidates[max(candidates.keys())][1])
    else:
        match_type_col_cs = df_cs.columns.to_list().index('Annot. Source: ChemSpider Search')
        for i, val in enumerate(np.array(compound_locations_cs) + 2):
            if val in compound_locations_cs_set:
                csid_list.append('')
                cs_structure_list.append('')
            else:
                idx = val
                candidates = {}
                while idx < df_cs.shape[0] and idx not in compound_locations_cs_set:
                    if df_cs.iloc[val - 2, match_type_col_cs] == 'Full match':
                        candidates[df_cs.iloc[idx, cs_ref_location]] = [df_cs.iloc[idx, cs_id_location],
                                                            df_cs.iloc[idx, cs_structure_location]]
                    idx += 1
                if len(candidates) == 0:
                    csid_list.append('')
                    cs_structure_list.append('')

                else:
                    csid_list.append(candidates[max(candidates.keys())][0])
                    cs_structure_list.append(candidates[max(candidates.keys())][1])

    compound_names_cs = df_cs.loc[:, 'Name'][compound_locations_cs].to_list()
    compound_formulas_cs = df_cs.loc[:, 'Formula'][compound_locations_cs].to_list()
    compound_mw_cs = df_cs.loc[:, 'Calc. MW'][compound_locations_cs].to_list()
    compound_rt_cs = df_cs.loc[:, 'RT [min]'][compound_locations_cs].to_list()

    # Creates dictionary with information about each compound
    # Also removes duplicates
    cs_name_set = set()
    cs_dict = {}
    for i in range(len(compound_names_cs)):
        if compound_names_cs[i] not in cs_name_set:
            cs_name_set.add(compound_names_cs[i])
            cs_dict[compound_names_cs[i]] = [compound_formulas_cs[i],
                                        compound_mw_cs[i],
                                        compound_rt_cs[i],
                                        str(csid_list[i]),
                                        cs_structure_list[i]]

    # same code as earlier
    compound_locations_mz = []
    for i in range(df_mz.shape[0]):
        if remove_nans(df_mz.iloc[i]) == lower_bar_mz:
            compound_locations_mz.append(i - 1)

    # Getting locations of important data
    mz_id_location = df_mz.iloc[1].to_list().index('mzCloud ID')
    mz_match_location = df_mz.iloc[1].to_list().index('Best Match')
    mz_structure_location = df_mz.iloc[1].to_list().index('Structure')

    mz_id_list = []
    mz_structure_list = []
    compound_locations_mz_set = set(compound_locations_mz)

    for i, val in enumerate(np.array(compound_locations_mz) + 2):
        if val in compound_locations_mz_set:
            mz_id_list.append('')
            mz_structure_list.append('')
        else:
            idx = val
            candidates = {}
            while idx < df_mz.shape[0] and idx not in compound_locations_mz_set:
                if 'Reference' in df_mz.iloc[idx, mz_id_location]:
                    candidates[df_mz.iloc[idx, mz_match_location]] = [df_mz.iloc[idx, mz_id_location][10:],
                                                            df_mz.iloc[idx, mz_structure_location]]
                idx += 1
            if len(candidates) == 0:
                mz_id_list.append('')
                mz_structure_list.append('')
            else:
                mz_id_list.append(candidates[max(candidates.keys())][0])
                mz_structure_list.append(candidates[max(candidates.keys())][1])
    #laksdnfjlansdjgna;kngkj;angjnajkldgn
    # Getting compound names for this file
    compound_names_mz = df_mz.loc[:, 'Name'][compound_locations_mz].to_list()

    # create mzCloud dictionary
    mz_name_set = set()
    mz_dict = {}
    for i in range(len(compound_names_mz)):
        if compound_names_mz[i] not in mz_name_set:
            mz_name_set.add(compound_names_mz[i])
            mz_dict[compound_names_mz[i]] = [mz_id_list[i], mz_structure_list[i]]

    # same code as earlier
    compound_locations_ml = []
    for i in range(df_ml.shape[0]):
        if remove_nans(df_ml.iloc[i]) == lower_bar_ml:
            compound_locations_ml.append(i - 1)

    ml_id_location = df_ml.iloc[1].to_list().index('FL_index')
    ml_structure_location = df_ml.iloc[1].to_list().index('Structure')
    if 'Compound Match' in lower_bar_ml:
        ml_match_location = df_ml.iloc[1].to_list().index('Compound Match')
    else:
        ml_match_location = None
    
    if 'npaid' in lower_bar_ml:
        npaid_location = df_ml.iloc[1].to_list().index('npaid')
    else:
        npaid_location = None  

    mlid_list = []
    ml_structure_list = []
    compound_locations_ml_set = set(compound_locations_ml)

    if ml_match_location:
        for i, val in enumerate(np.array(compound_locations_ml) + 2):
            appended = False
            if val in compound_locations_ml_set:
                mlid_list.append('')
                ml_structure_list.append('')
            else:
                idx = val
            while idx < df_ml.shape[0] and idx not in compound_locations_ml_set:
                if df_ml.iloc[idx, ml_match_location] == 'Full match':
                    appended = True
                    mlid_list.append(df_ml.iloc[idx, ml_id_location][28:])
                    ml_structure_list.append(df_ml.iloc[idx, ml_structure_location])
                    break
                idx += 1
            if not appended:
                mlid_list.append('')
                ml_structure_list.append('')
    else:
        match_type_col_ml = df_ml.columns.to_list().index('Annot. Source: MassList Search')
        appended = False
        for i, val in enumerate(np.array(compound_locations_ml) + 2):
            if val in compound_locations_ml_set:
                mlid_list.append('')
                ml_structure_list.append('')
            else:
                idx = val
                appended = False

            while idx < df_ml.shape[0] and idx not in compound_locations_ml_set:
                if df_ml.iloc[val - 2, match_type_col_ml] == 'Full match':
                    # This means that it's an FL###### code
                    if type(df_ml.iloc[idx, ml_id_location]) != float:
                        appended = True
                        mlid_list.append(df_ml.iloc[idx, ml_id_location][28:])
          
                    # This means that it's a NPA##### code
                    else:
                        appended = True
                        mlid_list.append(df_ml.iloc[idx, npaid_location])
                    ml_structure_list.append(df_ml.iloc[idx, ml_structure_location])
                    break
                idx += 1
            
            if not appended:
                mlid_list.append('')
                ml_structure_list.append('')

    # getting names from mass list
    compound_names_ml = df_ml.loc[:, 'Name'][compound_locations_ml].to_list()

    ml_name_set = set()
    ml_dict = {}
    for i in range(len(compound_names_ml)):
        if compound_names_ml[i] not in ml_name_set:
            ml_name_set.add(compound_names_ml[i])
            ml_dict[compound_names_ml[i]] = [mlid_list[i], ml_structure_list[i]]

    output_df = pd.DataFrame()
    output_df['Name'] = cs_dict.keys()
    output_df['Formula'] = [cs_dict[i][0] for i in cs_dict.keys()]
    output_df['Calc. MW'] = [cs_dict[i][1] for i in cs_dict.keys()]
    output_df['RT [min]'] = [cs_dict[i][2] for i in cs_dict.keys()]
    output_df['ChemSpider ID'] = [cs_dict[i][3] for i in cs_dict.keys()]

    mz_col = []
    for i in cs_dict.keys():
        if i in mz_dict.keys():
            mz_col.append(mz_dict[i][0])
        else:
            mz_col.append('')
    output_df['mzCloud ID'] = mz_col
    ml_col = []

    for i in cs_dict.keys():
        if i in ml_dict.keys():
            ml_col.append(ml_dict[i][0])
        else:
            ml_col.append('')
    output_df['Mass List ID'] = ml_col
    annot_list = []

    for i in range(output_df.shape[0]):
        lvl = 0
        if str(output_df.loc[i, 'ChemSpider ID']) != '':
            lvl += 1
        if str(output_df.loc[i, 'mzCloud ID']) != '':
            lvl += 1
        if str(output_df.loc[i, 'Mass List ID']) != '':
            lvl += 1
        annot_list.append(lvl)
    output_df['Annotation Level'] = annot_list

    structure_dict = {}
    counter = 0
    for names in output_df['Name']:
        if names in cs_dict.keys():
            structure_dict[names] = cs_dict[names][4]
        if names in mz_dict.keys():
            if mz_dict[names][1]:
                structure_dict[names] = mz_dict[names][1]
        if names in ml_dict.keys():
            if ml_dict[names][1]:
                structure_dict[names] = ml_dict[names][1]

    structure_list = []
    for i in range(output_df.shape[0]):
        structure_list.append(structure_dict[output_df.loc[i, 'Name']])
    output_df['Structure'] = structure_list

    # create a dictionary based on Metabolite that saves the rest of the data
    metabolite_dict = {}
    for i in range(df_database.shape[0]):
        category = df_database.iloc[i, 0]
        classification = df_database.iloc[i, 2]
        subclass = df_database.iloc[i, 3]
        comments = df_database.iloc[i, 4]
        metabolite_dict[df_database.iloc[i, 1]] = [category, classification, subclass, comments]

    category, classification, subclass, comments, esi = [], [], [], [], []
    for i in range(output_df.shape[0]):
        esi.append('ESI+')
        if output_df.loc[i, 'Name'] in metabolite_dict.keys():
            category.append(metabolite_dict[output_df.loc[i, 'Name']][0])
            classification.append(metabolite_dict[output_df.loc[i, 'Name']][1])
            subclass.append(metabolite_dict[output_df.loc[i, 'Name']][2])
            comments.append(metabolite_dict[output_df.loc[i, 'Name']][3])
        else:
            category.append('')
            classification.append('')
            subclass.append('')
            comments.append('')

    output_df['Main Category'] = category
    output_df['General Classification'] = classification
    output_df['Sub-class'] = subclass
    output_df['Comments'] = comments
    output_df['ESI Mode'] = esi

    desired_cols = ['Main Category', 'Name', 'Formula', 'ESI Mode', 'Calc. MW', 'RT [min]', 'Annotation Level', 'ChemSpider ID',
                    'mzCloud ID', 'Mass List ID', 'General Classification', 'Sub-class', 'Comments', 'Structure']

    output_df = output_df[desired_cols]

    # download output_df as an excel file
    output_df.to_excel('output.xlsx', index=False)

    # Load the workbook and select the active sheet
    workbook = load_workbook("output.xlsx")
    sheet = workbook.active
    sheet.title = "Validation"

    # Define the new colors for each level
    color_map = {
        3: PatternFill(start_color="B7E1CD", end_color="B7E1CD", fill_type="solid"),  # Light green
        2: PatternFill(start_color="FFF2CC", end_color="FFF2CC", fill_type="solid"),  # Light yellow
        1: PatternFill(start_color="F4CCCC", end_color="F4CCCC", fill_type="solid"),  # Pinkish red
        0: PatternFill(start_color="D9D9D9", end_color="D9D9D9", fill_type="solid"),  # Light gray
    }

    # Find the column for 'Annotation Level'
    for cell in sheet[1]:  # Assumes header is in the first row
        if cell.value == "Annotation Level":
            annotation_column = cell.column_letter
            break

    # Apply conditional formatting rules for each level
    for level, fill in color_map.items():
        rule = CellIsRule(operator="equal", formula=[str(level)], fill=fill)
        sheet.conditional_formatting.add(f"{annotation_column}2:{annotation_column}{sheet.max_row}", rule)

    color_map = {
        "Metabolite": PatternFill(start_color="93C47D", end_color="93C47D", fill_type="solid"),  # Medium green
        "Unmatched": PatternFill(start_color="FFD966", end_color="FFD966", fill_type="solid"),   # Medium yellow
        "Synthetic": PatternFill(start_color="E6B8AF", end_color="E6B8AF", fill_type="solid"),   # Darker pinkish red
    }

    # Find the column for 'Main Category'
    for cell in sheet[1]:  # Assumes header is in the first row
        if cell.value == "Main Category":
            category_column = cell.column_letter
            break

    # Apply conditional formatting rules for each category
    for category, fill in color_map.items():
        # Using FormulaRule to check if the cell value matches the category
        rule = FormulaRule(formula=[f'ISNUMBER(SEARCH("{category}", {category_column}2))'], fill=fill)
        sheet.conditional_formatting.add(f"{category_column}2:{category_column}{sheet.max_row}", rule)

    # Find the column for 'ChemSpider ID'
    for cell in sheet[1]:  # Assumes header is in the first row
        if cell.value == "ChemSpider ID":
            chemspider_column = cell.column_letter
            break

    # Convert each non-blank cell in the 'ChemSpider ID' column to a hyperlink
    for row in range(2, sheet.max_row + 1):  # Start from row 2, assuming row 1 is the header
        cell = sheet[f"{chemspider_column}{row}"]
        if cell.value:  # If the cell is not blank
            chemspider_id = str(cell.value)
            link = f"https://www.chemspider.com/Chemical-Structure.{chemspider_id}.html"
            cell.hyperlink = link
            cell.value = int(chemspider_id)  # Keeps the text the same as the original ID
            cell.style = "Hyperlink"  # Apply hyperlink style for consistent formatting

    # Find the column for 'mzCloud ID'
    for cell in sheet[1]:  # Assumes header is in the first row
        if cell.value == "mzCloud ID":
            mzCloud_column = cell.column_letter
            break

    # Convert each non-blank cell in the 'mzCloud ID' column to a hyperlink
    for row in range(2, sheet.max_row + 1):  # Start from row 2, assuming row 1 is the header
        cell = sheet[f"{mzCloud_column}{row}"]
        if cell.value:  # If the cell is not blank
            mzCloud_id = str(cell.value)
            link = f"https://www.mzcloud.org/compound/reference/{mzCloud_id}"
            cell.hyperlink = link
            cell.value = int(mzCloud_id)  # Keeps the text the same as the original ID
            cell.style = "Hyperlink"  # Apply hyperlink style for consistent formatting

    # Find the column for 'Mass List ID'
    for cell in sheet[1]:  # Assumes header is in the first row
        if cell.value == "Mass List ID":
            masslist_column = cell.column_letter
            break

    # Convert each non-blank cell in the 'Mass List ID' column to a hyperlink
    for row in range(2, sheet.max_row + 1):  # Start from row 2, assuming row 1 is the header
        cell = sheet[f"{masslist_column}{row}"]
        if cell.value:  # If the cell is not blank
            masslist_id = str(cell.value)
            if masslist_id.startswith('FL'):
                link = f"http://metabolomics.jp/wiki/{masslist_id}"
            else:
                link = f"https://www.npatlas.org/explore/compounds/{masslist_id}"
            cell.hyperlink = link
            cell.value = masslist_id  # Keeps the text the same as the original ID
            cell.style = "Hyperlink"  # Apply hyperlink style for consistent formatting

    # Set specific column widths
    column_widths = {
        'A': 15,
        'B': 15,
        'C': 18,
        'G': 18,
        'H': 15,
        'I': 15,
        'J': 18,
        'K': 20,
        'L': 18,
        'M': 15
    }

    for column, width in column_widths.items():
        sheet.column_dimensions[column].width = width

    # Define the fills for the alternating colors
    light_blue_fill = PatternFill(start_color="ADD8E6", end_color="ADD8E6", fill_type="solid")  # Light Blue
    light_yellow_fill = PatternFill(start_color="FFFFE0", end_color="FFFFE0", fill_type="solid")  # Light Yellow

    # Format the column titles
    for col in range(1, sheet.max_column + 1):
        cell = sheet.cell(row=1, column=col)
        cell.font = Font(bold=True)  # Make text bold

        # Apply alternating fills
        if col % 2 == 0:
            cell.fill = light_yellow_fill
        else:
            cell.fill = light_blue_fill

    # Center the title for column B
    sheet.cell(row=1, column=2).alignment = Alignment(horizontal='center')
    sheet.cell(row=1, column=11).alignment = Alignment(horizontal='center')
    sheet.cell(row=1, column=12).alignment = Alignment(horizontal='center')
    sheet.cell(row=1, column=13).alignment = Alignment(horizontal='center')

    # Center all cells in the entire worksheet, except for column B's entries
    for row in sheet.iter_rows():
        for cell in row:
            if cell.column in [2, 11, 12, 13] and cell.row > 1:  # For column B entries (skip header)
                cell.alignment = Alignment(horizontal='left')  # Left-align column B entries
            else:
                cell.alignment = Alignment(horizontal='center')  # Center align all other cells

    new_sheet = workbook.create_sheet("Structures")
    for i, cell in enumerate(sheet['N'], start=1):
        new_sheet[f'A{i}'] = cell.value  # Copy value to new sheet

    sheet.delete_cols(14)

    return workbook



    