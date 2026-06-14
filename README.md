# Encryption-Decryption Web Application with Custom Cipher Builder

An interactive classical cryptography laboratory web application designed for students of BS Computer Science studying **Essentials of Information Security**.

This platform allows users to learn, visualize, compare, and test classical ciphers (Caesar, Playfair, Hill, Columnar, Rail Fence) and create their own custom monoalphabetic substitution ciphers.

---

## 🛠️ Project Structure

```text
EncryptionProject/
│
├── app.py                      # Main Flask application controller
├── database.py                 # PyMySQL connection and schema auto-creation
├── requirements.txt            # Python packages dependencies list
│
├── ciphers/                    # Separate module directory for ciphers
│   ├── caesar.py               # Caesar cipher encryption/decryption + steps
│   ├── playfair.py             # Playfair cipher grid-based shift + steps
│   ├── hill.py                 # Hill cipher 2x2 matrix operations + steps
│   ├── columnar.py             # Columnar transposition sorting + steps
│   ├── railfence.py            # Rail fence zig-zag transposition + steps
│   └── custom_cipher.py        # Custom monoalphabetic substitution ciphers
│
├── templates/                  # Jinja2 HTML pages templates
│   ├── base.html               # Main layout page structure
│   ├── index.html              # Landing page
│   ├── login.html              # Login form
│   ├── register.html           # Registration form
│   ├── dashboard.html          # User dashboard and stats
│   ├── encrypt.html            # Encryption lab interface + visual steps
│   ├── decrypt.html            # Decryption lab interface + visual steps
│   ├── history.html            # Activity log, search, filter, CSV exports
│   ├── custom_cipher.html      # Custom alphabet designer lab
│   ├── comparison.html         # Tabular comparison of ciphers
│   ├── profile.html            # User profile and password updating
│   └── quiz.html               # 10 MCQ interactive learning quiz
│
├── static/                     # CSS & JS assets
│   ├── css/
│   │   └── style.css           # Styling with Dark Mode variables support
│   └── js/
│       └── script.js           # Client-side form styling & UI helpers
│
└── database/
    └── cryptography_db.sql     # Database backup SQL script
```

---

## 🚀 Setup Guide for Kali Linux + XAMPP

Follow these steps to deploy and run this application on a Kali Linux environment running XAMPP.

### Step 1: Start XAMPP Services
Open a terminal in Kali Linux and start Apache and MySQL services:
```bash
sudo /opt/lampp/lampp start
```
*Alternatively, if you installed standalone services, run:*
```bash
sudo systemctl start apache2
sudo systemctl start mysql
```

### Step 2: Set Up Python Virtual Environment (Kali Linux PEP 668)
Modern Debian-based systems (like Kali Linux) restrict global pip installations. We use a virtual environment to manage dependencies:

1. Navigate to the project directory:
   ```bash
   cd "/path/to/Cipher_project"
   ```
2. Create a virtual environment:
   ```bash
   python3 -m venv venv
   ```
3. Activate the virtual environment:
   ```bash
   source venv/bin/activate
   ```
4. Install requirements:
   ```bash
   pip install -r requirements.txt
   ```

### Step 3: Database Setup
The application is designed to **automatically initialize the database** and its tables upon startup. It will:
1. Connect to MySQL (`localhost` on port 3306, user `root`, empty password).
2. Create the database `cryptography_db` if it doesn't exist.
3. Generate all tables (`users`, `cipher_records`, `custom_ciphers`, `favorites`).
4. Seed the admin demo account (`admin` / `admin123`).

*Manual Import Option:*
If you prefer importing it manually, navigate to `http://localhost/phpmyadmin` in your browser, create a database named `cryptography_db`, and import the file located at `database/cryptography_db.sql`.

### Step 4: Run the Application
Start the Flask development server:
```bash
python3 app.py
```

Open your web browser and navigate to:
```text
http://localhost:5000
```

---

## 🔑 Administrative Demo Account
For testing and evaluations, you can log in with the default seeded administrator account:
- **Username:** `admin`
- **Password:** `admin123`

The administrator account has access to the **Admin Control Panel** to view, filter, and manage encryption records from all registered users on the system.

---


