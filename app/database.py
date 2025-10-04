import mysql.connector
from mysql.connector import Error
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
        self.connect()
    
    def connect(self):
        """Establish connection to MySQL database."""
        try:
            self.connection = mysql.connector.connect(
                host=os.getenv('MYSQL_HOST', 'localhost'),
                database=os.getenv('MYSQL_DATABASE', 'powerpuff_college'),
                user=os.getenv('MYSQL_USER', 'root'),
                password=os.getenv('MYSQL_PASSWORD')
            )
            
            if self.connection.is_connected():
                self.create_tables()
                
        except Error as e:
            st.error(f"Error connecting to MySQL: {e}")
            self.connection = None
    
    def create_tables(self):
        """Create necessary tables if they don't exist."""
        try:
            cursor = self.connection.cursor()
            
            # Users table
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
            
            # Chat history table
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
            
        except Error as e:
            st.error(f"Error creating tables: {e}")
    
    def hash_password(self, password: str) -> str:
        """Hash password using SHA-256."""
        return hashlib.sha256(password.encode()).hexdigest()
    
    def register_user(self, username: str, email: str, password: str, role: str) -> bool:
        """Register a new user."""
        try:
            cursor = self.connection.cursor()
            
            # Check if username or email already exists
            check_query = "SELECT id FROM users WHERE username = %s OR email = %s"
            cursor.execute(check_query, (username, email))
            
            if cursor.fetchone():
                cursor.close()
                return False  # User already exists
            
            # Insert new user
            hashed_password = self.hash_password(password)
            insert_query = """
            INSERT INTO users (username, email, password_hash, role) 
            VALUES (%s, %s, %s, %s)
            """
            cursor.execute(insert_query, (username, email, hashed_password, role))
            self.connection.commit()
            cursor.close()
            return True
            
        except Error as e:
            st.error(f"Error registering user: {e}")
            return False
    
    def authenticate_user(self, username: str, password: str) -> Optional[Dict[str, Any]]:
        """Authenticate user and return user info."""
        try:
            cursor = self.connection.cursor(dictionary=True)
            hashed_password = self.hash_password(password)
            
            query = """
            SELECT id, username, email, role 
            FROM users 
            WHERE username = %s AND password_hash = %s
            """
            cursor.execute(query, (username, hashed_password))
            user = cursor.fetchone()
            
            if user:
                # Update last login
                update_query = "UPDATE users SET last_login = NOW() WHERE id = %s"
                cursor.execute(update_query, (user['id'],))
                self.connection.commit()
            
            cursor.close()
            return user
            
        except Error as e:
            st.error(f"Error authenticating user: {e}")
            return None
    
    def save_chat_message(self, user_id: int, message: str, response: str):
        """Save chat message and response to database."""
        try:
            cursor = self.connection.cursor()
            
            insert_query = """
            INSERT INTO chat_history (user_id, message, response) 
            VALUES (%s, %s, %s)
            """
            cursor.execute(insert_query, (user_id, message, response))
            self.connection.commit()
            cursor.close()
            
        except Error as e:
            st.error(f"Error saving chat message: {e}")
    
    def get_chat_history(self, user_id: int, limit: int = 50) -> list:
        """Get chat history for a user."""
        try:
            cursor = self.connection.cursor(dictionary=True)
            
            query = """
            SELECT message, response, timestamp 
            FROM chat_history 
            WHERE user_id = %s 
            ORDER BY timestamp DESC 
            LIMIT %s
            """
            cursor.execute(query, (user_id, limit))
            history = cursor.fetchall()
            cursor.close()
            
            return list(reversed(history))  # Return in chronological order
            
        except Error as e:
            st.error(f"Error getting chat history: {e}")
            return []
    
    def close_connection(self):
        """Close database connection."""
        if self.connection and self.connection.is_connected():
            self.connection.close()

# Global database instance
@st.cache_resource
def get_database():
    """Get database instance (cached)."""
    return DatabaseManager()


