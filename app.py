import io
import csv
from datetime import datetime
from functools import wraps
from flask import Flask, render_template, request, redirect, url_for, session, flash, Response, make_response
import pymysql

# Import database module and ciphers
import database
from ciphers import caesar, playfair, hill, columnar, railfence, custom_cipher

app = Flask(__name__)
app.secret_key = 'super_secret_session_key_for_classical_ciphers_project'

# Initialize database tables and seed admin user on startup
try:
    database.init_db()
except Exception as e:
    print(f"\n[WARNING] Database initialization failed: {e}")
    print("[WARNING] Please check if XAMPP is running, then restart the Flask server.\n")

# Route login decorator
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash("Please log in to access this page.", "warning")
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

# Route admin decorator
def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash("Please log in to access this page.", "warning")
            return redirect(url_for('login'))
        if session.get('username') != 'admin':
            flash("Access denied. Administrator privileges required.", "danger")
            return redirect(url_for('dashboard'))
        return f(*args, **kwargs)
    return decorated_function

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if 'user_id' in session:
        return redirect(url_for('dashboard'))
        
    if request.method == 'POST':
        fullname = request.form.get('fullname', '').strip()
        username = request.form.get('username', '').strip()
        email = request.form.get('email', '').strip()
        password = request.form.get('password', '')
        confirm_password = request.form.get('confirm_password', '')
        
        # Simple inputs validation
        if not fullname or not username or not email or not password:
            flash("All fields are required.", "danger")
            return render_template('register.html')
            
        if password != confirm_password:
            flash("Passwords do not match.", "danger")
            return render_template('register.html')
            
        # Check password hash and generate
        from werkzeug.security import generate_password_hash
        hashed_password = generate_password_hash(password)
        
        # Insert user to database
        try:
            conn = database.get_connection()
            with conn.cursor() as cursor:
                # Check if username or email already exists
                cursor.execute("SELECT id FROM users WHERE username = %s OR email = %s", (username, email))
                existing_user = cursor.fetchone()
                
                if existing_user:
                    flash("Username or Email already registered.", "danger")
                    conn.close()
                    return render_template('register.html')
                    
                cursor.execute("""
                    INSERT INTO users (fullname, username, email, password)
                    VALUES (%s, %s, %s, %s)
                """, (fullname, username, email, hashed_password))
            conn.commit()
            conn.close()
            
            flash("Registration successful! Please login.", "success")
            return redirect(url_for('login'))
            
        except pymysql.MySQLError as e:
            flash(f"Database error occurred: {e}", "danger")
            return render_template('register.html')
            
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if 'user_id' in session:
        return redirect(url_for('dashboard'))
        
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '')
        
        if not username or not password:
            flash("Please fill in all fields.", "danger")
            return render_template('login.html')
            
        try:
            conn = database.get_connection()
            with conn.cursor() as cursor:
                cursor.execute("SELECT * FROM users WHERE username = %s", (username,))
                user = cursor.fetchone()
            conn.close()
            
            if user:
                from werkzeug.security import check_password_hash
                if check_password_hash(user['password'], password):
                    # Set session
                    session['user_id'] = user['id']
                    session['username'] = user['username']
                    session['fullname'] = user['fullname']
                    flash(f"Welcome back, {user['fullname']}!", "success")
                    return redirect(url_for('dashboard'))
                    
            flash("Invalid username or password.", "danger")
            
        except pymysql.MySQLError as e:
            flash(f"Database error: {e}", "danger")
            
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.clear()
    flash("You have been logged out successfully.", "success")
    return redirect(url_for('index'))

