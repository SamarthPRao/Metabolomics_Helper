from flask import Flask, request
import pandas as pd

app = Flask(__name__)

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return "No file part in the request", 400

    file = request.files['file']
    if file.filename == '':
        return "No file selected", 400

    # Read the CSV file
    try:
        df = pd.read_csv(file)
        print("Columns in the uploaded CSV file:")
        print(df.columns.tolist())
        return "File uploaded successfully. Check your console for the column names.", 200
    except Exception as e:
        print(f"Error: {e}")
        return "Error processing the file. Make sure it is a valid CSV.", 400

if __name__ == '__main__':
    app.run(debug=True)