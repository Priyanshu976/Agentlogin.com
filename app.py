from flask import Flask, request, render_template, redirect, url_for,flash
import pandas as pd
from werkzeug.utils import secure_filename
from datetime import datetime
import os

app = Flask(__name__, static_folder='static')
app.secret_key = 'your_secret_key'

# Path to the Excel file
EXCEL_FILE = "user_data.xlsx"

# Path to the Upload file
app.config['UPLOAD_FOLDER'] = os.path.join(os.getcwd(), 'uploads')

# Folder to save uploaded files
UPLOAD_FOLDER = 'uploads'
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

def load_user_data():
    return pd.read_excel('user_data.xlsx')

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/about')
def about():
    return render_template('aboutus.html')

@app.route('/contact')
def contact():
    return render_template('contactus.html')

@app.route('/signin')
def signin():
    return render_template('signin.html')

@app.route('/login', methods=['POST'])
def login():
    #form data
    username = request.form['username']
    password = request.form['password']

    #Load data
    try:
        df = pd.read_excel(EXCEL_FILE)
    except Exception as e:
        return f"Error reading Excel file: {e}"

    #username and password match
    user = df[(df['username'] == username) & (df['password'] == password)]
    
     # Load user data from the Excel sheet
    user_data = load_user_data()

    # Check if the username and password exist in the data
    user_row = user_data[(user_data['username'] == username) & (user_data['password'] == password)]
    
    if not user_row.empty:  # If a match is found
        user_info = user_row.iloc[0].to_dict()  # Convert row to a dictionary
        return render_template('dashboard.html', user_info=user_info)  # Pass user info to the template
        flash(f"Welcome,{user_info['Full Name']}!")
    else:
        flash("Invalid credentials(username or password). Please try again.")
        return redirect(url_for('signin'))

# Folder to save uploaded files
UPLOAD_FOLDER = 'uploads'
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

@app.route('/dashboard/<username>', methods=['GET'])
def dashboard(username):

    # Pass user details to the dashboard
    user_data = load_user_data()
    user_row = user_data[user_data['username'] == username]
    if not user_row.empty:
        user_info = user_row.iloc[0].to_dict()
        return render_template('dashboard.html', user_info=user_info)
    else:
        flash("User not found.", "error")
        return redirect(url_for('home'))

# @app.route('/dashboard', methods=['GET'])
# def dashboard():
#     if 'username' not in session:  # Check if the user is logged in
#         flash("Access denied. Please log in.", "error")
#         return redirect(url_for('signin'))  # Redirect to the sign-in page

#     # If logged in, fetch user details and render the dashboard
#     username = session['username']  # Retrieve the username from the session
#     user_data = load_user_data()
#     user_row = user_data[user_data['Username'] == username]
#     if not user_row.empty:
#         user_info = user_row.iloc[0].to_dict()
#         return render_template('dashboard.html', user_info=user_info)
#     else:
#         flash("User not found.", "error")
#         return redirect(url_for('home'))



@app.route('/submit_report', methods=['POST'])
def submit_report():
    username = request.form['username']  # Username passed as a hidden input
    report_text = request.form['report']
    file = request.files['file']
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    # Save file if uploaded
    if file and file.filename != '':
        filename = secure_filename(file.filename)
        file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
    else:
        filename = None

    # Save report details to an Excel sheet
    data = {
        "username": [username],
        "Report": [report_text],
        "Document": [filename],
        "Timestamp": [timestamp]
    }
    df = pd.DataFrame(data)

    # Append to existing Excel file or create a new one
    excel_file = 'report_data.xlsx'
    if os.path.exists(excel_file):
        existing_df = pd.read_excel(excel_file)
        df = pd.concat([existing_df, df], ignore_index=True)
    df.to_excel(excel_file, index=False)

    flash("Report submitted successfully!", "success")
    return redirect(url_for('dashboard', username=username))

@app.route('/logout')
def logout():
    session.clear()  # Clear all session data
    flash("You have been logged out.", "success")
    return redirect(url_for('signin'))

@app.after_request
def add_cache_headers(response):
    response.headers['Cache-Control'] = 'no-store, no-cache, must-revalidate, post-check=0, pre-check=0, max-age=0'
    response.headers['Pragma'] = 'no-cache'
    response.headers['Expires'] = '1'
    return response




if __name__ == "__main__":
    app.run(debug=True)
