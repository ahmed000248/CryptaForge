import pymysql
from werkzeug.security import generate_password_hash

DB_HOST = 'localhost'
DB_USER = 'root'
DB_PASSWORD = ''
DB_NAME = 'cryptography_db'

def get_connection(with_db=True):
    """
    Establishes and returns a PyMySQL connection.
    If with_db is True, it connects directly to cryptography_db.
    If MySQL server is not running or credentials are wrong, raises connection error.
    """
    try:
        if with_db:
            return pymysql.connect(
                host=DB_HOST,
                user=DB_USER,
                password=DB_PASSWORD,
                database=DB_NAME,
                cursorclass=pymysql.cursors.DictCursor
            )
        else:
            return pymysql.connect(
                host=DB_HOST,
                user=DB_USER,
                password=DB_PASSWORD,
                cursorclass=pymysql.cursors.DictCursor
            )
    except pymysql.MySQLError as e:
        print(f"\n[ERROR] Could not connect to MySQL server: {e}")
        print("[INSTRUCTION] Please ensure XAMPP (Apache & MySQL) is running.\n")
        raise e

def init_db():
    """
    Initializes the database:
    1. Creates the cryptography_db database if it doesn't exist.
    2. Creates the necessary tables (users, cipher_records, custom_ciphers, favorites).
    3. Seeds the admin account (username: admin, password: admin123) if not present.
    """
    # Step 1: Connect to server without database to create it
    conn = get_connection(with_db=False)
    try:
        with conn.cursor() as cursor:
            cursor.execute(f"CREATE DATABASE IF NOT EXISTS {DB_NAME}")
        conn.commit()
    finally:
        conn.close()

    # Step 2: Connect to the database to create tables
    conn = get_connection(with_db=True)
    try:
        with conn.cursor() as cursor:
            # Create users table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS users (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    fullname VARCHAR(100) NOT NULL,
                    username VARCHAR(50) NOT NULL UNIQUE,
                    email VARCHAR(100) NOT NULL UNIQUE,
                    password VARCHAR(255) NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
            """)

            # Create cipher_records table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS cipher_records (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    user_id INT NOT NULL,
                    message TEXT NOT NULL,
                    result TEXT NOT NULL,
                    cipher_type VARCHAR(50) NOT NULL,
                    operation VARCHAR(10) NOT NULL,
                    cipher_key VARCHAR(255) NOT NULL,
                    notes TEXT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
                ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
            """)

            # Create custom_ciphers table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS custom_ciphers (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    user_id INT NOT NULL,
                    cipher_name VARCHAR(100) NOT NULL,
                    normal_alphabet VARCHAR(26) DEFAULT 'ABCDEFGHIJKLMNOPQRSTUVWXYZ',
                    custom_alphabet VARCHAR(26) NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
                ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
            """)

            # Create favorites table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS favorites (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    user_id INT NOT NULL,
                    favorite_cipher VARCHAR(50) NOT NULL,
                    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
                ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
            """)

            # Step 3: Seed Admin account if it does not exist
            cursor.execute("SELECT id FROM users WHERE username = 'admin'")
            admin_user = cursor.fetchone()
            if not admin_user:
                hashed_pw = generate_password_hash('admin123')
                cursor.execute("""
                    INSERT INTO users (fullname, username, email, password)
                    VALUES (%s, %s, %s, %s)
                """, ("Administrator", "admin", "admin@cryptography.local", hashed_pw))
                print("[INFO] Seeded admin demo account (admin / admin123)")

        conn.commit()
    finally:
        conn.close()
