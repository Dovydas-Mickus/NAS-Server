from flask import Flask, render_template, session, request, redirect, url_for, send_from_directory, jsonify, abort, send_file
import os
import mysql.connector
import auth
import ssl
from database import add_file, get_files, get_file_by_id, create_tables_if_not_exists, add_user, get_files_with_owner_names, delete_file
from argon2 import PasswordHasher

app = Flask(__name__)
app.config['SECRET_KEY'] = '1234'

UPLOAD_FOLDER = 'uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
ph = PasswordHasher()

# <-----Logging routes----->

@app.route('/login_attempt', methods=['GET', 'POST'])
def login_attempt():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        
        # Call the login_attempt function from auth.py
        user = auth.login_attempt(email, password)

        if user:
            # If user exists and password is correct, set the session
            session['user_id'] = user['id']
            return redirect(url_for('home'))
        else:
            return "Invalid username or password", 401

    return render_template('login.html')  # Render a login page


@app.route('/login')
def login():
    if(auth.check_session(session, request)):
        return redirect(url_for('home'))
    return render_template('login.html')
    
@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))
    
# <-----End of Logging routes----->

@app.route('/new_file')
def new_file():
    return render_template('new_file_page.html')

@app.route('/')
def home():
    if not auth.check_session(session, request):
        return redirect(url_for('login')) 
    files = get_files_with_owner_names()
    return render_template('index.html', files=files)

@app.route('/cert')
def cert():
    return send_from_directory('', 'cert.pem')

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'files[]' not in request.files:
        return jsonify({'error': 'No file part in the request'}), 400

    files = request.files.getlist('files[]')  # Retrieve the list of files
    print(request.files)

    if not files:
        return jsonify({'error': 'No files selected for uploading'}), 400

    uploaded_files = []
    
    try:
        for file in files:
            if file.filename == '':
                continue  # Skip empty filenames

            # Save each file to the upload folder
            file_path = os.path.join(UPLOAD_FOLDER, file.filename)
            file.save(file_path)

            # Assuming you have a function to add the file to your database
            add_file(
                name=file.filename,
                path=file_path,
                is_directory=False,
                owner_id=session['user_id'],  # Replace with actual user ID from session
                size=os.path.getsize(file_path)
            )

            uploaded_files.append(file.filename)

        return jsonify({'message': f'Successfully uploaded {len(uploaded_files)} file(s)', 'files': uploaded_files}), 200

    except Exception as e:
        return jsonify({'error': f'Error saving files: {str(e)}'}), 500

@app.route('/download/<int:file_id>')
def download_file(file_id):
    file = get_file_by_id(file_id)
    if not file:
        abort(404)
    
    file_path = file['path']

    if not os.path.exists(file_path):
        abort(404)

    return send_file(file_path, as_attachment=True, download_name=file['name'])


@app.route('/delete-file/<int:file_id>', methods=['GET'])
def delete_file_get(file_id):
    """
    Flask route to delete a file via a link.
    """
    result = delete_file(file_id)
    if result["success"]:
        message = result["message"]
        # Redirect back to the files page with a success message
        return redirect(url_for('home'))
    else:
        message = result["message"]
        # Redirect back to the files page with an error message
        return redirect(url_for('home'))


if __name__ == '__main__':
    create_tables_if_not_exists()
    app.run(host="0.0.0.0", port=8000, debug=True)

