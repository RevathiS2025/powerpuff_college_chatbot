import mysql.connector
from mysql.connector import Error
import sqlite3
import hashlib
import os
from typing import Optional, Dict, Any
import streamlit as st
from dotenv import load_dotenv
load_dotenv()


class DatabaseManager:
    """Handles all MySQL database operations for user management."""
   
    def __init__(self):
        self.connection = None
        self.is_sqlite = False
        self.force_sqlite = (os.getenv('DB_BACKEND','').lower() == 'sqlite') or (os.getenv('USE_SQLITE','').lower() in ('1','true','yes'))
        self.connect()
   
    def connect(self):
        """Establish connection to database with SQLite fallback."""
        if self.force_sqlite:
            try:
                db_path = os.getenv('SQLITE_PATH', os.path.join(os.getcwd(), 'powerpuff_college.db'))
                self.connection = sqlite3.connect(db_path, check_same_thread=False)
                self.connection.row_factory = sqlite3.Row
                self.is_sqlite = True
                self.create_tables()
            except Exception as e2:
                st.error(f"Error connecting to SQLite: {e2}")
                self.connection = None
            return
        try:
            self.connection = mysql.connector.connect(
                host=os.getenv('MYSQL_HOST', 'localhost'),
                database=os.getenv('MYSQL_DATABASE', 'powerpuff_college'),
                user=os.getenv('MYSQL_USER', 'root'),
                password=os.getenv('MYSQL_PASSWORD')
            )
            if self.connection.is_connected():
                self.is_sqlite = False
                self.create_tables()
                return
        except Error as e:
            st.warning(f"Error connecting to MySQL: {e}")
            self.connection = None
        try:
            db_path = os.getenv('SQLITE_PATH', os.path.join(os.getcwd(), 'powerpuff_college.db'))
            self.connection = sqlite3.connect(db_path, check_same_thread=False)
            self.connection.row_factory = sqlite3.Row
            self.is_sqlite = True
            st.info(f"Using SQLite database at {db_path}")
            self.create_tables()
        except Exception as e2:
            st.error(f"Error connecting to SQLite: {e2}")
            self.connection = None
   
    def ensure_connection(self):
        if not self.connection or (hasattr(self.connection, 'is_connected') and not self.connection.is_connected()):
            self.connect()

    def create_tables(self):
        """Create necessary tables if they don't exist."""
        try:
            cursor = self.connection.cursor()
            if self.is_sqlite:
                create_users_table = """
                CREATE TABLE IF NOT EXISTS users (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    username TEXT UNIQUE NOT NULL,
                    email TEXT UNIQUE NOT NULL,
                    password_hash TEXT NOT NULL,
                    role TEXT NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    last_login TIMESTAMP NULL
                )
                """
                create_chat_table = """
                CREATE TABLE IF NOT EXISTS chat_history (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER,
                    message TEXT NOT NULL,
                    response TEXT NOT NULL,
                    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
                )
                """
            else:
                create_users_table = """
                CREATE TABLE IF NOT EXISTS users (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    username VARCHAR(50) UNIQUE NOT NULL,
                    email VARCHAR(100) UNIQUE NOT NULL,
                    password_hash VARCHAR(255) NOT NULL,
                    role ENUM('parent', 'student', 'professor', 'dean') NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    last_login TIMESTAMP NULL
                )
                """
                create_chat_table = """
                CREATE TABLE IF NOT EXISTS chat_history (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    user_id INT,
                    message TEXT NOT NULL,
                    response TEXT NOT NULL,
                    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
                )
                """
            cursor.execute(create_users_table)
            cursor.execute(create_chat_table)
            self.connection.commit()
            cursor.close()
        except Exception as e:
            st.error(f"Error creating tables: {e}")
   
    def hash_password(self, password: str) -> str:
        """Hash password using SHA-256."""
        return hashlib.sha256(password.encode()).hexdigest()
   
    def register_user(self, username: str, email: str, password: str, role: str) -> bool:
        """Register a new user."""
        self.ensure_connection()
        if not self.connection:
            st.error("Database connection is not available.")
            return False
        try:
            cursor = self.connection.cursor()
            ph = "?" if self.is_sqlite else "%s"
            check_query = f"SELECT id FROM users WHERE username = {ph} OR email = {ph}"
            cursor.execute(check_query, (username, email))
            if cursor.fetchone():
                cursor.close()
                return False
            hashed_password = self.hash_password(password)
            insert_query = f"INSERT INTO users (username, email, password_hash, role) VALUES ({ph}, {ph}, {ph}, {ph})"
            cursor.execute(insert_query, (username, email, hashed_password, role))
            self.connection.commit()
            cursor.close()
            return True
        except Exception as e:
            st.error(f"Error registering user: {e}")
            return False
   
    def authenticate_user(self, username: str, password: str) -> Optional[Dict[str, Any]]:
        """Authenticate user and return user info."""
        self.ensure_connection()
        if not self.connection:
            st.error("Database connection is not available.")
            return None
        try:
            cursor = self.connection.cursor(dictionary=True) if not self.is_sqlite else self.connection.cursor()
            hashed_password = self.hash_password(password)
            ph = "?" if self.is_sqlite else "%s"
            query = f"SELECT id, username, email, role FROM users WHERE username = {ph} AND password_hash = {ph}"
            cursor.execute(query, (username, hashed_password))
            row = cursor.fetchone()
            user = dict(row) if (row and self.is_sqlite) else row
            if user:
                update_query = (f"UPDATE users SET last_login = CURRENT_TIMESTAMP WHERE id = {ph}" if self.is_sqlite else "UPDATE users SET last_login = NOW() WHERE id = %s")
                cursor.execute(update_query, (user['id'],))
                self.connection.commit()
            cursor.close()
            return user
        except Exception as e:
            st.error(f"Error authenticating user: {e}")
            return None
   
    def save_chat_message(self, user_id: int, message: str, response: str):
        """Save chat message and response to database."""
        self.ensure_connection()
        if not self.connection:
            st.error("Database connection is not available.")
            return
        try:
            cursor = self.connection.cursor()
            ph = "?" if self.is_sqlite else "%s"
            insert_query = f"INSERT INTO chat_history (user_id, message, response) VALUES ({ph}, {ph}, {ph})"
            cursor.execute(insert_query, (user_id, message, response))
            self.connection.commit()
            cursor.close()
        except Exception as e:
            st.error(f"Error saving chat message: {e}")
   
    def get_chat_history(self, user_id: int, limit: int = 50) -> list:
        """Get chat history for a user."""
        self.ensure_connection()
        if not self.connection:
            st.error("Database connection is not available.")
            return []
        try:
            cursor = self.connection.cursor(dictionary=True) if not self.is_sqlite else self.connection.cursor()
            ph = "?" if self.is_sqlite else "%s"
            query = f"SELECT message, response, timestamp FROM chat_history WHERE user_id = {ph} ORDER BY timestamp DESC LIMIT {ph}"
            cursor.execute(query, (user_id, limit))
            rows = cursor.fetchall()
            cursor.close()
            if self.is_sqlite:
                return list(reversed([dict(r) for r in rows]))
            return list(reversed(rows))
        except Exception as e:
            st.error(f"Error getting chat history: {e}")
            return []


    def has_users(self) -> bool:
        self.ensure_connection()
        if not self.connection:
            return False
        try:
            cursor = self.connection.cursor()
            cursor.execute("SELECT 1 FROM users LIMIT 1")
            exists = cursor.fetchone() is not None
            cursor.close()
            return exists
        except Exception:
            return False

    def clear_chat_history(self, user_id: int) -> bool:
        """Delete all chat history for a user."""
        try:
            self.ensure_connection()
            if not self.connection:
                st.error("Database connection is not available.")
                return False
            cursor = self.connection.cursor()
            ph = "?" if self.is_sqlite else "%s"
            delete_query = f"DELETE FROM chat_history WHERE user_id = {ph}"
            cursor.execute(delete_query, (user_id,))
            self.connection.commit()
            cursor.close()
            return True
        except Exception as e:
            st.error(f"Error clearing chat history: {e}")
            return False
   
    def close_connection(self):
        """Close database connection."""
        if self.connection:
            try:
                if hasattr(self.connection, 'is_connected') and self.connection.is_connected():
                    self.connection.close()
                else:
                    self.connection.close()
            except Exception:
                pass


# Global database instance
@st.cache_resource
def get_database():
    """Get database instance (cached)."""
    db = DatabaseManager()
    db.ensure_connection()
    return db
