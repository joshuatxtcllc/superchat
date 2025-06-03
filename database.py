
import sqlite3
import json
import os
from datetime import datetime

class ConversationDB:
    def __init__(self, db_path="conversations.db"):
        self.db_path = db_path
        self.init_db()
    
    def init_db(self):
        """Initialize the database with required tables"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Conversations table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS conversations (
                id TEXT PRIMARY KEY,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                message_count INTEGER DEFAULT 0,
                metadata TEXT
            )
        ''')
        
        # Messages table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS messages (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                conversation_id TEXT,
                role TEXT,
                content TEXT,
                model TEXT,
                timestamp TIMESTAMP,
                token_count INTEGER,
                response_time REAL,
                FOREIGN KEY (conversation_id) REFERENCES conversations (id)
            )
        ''')
        
        # Usage analytics table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS usage_analytics (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                date DATE,
                model_used TEXT,
                message_count INTEGER DEFAULT 1,
                avg_response_time REAL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        conn.commit()
        conn.close()
    
    def save_conversation(self, conversation_id, messages):
        """Save conversation to database (fallback when file system is used)"""
        # For now, this is a placeholder for future database migration
        pass
    
    def get_usage_stats(self, days=7):
        """Get usage statistics for the last N days"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT model_used, COUNT(*) as usage_count, AVG(avg_response_time) as avg_time
            FROM usage_analytics 
            WHERE date >= date('now', '-{} days')
            GROUP BY model_used
        '''.format(days))
        
        stats = cursor.fetchall()
        conn.close()
        return stats
