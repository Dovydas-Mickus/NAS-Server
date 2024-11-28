import mysql.connector
from mysql.connector import Error
from datetime import datetime
import os

conn = mysql.connector.connect(
        host="localhost",
        port=3306,
        user="root",
        database="nas_server"
    )


def create_tables_if_not_exists():
    cursor = conn.cursor()
    try:
        # List of table creation queries
        queries = [
            """
            CREATE TABLE IF NOT EXISTS users (
                id INT AUTO_INCREMENT PRIMARY KEY,
                username VARCHAR(100) NOT NULL UNIQUE,
                email VARCHAR(255) NOT NULL UNIQUE,
                password_hash VARCHAR(255) NOT NULL,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP
            );
            """,
            """
            CREATE TABLE IF NOT EXISTS `groups` (
                id INT AUTO_INCREMENT PRIMARY KEY,
                name VARCHAR(255) NOT NULL UNIQUE,
                description TEXT,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP
            );
            """,
            """
            CREATE TABLE IF NOT EXISTS folders (
                id INT AUTO_INCREMENT PRIMARY KEY,
                name VARCHAR(255) NOT NULL,
                parent_id INT,
                user_id INT NOT NULL,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (parent_id) REFERENCES folders(id),
                FOREIGN KEY (user_id) REFERENCES users(id)
            );
            """,
            """
            CREATE TABLE IF NOT EXISTS files (
                id INT AUTO_INCREMENT PRIMARY KEY,
                name VARCHAR(255) NOT NULL UNIQUE,  -- Ensures the name is unique
                path TEXT NOT NULL,
                is_directory BOOLEAN DEFAULT FALSE NOT NULL,
                owner_id INT NOT NULL,
                size BIGINT DEFAULT 0,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
                folder_id INT,
                FOREIGN KEY (owner_id) REFERENCES users(id),
                FOREIGN KEY (folder_id) REFERENCES folders(id)
            );
            """,
            """
            CREATE TABLE IF NOT EXISTS folder_permissions (
                id INT AUTO_INCREMENT PRIMARY KEY,
                folder_id INT NOT NULL,
                user_id INT,
                group_id INT,
                can_read BOOLEAN DEFAULT FALSE,
                can_write BOOLEAN DEFAULT FALSE,
                can_delete BOOLEAN DEFAULT FALSE,
                FOREIGN KEY (folder_id) REFERENCES folders(id),
                FOREIGN KEY (user_id) REFERENCES users(id),
                FOREIGN KEY (group_id) REFERENCES `groups`(id)
            );
            """,
            """
            CREATE TABLE IF NOT EXISTS group_members (
                id INT AUTO_INCREMENT PRIMARY KEY,
                group_id INT NOT NULL,
                user_id INT NOT NULL,
                joined_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (group_id) REFERENCES `groups`(id),
                FOREIGN KEY (user_id) REFERENCES users(id)
            );
            """,
            """
            CREATE TABLE IF NOT EXISTS group_permissions (
                id INT AUTO_INCREMENT PRIMARY KEY,
                group_id INT NOT NULL,
                file_id INT NOT NULL,
                can_read BOOLEAN DEFAULT FALSE,
                can_write BOOLEAN DEFAULT FALSE,
                can_delete BOOLEAN DEFAULT FALSE,
                FOREIGN KEY (group_id) REFERENCES `groups`(id),
                FOREIGN KEY (file_id) REFERENCES files(id)
            );
            """,
            """
            CREATE TABLE IF NOT EXISTS permissions (
                id INT AUTO_INCREMENT PRIMARY KEY,
                file_id INT NOT NULL,
                user_id INT NOT NULL,
                can_read BOOLEAN DEFAULT FALSE,
                can_write BOOLEAN DEFAULT FALSE,
                can_delete BOOLEAN DEFAULT FALSE,
                FOREIGN KEY (file_id) REFERENCES files(id),
                FOREIGN KEY (user_id) REFERENCES users(id)
            );
            """,
            """
            CREATE TABLE IF NOT EXISTS shares (
                id INT AUTO_INCREMENT PRIMARY KEY,
                file_id INT NOT NULL,
                shared_with_user_id INT NOT NULL,
                shared_by_user_id INT NOT NULL,
                access_level ENUM('read', 'write', 'delete') DEFAULT 'read',
                expires_at DATETIME,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (file_id) REFERENCES files(id),
                FOREIGN KEY (shared_with_user_id) REFERENCES users(id),
                FOREIGN KEY (shared_by_user_id) REFERENCES users(id)
            );
            """
        ]


        # Execute each query
        for query in queries:
            cursor.execute(query)
        conn.commit()
        print("Tables created successfully or already exist.")

    except mysql.connector.Error as err:
        print(f"Error: {err}")
        conn.rollback()
    finally:
        cursor.close()



