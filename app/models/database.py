import sqlite3
import datetime

class Database:
    def __init__(self, db_path="time_app.db"):
        """
        Initialize the database connection with support for:
        - Automated time tracking
        - Deadlines
        - History tracking
        """
        self.db_path = db_path
        self.conn = sqlite3.connect(db_path)
        
        # Enable foreign keys for data integrity
        self.conn.execute("PRAGMA foreign_keys = ON")
        
        # This allows accessing columns by name (more readable)
        self.conn.row_factory = sqlite3.Row
        
        self.create_tables()

    def create_tables(self):
        """
        Create database tables with support for the new features.
        Automatically adds the priority column if it doesn't exist.
        """
        cursor = self.conn.cursor()
        
        # Tasks table with deadline support
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS tasks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            description TEXT,
            category TEXT,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            deadline DATETIME,                      -- New: deadline date/time
            completed BOOLEAN DEFAULT 0,
            priority BOOLEAN DEFAULT 0,             -- Corretta la virgola mancante qui
            total_time INTEGER DEFAULT 0            -- Tracked time in seconds
        )
        """)
        try:
            cursor.execute("PRAGMA table_info(tasks)")
            columns = [col[1] for col in cursor.fetchall()]
            if 'priority' not in columns:
                cursor.execute("ALTER TABLE tasks ADD COLUMN priority BOOLEAN DEFAULT 0")
        except:
            pass  # Column might already exist
    
        
        # Time entries for session tracking
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS time_entries (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            task_id INTEGER NOT NULL,
            start_time DATETIME NOT NULL,           -- Session start timestamp
            end_time DATETIME,                      -- Session end timestamp
            duration INTEGER,                       -- Session duration in seconds
            FOREIGN KEY(task_id) REFERENCES tasks(id) ON DELETE CASCADE
        )
        """)
        
        # Notes table
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS notes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            task_id INTEGER NOT NULL,
            content TEXT NOT NULL,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY(task_id) REFERENCES tasks(id) ON DELETE CASCADE
        )
        """)
        
        # New: Task history for tracking changes
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS task_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            task_id INTEGER NOT NULL,
            change_date DATETIME DEFAULT CURRENT_TIMESTAMP,
            user TEXT DEFAULT 'default_user',       -- For future multi-user support
            field_name TEXT NOT NULL,               -- Which field was changed
            old_value TEXT,                         -- Previous value (as text)
            new_value TEXT,                         -- New value (as text)
            FOREIGN KEY(task_id) REFERENCES tasks(id) ON DELETE CASCADE
        )
        """)
        
        self.conn.commit()

    def execute(self, query, params=(), fetchone=False, fetchall=False):
        """
        Execute a SQL query with parameters.
        Returns results based on options or last inserted row id.
        """
        cursor = self.conn.cursor()
        cursor.execute(query, params)
        
        # Return data if requested
        if fetchone:
            return cursor.fetchone()
        elif fetchall:
            return cursor.fetchall()
            
        # For insert operations, commit and return the new id
        self.conn.commit()
        return cursor.lastrowid
    
    def get_current_datetime(self):
        """
        Returns current date and time from system.
        Used for synchronizing with local calendar/clock.
        """
        return datetime.datetime.now()
        
    def close(self):
        """Close the database connection properly"""
        if self.conn:
            self.conn.close()