@app.route('/dashboard')
@login_required
def dashboard():
    user_id = session['user_id']
    stats = {
        'total_records': 0,
        'total_enc': 0,
        'total_dec': 0,
        'total_custom': 0,
        'favorite_cipher': 'None',
        'most_used': 'None'
    }
    recent_records = []
    
    try:
        conn = database.get_connection()
        with conn.cursor() as cursor:
            # 1. Total records
            cursor.execute("SELECT COUNT(*) as count FROM cipher_records WHERE user_id = %s", (user_id,))
            stats['total_records'] = cursor.fetchone()['count']
            
            # 2. Total encryptions
            cursor.execute("SELECT COUNT(*) as count FROM cipher_records WHERE user_id = %s AND operation = 'encrypt'", (user_id,))
            stats['total_enc'] = cursor.fetchone()['count']
            
            # 3. Total decryptions
            cursor.execute("SELECT COUNT(*) as count FROM cipher_records WHERE user_id = %s AND operation = 'decrypt'", (user_id,))
            stats['total_dec'] = cursor.fetchone()['count']
            
            # 4. Total custom ciphers
            cursor.execute("SELECT COUNT(*) as count FROM custom_ciphers WHERE user_id = %s", (user_id,))
            stats['total_custom'] = cursor.fetchone()['count']
            
            # 5. Favorite Cipher
            cursor.execute("SELECT favorite_cipher FROM favorites WHERE user_id = %s ORDER BY id DESC LIMIT 1", (user_id,))
            fav = cursor.fetchone()
            if fav:
                stats['favorite_cipher'] = fav['favorite_cipher'].capitalize()
                
            # 6. Most used cipher
            cursor.execute("""
                SELECT cipher_type, COUNT(*) as cnt 
                FROM cipher_records 
                WHERE user_id = %s 
                GROUP BY cipher_type 
                ORDER BY cnt DESC LIMIT 1
            """, (user_id,))
            most = cursor.fetchone()
            if most:
                stats['most_used'] = most['cipher_type'].capitalize()
                
            # 7. Recent 5 records
            cursor.execute("""
                SELECT * FROM cipher_records 
                WHERE user_id = %s 
                ORDER BY id DESC LIMIT 5
            """, (user_id,))
            recent_records = cursor.fetchall()
            
        conn.close()
    except pymysql.MySQLError as e:
        flash(f"Error fetching stats: {e}", "danger")
        
    return render_template('dashboard.html', stats=stats, recent_records=recent_records)