# USERS TABLE
def get_users(conn):
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM users")
    users = cursor.fetchall()
    cursor.close()
    return users

def add_user(username, email, password_hash):
    cursor = conn.cursor()
    query = "INSERT INTO users (username, email, password_hash, created_at) VALUES (%s, %s, %s, %s)"
    cursor.execute(query, (username, email, password_hash, datetime.now()))
    conn.commit()
    cursor.close()

def get_user_by_username(conn, username):
    cursor = conn.cursor(dictionary=True)  # Using dictionary=True to fetch results as a dictionary

    query = "SELECT * FROM users WHERE username = %s"
    cursor.execute(query, (username,))  # Execute the query with the username as a parameter

    user = cursor.fetchone()  # Fetch one result (since username should be unique)

    cursor.close()

    return user

def get_user_by_email(email):
    cursor = conn.cursor(dictionary=True)

    query = "SELECT * FROM users WHERE email = %s"
    cursor.execute(query, (email,))
    user = cursor.fetchone()

    cursor.close()
    return user


# FILES TABLE
def get_files():
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM files")
    files = cursor.fetchall()
    cursor.close()
    return files

def get_file_by_id(file_id):
    cursor = conn.cursor(dictionary=True)

    cursor.execute("SELECT * FROM files WHERE id = %s", (file_id,))
    file = cursor.fetchone()
    return file

def add_file(name, path, is_directory, owner_id, size, folder_id=None):
    cursor = conn.cursor()
    query = """
        INSERT INTO files (name, path, is_directory, owner_id, size, created_at, updated_at, folder_id) 
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
    """
    cursor.execute(query, (name, path, is_directory, owner_id, size, datetime.now(), datetime.now(), folder_id))
    conn.commit()
    cursor.close()

# FOLDERS TABLE
def get_folders(conn):
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM folders")
    folders = cursor.fetchall()
    cursor.close()
    return folders

def add_folder(conn, name, user_id, parent_id=None):
    cursor = conn.cursor()
    query = "INSERT INTO folders (name, parent_id, user_id, created_at) VALUES (%s, %s, %s, %s)"
    cursor.execute(query, (name, parent_id, user_id, datetime.now()))
    conn.commit()
    cursor.close()

# FOLDER_PERMISSIONS TABLE
def get_folder_permissions(conn):
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM folder_permissions")
    permissions = cursor.fetchall()
    cursor.close()
    return permissions

def add_folder_permission(conn, folder_id, user_id=None, group_id=None, can_read=False, can_write=False, can_delete=False):
    cursor = conn.cursor()
    query = """
        INSERT INTO folder_permissions (folder_id, user_id, group_id, can_read, can_write, can_delete) 
        VALUES (%s, %s, %s, %s, %s, %s)
    """
    cursor.execute(query, (folder_id, user_id, group_id, can_read, can_write, can_delete))
    conn.commit()
    cursor.close()

# GROUPS TABLE
def get_groups(conn):
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM groups")
    groups = cursor.fetchall()
    cursor.close()
    return groups

