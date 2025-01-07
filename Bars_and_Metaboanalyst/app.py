from flask import Flask, render_template, request, redirect, session, send_file, after_this_request
import pandas as pd
import os
import zipfile
import matplotlib.pyplot as plt
from rename_columns import detect_similar_columns, apply_column_renames
from filter_rows import filter_rows
from graph_maker import generate_graph


app = Flask(__name__)
app.secret_key = 'your_secret_key'  # Necessary for session handling
UPLOAD_FOLDER = 'uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/process', methods=['POST'])
def process_csv():
    if 'validated_data' not in request.files:
        return "No file part", 400

    file = request.files['validated_data']
    if file.filename == '':
        return "No selected file", 400

    if file and file.filename.endswith('.csv'):
        filepath = os.path.join(UPLOAD_FOLDER, file.filename)
        file.save(filepath)

        session['val_path'] = filepath

    if 'cd_data' not in request.files:
        return "No file part", 400

    file = request.files['cd_data']
    if file.filename == '':
        return "No selected file", 400

    if file and file.filename.endswith('.csv'):
        filepath = os.path.join(UPLOAD_FOLDER, file.filename)
        file.save(filepath)

        # Load the CSV to detect similar columns
        df = pd.read_csv(filepath)

        # Step 1: Clean the DataFrame
        names = df.Name
        df = df.loc[:, df.columns.str.startswith('Area')]
        df = df.loc[:, ~df.columns.str.contains('pool', case=False)]
        df = df.loc[:, ~df.columns.str.contains('blank', case=False)]
        df.insert(0, 'Name', names)

        # Save the cleaned DataFrame
        cleaned_path = os.path.join(UPLOAD_FOLDER, 'cleaned_' + file.filename)
        df.to_csv(cleaned_path, index=False)

        # Step 2: Detect similar columns
        similar_columns = detect_similar_columns(df.columns)

        # Save the original dataframe and path to the session
        session['cd_path'] = cleaned_path
        session['similar_columns'] = similar_columns

        return render_template('rename_columns.html', similar_columns=similar_columns)

    return "Invalid file format. Please upload a CSV file.", 400

@app.route('/rename', methods=['POST'])
def rename_columns():
    if 'cd_path' not in session or 'similar_columns' not in session or 'val_path' not in session:
        return "Session expired. Please upload the file again.", 400

    cd_path = session['cd_path']
    val_path = session['val_path']
    similar_columns = session['similar_columns']

    # Collect user-provided names for similar columns
    renames = {group: request.form[f'rename_{group}'] for group in similar_columns.keys()}

    # Apply the renames to the dataframe
    df = pd.read_csv(cd_path)
    cd_path = apply_column_renames(df, similar_columns, renames, cd_path)
    session['cd_path'] = cd_path

    cd_df = pd.read_csv(cd_path)
    val_df = pd.read_csv(val_path)
    dataframes = filter_rows(cd_df, val_df)
    sheet_names = ['QCs', 'No QCs', 'Flavonoid QCs', 'Flavonoid No QCs']
    # Define output Excel file path
    excel_path = os.path.join(UPLOAD_FOLDER, 'metaboanalyst_files.xlsx')
    with pd.ExcelWriter(excel_path, engine='openpyxl') as writer:
        for df, sheet_name in zip(dataframes, sheet_names):
            # Replace column names containing 'Unnamed' with empty strings
            df.columns = ["" if "Unnamed" in col else col for col in df.columns]
            df.to_excel(writer, sheet_name=sheet_name, index=False)

    # Generate graphs and workbook
    figures, workbook = generate_graph(val_path)

    # Save figures as PNGs
    zip_path = os.path.join(UPLOAD_FOLDER, 'graphs_and_data.zip')
    with zipfile.ZipFile(zip_path, 'w') as zipf:
        # Save figures to PNG and add to ZIP
        for i, fig in enumerate(figures):
            fig_path = os.path.join(UPLOAD_FOLDER, f'figure_{i+1}.png')
            fig.savefig(fig_path, dpi=300)
            plt.close(fig)
            zipf.write(fig_path, os.path.basename(fig_path))
            os.remove(fig_path)

        # Save workbook to Excel files and add to ZIP
        # Excel path is the original metaboanalyst stuff
        # Excel path 2 is just the bar graph data
        excel_path2 = os.path.join(UPLOAD_FOLDER, 'data_summary.xlsx')
        workbook.save(excel_path2)
        zipf.write(excel_path, os.path.basename(excel_path))
        zipf.write(excel_path2, os.path.basename(excel_path2))
        # Free up space
        os.remove(excel_path)
        os.remove(excel_path2)

    # Schedule files for deletion after the response
    @after_this_request
    def cleanup_files(response):
        try:
            os.remove(cd_path)  # Delete the original file
            os.remove(excel_path)  # Delete the updated file
            os.remove(val_path) # Delete validated path
        except Exception as e:
            app.logger.error(f"Error deleting files: {e}")
        return response

    # Automatically return the file as a download response
    return send_file(zip_path, as_attachment=True, download_name="graphing_files.zip")
    

if __name__ == '__main__':
    app.run(debug=True)