@app.route('/encrypt', methods=['GET', 'POST'])
@login_required
def encrypt_page():
    user_id = session['user_id']
    custom_ciphers = []
    
    # Load custom ciphers for dropdown selection
    try:
        conn = database.get_connection()
        with conn.cursor() as cursor:
            cursor.execute("SELECT id, cipher_name, custom_alphabet FROM custom_ciphers WHERE user_id = %s", (user_id,))
            custom_ciphers = cursor.fetchall()
        conn.close()
    except pymysql.MySQLError as e:
        flash(f"Error loading custom ciphers: {e}", "danger")

    if request.method == 'POST':
        cipher_type = request.form.get('cipher_type')
        message = request.form.get('message', '')
        key = request.form.get('key', '')
        notes = request.form.get('notes', 'Testing')
        custom_cipher_id = request.form.get('custom_cipher_id')
        
        # Check if marking favorite
        if request.form.get('mark_favorite'):
            try:
                conn = database.get_connection()
                with conn.cursor() as cursor:
                    # Remove any existing favorite to keep only one favorite cipher
                    cursor.execute("DELETE FROM favorites WHERE user_id = %s", (user_id,))
                    cursor.execute("INSERT INTO favorites (user_id, favorite_cipher) VALUES (%s, %s)", (user_id, cipher_type))
                conn.commit()
                conn.close()
                flash(f"{cipher_type.capitalize()} Cipher marked as your favorite!", "success")
            except pymysql.MySQLError as e:
                flash(f"Database error: {e}", "danger")
            return redirect(url_for('encrypt_page', cipher_type=cipher_type))

        # Main Encryption execution
        result = ""
        steps = []
        actual_key_used = key
        
        try:
            if cipher_type == 'caesar':
                result, steps = caesar.encrypt(message, key)
            elif cipher_type == 'playfair':
                result, steps = playfair.encrypt(message, key)
            elif cipher_type == 'hill':
                result, steps = hill.encrypt(message, key)
            elif cipher_type == 'columnar':
                result, steps = columnar.encrypt(message, key)
            elif cipher_type == 'railfence':
                result, steps = railfence.encrypt(message, key)
            elif cipher_type == 'custom':
                if not custom_cipher_id:
                    raise ValueError("No custom cipher selected.")
                # Fetch custom alphabet
                conn = database.get_connection()
                with conn.cursor() as cursor:
                    cursor.execute("SELECT cipher_name, custom_alphabet FROM custom_ciphers WHERE id = %s AND user_id = %s", (custom_cipher_id, user_id))
                    c_cipher = cursor.fetchone()
                conn.close()
                if not c_cipher:
                    raise ValueError("Selected custom cipher not found.")
                
                actual_key_used = f"{c_cipher['cipher_name']} ({c_cipher['custom_alphabet']})"
                result, steps = custom_cipher.encrypt(message, c_cipher['custom_alphabet'])
            else:
                raise ValueError("Unknown cipher algorithm selected.")
                
            # Save transaction to database
            conn = database.get_connection()
            with conn.cursor() as cursor:
                cursor.execute("""
                    INSERT INTO cipher_records (user_id, message, result, cipher_type, operation, cipher_key, notes)
                    VALUES (%s, %s, %s, %s, %s, %s, %s)
                """, (user_id, message, result, cipher_type, 'encrypt', actual_key_used, notes))
                record_id = cursor.lastrowid
            conn.commit()
            conn.close()
            
            form_data = {
                'message': message,
                'cipher_type': cipher_type,
                'key': key,
                'notes': notes,
                'custom_cipher_id': custom_cipher_id
            }
            return render_template('encrypt.html', custom_ciphers=custom_ciphers, result=result, steps=steps, form_data=form_data, record_id=record_id)
            
        except Exception as e:
            flash(str(e), "danger")
            form_data = {
                'message': message,
                'cipher_type': cipher_type,
                'key': key,
                'notes': notes,
                'custom_cipher_id': custom_cipher_id
            }
            return render_template('encrypt.html', custom_ciphers=custom_ciphers, form_data=form_data)
            
    # GET Request: check if preselect is requested
    pre_cipher = request.args.get('cipher_type', 'caesar')
    pre_custom_id = request.args.get('custom_cipher_id', '')
    form_data = {'cipher_type': pre_cipher, 'custom_cipher_id': pre_custom_id, 'notes': 'Testing'}
    
    return render_template('encrypt.html', custom_ciphers=custom_ciphers, form_data=form_data)