def add_group(conn, name, description=None):
    cursor = conn.cursor()
    query = "INSERT INTO groups (name, description, created_at) VALUES (%s, %s, %s)"
    cursor.execute(query, (name, description, datetime.now()))
    conn.commit()
    cursor.close()

# GROUP_MEMBERS TABLE
def get_group_members(conn):
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM group_members")
    members = cursor.fetchall()
    cursor.close()
    return members

def add_group_member(conn, group_id, user_id):
    cursor = conn.cursor()
    query = "INSERT INTO group_members (group_id, user_id, joined_at) VALUES (%s, %s, %s)"
    cursor.execute(query, (group_id, user_id, datetime.now()))
    conn.commit()
    cursor.close()

# GROUP_PERMISSIONS TABLE
def get_group_permissions(conn):
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM group_permissions")
    permissions = cursor.fetchall()
    cursor.close()
    return permissions

def add_group_permission(conn, group_id, file_id, can_read=False, can_write=False, can_delete=False):
    cursor = conn.cursor()
    query = """
        INSERT INTO group_permissions (group_id, file_id, can_read, can_write, can_delete) 
        VALUES (%s, %s, %s, %s, %s)
    """
    cursor.execute(query, (group_id, file_id, can_read, can_write, can_delete))
    conn.commit()
    cursor.close()

# PERMISSIONS TABLE
def get_permissions(conn):
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM permissions")
    permissions = cursor.fetchall()
    cursor.close()
    return permissions

def add_permission(conn, file_id, user_id, can_read=False, can_write=False, can_delete=False):
    cursor = conn.cursor()
    query = """
        INSERT INTO permissions (file_id, user_id, can_read, can_write, can_delete) 
        VALUES (%s, %s, %s, %s, %s)
    """
    cursor.execute(query, (file_id, user_id, can_read, can_write, can_delete))
    conn.commit()
    cursor.close()

# SHARES TABLE
def get_shares(conn):
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM shares")
    shares = cursor.fetchall()
    cursor.close()
    return shares

def add_share(conn, file_id, shared_with_user_id, shared_by_user_id, access_level="read", expires_at=None):
    cursor = conn.cursor()
    query = """
        INSERT INTO shares (file_id, shared_with_user_id, shared_by_user_id, access_level, expires_at, created_at) 
        VALUES (%s, %s, %s, %s, %s, %s)
    """
    cursor.execute(query, (file_id, shared_with_user_id, shared_by_user_id, access_level, expires_at, datetime.now()))
    conn.commit()
    cursor.close()

def get_files_with_owner_names():
    cursor = conn.cursor(dictionary=True)
    query = """
    SELECT f.id, f.name, DATE(f.updated_at) AS updated_date, f.owner_id, u.username AS owner_name
    FROM files f
    JOIN users u ON f.owner_id = u.id
    """
    cursor.execute(query)
    files = cursor.fetchall()
    cursor.close()
    return files

def delete_file(file_id):
    uploads_folder=""
    try:
        # Connect to the database

        cursor = conn.cursor(dictionary=True)

        # Step 1: Retrieve the file path from the database
        cursor.execute("SELECT path FROM files WHERE id = %s", (file_id,))
        file_record = cursor.fetchone()

        if not file_record:
            return {"success": False, "message": "File not found in the database."}

        file_path = file_record['path']
        absolute_path = os.path.join(uploads_folder, file_path)

        # Step 2: Delete the file from the filesystem
        if os.path.exists(absolute_path):
            os.remove(absolute_path)
        else:
            return {"success": False, "message": f"File not found on the filesystem: {absolute_path}"}

        # Step 3: Delete the record from the database
        cursor.execute("DELETE FROM files WHERE id = %s", (file_id,))
        conn.commit()

        return {"success": True, "message": "File deleted successfully."}

    except Error as e:
        return {"success": False, "message": f"Database error: {e}"}