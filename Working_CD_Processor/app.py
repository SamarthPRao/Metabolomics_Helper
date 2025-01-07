from flask import Flask, render_template, request, redirect, session, send_file, after_this_request
import os
from processor import process_files

app = Flask(__name__)
app.secret_key = 'your_secret_key'  # Necessary for session handling
UPLOAD_FOLDER = 'uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/process', methods=['POST'])
def process_csv():
    required_files = ['cs_data', 'mz_data', 'ml_data', 'database']

    # Check if all required files are in the request
    missing_files = [file for file in required_files if file not in request.files]
    if missing_files:
        return f"Missing files: {', '.join(missing_files)}", 400

    # Process each file and check if the filename is valid
    uploaded_files = {}
    for file_key in required_files:
        file = request.files[file_key]
        
        # Check if the file is empty
        if file.filename == '':
            return f"No selected file for {file_key}", 400

        # Check if the file has the correct extension
        if file and file.filename.endswith('.xlsx'):
            filepath = os.path.join(UPLOAD_FOLDER, file.filename)
            file.save(filepath)
            uploaded_files[file_key] = filepath
        else:
            return f"Invalid file type for {file_key}. Only XLSX files are allowed.", 400

    # You can now access the file paths from the `uploaded_files` dictionary
    cs_filepath = uploaded_files.get('cs_data')
    mz_filepath = uploaded_files.get('mz_data')
    ml_filepath = uploaded_files.get('ml_data')
    database_filepath = uploaded_files.get('database')

    # Generate graphs and workbook
    workbook = process_files(cs_filepath, mz_filepath, ml_filepath, database_filepath)

    # Save Workbook
    output_path = os.path.join(UPLOAD_FOLDER, 'output.xlsx')
    workbook.save(output_path)

    @after_this_request
    def cleanup(response):
        # Clean up uploaded files
        for filepath in uploaded_files.values():
            try:
                os.remove(filepath)
            except Exception as e:
                print(f"Error removing uploaded file {filepath}: {e}")

        # Clean up the output file
        try:
            os.remove(output_path)
        except Exception as e:
            print(f"Error removing output file {output_path}: {e}")
        
        return response

    return send_file(output_path, as_attachment=True, download_name="output.xlsx")

if __name__ == '__main__':
    app.run(debug=True)