@app.route('/decrypt', methods=['GET', 'POST'])
@login_required
def decrypt_page():
    user_id = session['user_id']
    custom_ciphers = []
    
    # Load custom ciphers for dropdown selection
    try:
        conn = database.get_connection()
        with conn.cursor() as cursor:
            cursor.execute("SELECT id, cipher_name, custom_alphabet FROM custom_ciphers WHERE user_id = %s", (user_id,))
            custom_ciphers = cursor.fetchall()
        conn.close()
    except pymysql.MySQLError as e:
        flash(f"Error loading custom ciphers: {e}", "danger")

    if request.method == 'POST':
        cipher_type = request.form.get('cipher_type')
        message = request.form.get('message', '') # Ciphertext input
        key = request.form.get('key', '')
        notes = request.form.get('notes', 'Testing')
        custom_cipher_id = request.form.get('custom_cipher_id')
        
        # Check if marking favorite
        if request.form.get('mark_favorite'):
            try:
                conn = database.get_connection()
                with conn.cursor() as cursor:
                    cursor.execute("DELETE FROM favorites WHERE user_id = %s", (user_id,))
                    cursor.execute("INSERT INTO favorites (user_id, favorite_cipher) VALUES (%s, %s)", (user_id, cipher_type))
                conn.commit()
                conn.close()
                flash(f"{cipher_type.capitalize()} Cipher marked as your favorite!", "success")
            except pymysql.MySQLError as e:
                flash(f"Database error: {e}", "danger")
            return redirect(url_for('decrypt_page', cipher_type=cipher_type))

        # Main Decryption execution
        result = ""
        steps = []
        actual_key_used = key
        
        try:
            if cipher_type == 'caesar':
                result, steps = caesar.decrypt(message, key)
            elif cipher_type == 'playfair':
                result, steps = playfair.decrypt(message, key)
            elif cipher_type == 'hill':
                result, steps = hill.decrypt(message, key)
            elif cipher_type == 'columnar':
                result, steps = columnar.decrypt(message, key)
            elif cipher_type == 'railfence':
                result, steps = railfence.decrypt(message, key)
            elif cipher_type == 'custom':
                if not custom_cipher_id:
                    raise ValueError("No custom cipher selected.")
                # Fetch custom alphabet
                conn = database.get_connection()
                with conn.cursor() as cursor:
                    cursor.execute("SELECT cipher_name, custom_alphabet FROM custom_ciphers WHERE id = %s AND user_id = %s", (custom_cipher_id, user_id))
                    c_cipher = cursor.fetchone()
                conn.close()
                if not c_cipher:
                    raise ValueError("Selected custom cipher not found.")
                
                actual_key_used = f"{c_cipher['cipher_name']} ({c_cipher['custom_alphabet']})"
                result, steps = custom_cipher.decrypt(message, c_cipher['custom_alphabet'])
            else:
                raise ValueError("Unknown cipher algorithm selected.")
                
            # Save transaction to database
            conn = database.get_connection()
            with conn.cursor() as cursor:
                cursor.execute("""
                    INSERT INTO cipher_records (user_id, message, result, cipher_type, operation, cipher_key, notes)
                    VALUES (%s, %s, %s, %s, %s, %s, %s)
                """, (user_id, message, result, cipher_type, 'decrypt', actual_key_used, notes))
                record_id = cursor.lastrowid
            conn.commit()
            conn.close()
            
            form_data = {
                'message': message,
                'cipher_type': cipher_type,
                'key': key,
                'notes': notes,
                'custom_cipher_id': custom_cipher_id
            }
            return render_template('decrypt.html', custom_ciphers=custom_ciphers, result=result, steps=steps, form_data=form_data, record_id=record_id)
            
        except Exception as e:
            flash(str(e), "danger")
            form_data = {
                'message': message,
                'cipher_type': cipher_type,
                'key': key,
                'notes': notes,
                'custom_cipher_id': custom_cipher_id
            }
            return render_template('decrypt.html', custom_ciphers=custom_ciphers, form_data=form_data)
            
    # GET Request: check if preselect is requested
    pre_cipher = request.args.get('cipher_type', 'caesar')
    pre_custom_id = request.args.get('custom_cipher_id', '')
    form_data = {'cipher_type': pre_cipher, 'custom_cipher_id': pre_custom_id, 'notes': 'Testing'}
    
    return render_template('decrypt.html', custom_ciphers=custom_ciphers, form_data=form_data)

@app.route('/custom-cipher-lab', methods=['GET', 'POST'])
@login_required
def custom_cipher_lab():
    user_id = session['user_id']
    edit_cipher = None
    
    # Check if we are loading an existing cipher for editing
    edit_id = request.args.get('edit')
    if edit_id:
        try:
            conn = database.get_connection()
            with conn.cursor() as cursor:
                cursor.execute("SELECT * FROM custom_ciphers WHERE id = %s AND user_id = %s", (edit_id, user_id))
                edit_cipher = cursor.fetchone()
            conn.close()
        except pymysql.MySQLError as e:
            flash(f"Error loading cipher for editing: {e}", "danger")

    if request.method == 'POST':
        cipher_name = request.form.get('cipher_name', '').strip()
        custom_alphabet = request.form.get('custom_alphabet', '').upper().strip()
        cipher_id = request.form.get('cipher_id') # Present if editing
        
        try:
            # Validate custom alphabet sequence using cipher module method
            cleaned_alphabet = custom_cipher.validate_custom_alphabet(custom_alphabet)
            
            conn = database.get_connection()
            with conn.cursor() as cursor:
                if cipher_id:
                    # Update operation
                    cursor.execute("""
                        UPDATE custom_ciphers 
                        SET cipher_name = %s, custom_alphabet = %s 
                        WHERE id = %s AND user_id = %s
                    """, (cipher_name, cleaned_alphabet, cipher_id, user_id))
                    flash("Custom cipher updated successfully!", "success")
                else:
                    # Insert operation
                    cursor.execute("""
                        INSERT INTO custom_ciphers (user_id, cipher_name, custom_alphabet)
                        VALUES (%s, %s, %s)
                    """, (user_id, cipher_name, cleaned_alphabet))
                    flash("Custom cipher saved to library!", "success")
            conn.commit()
            conn.close()
            return redirect(url_for('custom_cipher_lab'))
            
        except Exception as e:
            flash(str(e), "danger")

    # Load all user custom ciphers
    saved_ciphers = []
    try:
        conn = database.get_connection()
        with conn.cursor() as cursor:
            cursor.execute("SELECT * FROM custom_ciphers WHERE user_id = %s ORDER BY id DESC", (user_id,))
            saved_ciphers = cursor.fetchall()
        conn.close()
    except pymysql.MySQLError as e:
        flash(f"Error loading ciphers library: {e}", "danger")
        
    return render_template('custom_cipher.html', saved_ciphers=saved_ciphers, edit_cipher=edit_cipher)

@app.route('/delete-custom-cipher/<int:cipher_id>', methods=['POST'])
@login_required
def delete_custom_cipher(cipher_id):
    user_id = session['user_id']
    try:
        conn = database.get_connection()
        with conn.cursor() as cursor:
            cursor.execute("DELETE FROM custom_ciphers WHERE id = %s AND user_id = %s", (cipher_id, user_id))
        conn.commit()
        conn.close()
        flash("Custom cipher deleted from library.", "info")
    except pymysql.MySQLError as e:
        flash(f"Error deleting custom cipher: {e}", "danger")
    return redirect(url_for('custom_cipher_lab'))

@app.route('/delete-record/<int:record_id>', methods=['POST'])
@login_required
def delete_record(record_id):
    user_id = session['user_id']
    is_admin = session.get('username') == 'admin'
    
    try:
        conn = database.get_connection()
        with conn.cursor() as cursor:
            if is_admin:
                cursor.execute("DELETE FROM cipher_records WHERE id = %s", (record_id,))
            else:
                cursor.execute("DELETE FROM cipher_records WHERE id = %s AND user_id = %s", (record_id, user_id))
        conn.commit()
        conn.close()
        flash("Record deleted from history log.", "info")
    except pymysql.MySQLError as e:
        flash(f"Error deleting record: {e}", "danger")
        
    if is_admin and request.referrer and 'admin' in request.referrer:
        return redirect(url_for('admin_dashboard'))
    return redirect(url_for('history_page'))

@app.route('/history')
@login_required
def history_page():
    user_id = session['user_id']
    
    # Get filters from request query parameters
    search = request.args.get('search', '').strip()
    cipher_type = request.args.get('cipher_type', '')
    operation = request.args.get('operation', '')
    date = request.args.get('date', '')
    
    records = []
    
    try:
        conn = database.get_connection()
        with conn.cursor() as cursor:
            # Build dynamic parameterized SQL query
            query = "SELECT * FROM cipher_records WHERE user_id = %s"
            params = [user_id]
            
            if search:
                query += " AND (message LIKE %s OR result LIKE %s)"
                params.extend([f"%{search}%", f"%{search}%"])
                
            if cipher_type:
                query += " AND cipher_type = %s"
                params.append(cipher_type)
                
            if operation:
                query += " AND operation = %s"
                params.append(operation)
                
            if date:
                # Format dates to match DATE format in SQL
                query += " AND DATE(created_at) = %s"
                params.append(date)
                
            query += " ORDER BY id DESC"
            cursor.execute(query, params)
            records = cursor.fetchall()
            
        conn.close()
    except pymysql.MySQLError as e:
        flash(f"Error querying history: {e}", "danger")
        
    filters = {
        'search': search,
        'cipher_type': cipher_type,
        'operation': operation,
        'date': date
    }
    return render_template('history.html', records=records, filters=filters)

@app.route('/export-history')
@login_required
def export_history():
    user_id = session['user_id']
    try:
        conn = database.get_connection()
        with conn.cursor() as cursor:
            cursor.execute("""
                SELECT id, cipher_type, operation, cipher_key, notes, message, result, created_at 
                FROM cipher_records 
                WHERE user_id = %s 
                ORDER BY id DESC
            """, (user_id,))
            records = cursor.fetchall()
        conn.close()
        
        # Build CSV file in memory
        output = io.StringIO()
        writer = csv.writer(output)
        
        # Write headers
        writer.writerow(['ID', 'Cipher Type', 'Operation', 'Cipher Key', 'Notes', 'Input Message', 'Output Result', 'Execution Date'])
        
        # Write data rows
        for r in records:
            writer.writerow([
                r['id'],
                r['cipher_type'],
                r['operation'],
                r['cipher_key'],
                r['notes'],
                r['message'],
                r['result'],
                r['created_at'].strftime('%Y-%m-%d %H:%M:%S')
            ])
            
        csv_data = output.getvalue()
        output.close()
        
        # Return response attachment
        response = Response(csv_data, mimetype='text/csv')
        response.headers.set("Content-Disposition", "attachment", filename=f"cipherforge_history_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv")
        return response
        
    except Exception as e:
        flash(f"Failed to export history: {e}", "danger")
        return redirect(url_for('history_page'))

@app.route('/download-result/<int:record_id>')
@login_required
def download_result(record_id):
    user_id = session['user_id']
    is_admin = session.get('username') == 'admin'
    
    try:
        conn = database.get_connection()
        with conn.cursor() as cursor:
            if is_admin:
                cursor.execute("SELECT * FROM cipher_records WHERE id = %s", (record_id,))
            else:
                cursor.execute("SELECT * FROM cipher_records WHERE id = %s AND user_id = %s", (record_id, user_id))
            record = cursor.fetchone()
        conn.close()
        
        if not record:
            flash("Record not found or access denied.", "danger")
            return redirect(url_for('dashboard'))
            
        # Generate result file content
        content = (
            "=============================================\n"
            "         CIPHERFORGE EXPERIMENT RECORD         \n"
            "=============================================\n"
            f"Record ID:   #{record['id']}\n"
            f"Algorithm:   {record['cipher_type'].upper()}\n"
            f"Operation:   {record['operation'].upper()}\n"
            f"Key Used:    {record['cipher_key']}\n"
            f"Notes:       {record['notes'] or 'N/A'}\n"
            f"Date/Time:   {record['created_at'].strftime('%Y-%m-%d %H:%M:%S')}\n"
            "---------------------------------------------\n"
            "INPUT MESSAGE:\n"
            f"{record['message']}\n"
            "---------------------------------------------\n"
            "OUTPUT RESULT:\n"
            f"{record['result']}\n"
            "=============================================\n"
        )
        
        response = make_response(content)
        response.headers["Content-Disposition"] = f"attachment; filename=cipher_result_{record['id']}.txt"
        response.headers["Content-Type"] = "text/plain"
        return response
        
    except pymysql.MySQLError as e:
        flash(f"Database error: {e}", "danger")
        return redirect(url_for('dashboard'))

@app.route('/comparison')
@login_required
def comparison_page():
    return render_template('comparison.html')

@app.route('/about')
@login_required
def about_page():
    return render_template('about.html')

@app.route('/quiz', methods=['GET', 'POST'])
@login_required
def quiz_page():
    score = None
    user_answers = None
    checked_answers = None
    
    if request.method == 'POST':
        # Correct keys
        correct_answers = {
            'q1': 'B', 'q2': 'C', 'q3': 'C', 'q4': 'C', 'q5': 'C',
            'q6': 'A', 'q7': 'B', 'q8': 'A', 'q9': 'B', 'q10': 'D'
        }
        
        user_answers = {}
        checked_answers = []
        score = 0
        
        for i in range(1, 11):
            key = f"q{i}"
            ans = request.form.get(key)
            user_answers[key] = ans
            
            if ans == correct_answers[key]:
                score += 1
                checked_answers.append(True)
            else:
                checked_answers.append(False)
                
    return render_template('quiz.html', score=score, user_answers=user_answers, checked_answers=checked_answers)

@app.route('/profile')
@login_required
def profile_page():
    user_id = session['user_id']
    user = None
    operation_count = 0
    
    try:
        conn = database.get_connection()
        with conn.cursor() as cursor:
            # Get user info
            cursor.execute("SELECT fullname, username, email, created_at FROM users WHERE id = %s", (user_id,))
            user = cursor.fetchone()
            
            # Get operation count
            cursor.execute("SELECT COUNT(*) as count FROM cipher_records WHERE user_id = %s", (user_id,))
            operation_count = cursor.fetchone()['count']
        conn.close()
    except pymysql.MySQLError as e:
        flash(f"Error fetching profile details: {e}", "danger")
        
    return render_template('profile.html', user=user, operation_count=operation_count)

@app.route('/change-password', methods=['POST'])
@login_required
def change_password():
    user_id = session['user_id']
    current_password = request.form.get('current_password', '')
    new_password = request.form.get('new_password', '')
    confirm_new_password = request.form.get('confirm_new_password', '')
    
    if new_password != confirm_new_password:
        flash("New passwords do not match.", "danger")
        return redirect(url_for('profile_page'))
        
    try:
        conn = database.get_connection()
        with conn.cursor() as cursor:
            cursor.execute("SELECT password FROM users WHERE id = %s", (user_id,))
            user = cursor.fetchone()
            
            if user:
                from werkzeug.security import check_password_hash, generate_password_hash
                if check_password_hash(user['password'], current_password):
                    hashed_pw = generate_password_hash(new_password)
                    cursor.execute("UPDATE users SET password = %s WHERE id = %s", (hashed_pw, user_id))
                    conn.commit()
                    flash("Password updated successfully!", "success")
                else:
                    flash("Current password entered is incorrect.", "danger")
            else:
                flash("User profile not found.", "danger")
        conn.close()
    except pymysql.MySQLError as e:
        flash(f"Database error: {e}", "danger")
        
    return redirect(url_for('profile_page'))

@app.route('/admin')
@admin_required
def admin_dashboard():
    stats = {
        'total_users': 0,
        'total_encryptions': 0,
        'total_decryptions': 0,
        'total_custom_ciphers': 0
    }
    records = []
    
    try:
        conn = database.get_connection()
        with conn.cursor() as cursor:
            # 1. Total users
            cursor.execute("SELECT COUNT(*) as count FROM users")
            stats['total_users'] = cursor.fetchone()['count']
            
            # 2. Total encryptions
            cursor.execute("SELECT COUNT(*) as count FROM cipher_records WHERE operation = 'encrypt'")
            stats['total_encryptions'] = cursor.fetchone()['count']
            
            # 3. Total decryptions
            cursor.execute("SELECT COUNT(*) as count FROM cipher_records WHERE operation = 'decrypt'")
            stats['total_decryptions'] = cursor.fetchone()['count']
            
            # 4. Total custom ciphers
            cursor.execute("SELECT COUNT(*) as count FROM custom_ciphers")
            stats['total_custom_ciphers'] = cursor.fetchone()['count']
            
            # 5. Get all user records with details
            cursor.execute("""
                SELECT cr.*, u.username, u.fullname 
                FROM cipher_records cr 
                JOIN users u ON cr.user_id = u.id 
                ORDER BY cr.id DESC
            """)
            records = cursor.fetchall()
        conn.close()
    except pymysql.MySQLError as e:
        flash(f"Admin stats error: {e}", "danger")
        
    return render_template('admin.html', stats=stats, records=records)

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
