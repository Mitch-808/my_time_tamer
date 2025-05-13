import time
import datetime

class TimerController:
    def __init__(self, db_connection):
        """
        Initialize the timer controller with database connection.
        
        Args:
            db_connection: Database instance for storing time entries
        """
        self.db = db_connection
        self.current_task_id = None
        self.start_time = None
        self.is_running = False
        self.paused_time = 0
        self.current_entry_id = None
    
    def start(self, task_id):
        """
        Start timing a task. Creates a new time entry in the database.
        
        Args:
            task_id: ID of the task to time
            
        Returns:
            entry_id: ID of the created time entry
            
        Raises:
            RuntimeError: If timer is already running
        """
        # Check if timer is already running
        if self.is_running:
            raise RuntimeError("Timer is already running")
        
        # Store the current task and start time
        self.current_task_id = task_id
        current_datetime = self.db.get_current_datetime()  # Synchronized with system
        
        # If we're resuming from pause, adjust the start time
        if self.paused_time > 0:
            self.start_time = time.time() - self.paused_time
            self.paused_time = 0
        else:
            self.start_time = time.time()
        
        self.is_running = True
        
        # Create a new time entry in the database
        self.current_entry_id = self.db.execute(
            "INSERT INTO time_entries (task_id, start_time) VALUES (?, ?)",
            (task_id, current_datetime)
        )
        
        return self.current_entry_id
    
    def pause(self):
        """
        Pause the current timing session without ending it.
        
        Raises:
            RuntimeError: If timer is not running
        """
        if not self.is_running:
            raise RuntimeError("Timer is not running")
        
        # Store how much time has elapsed so far
        self.paused_time = time.time() - self.start_time
        self.is_running = False
    
    def resume(self):
        """
        Resume a paused timer.
        
        Raises:
            RuntimeError: If timer is not paused
        """
        if self.is_running or self.paused_time == 0:
            raise RuntimeError("Timer is not paused")
            
        # Reset start time based on the pause duration
        self.start_time = time.time() - self.paused_time
        self.is_running = True
    
    def stop(self):
        """
        Stop timing and update the database with the session duration.
        
        Returns:
            duration: The session duration in seconds
            
        Raises:
            RuntimeError: If timer is not running or paused
        """
        if not self.is_running and self.paused_time == 0:
            raise RuntimeError("Timer is not running or paused")
        
        # Get current time for the end timestamp
        current_datetime = self.db.get_current_datetime()
        
        # Calculate duration based on whether timer is running or paused
        duration = int(time.time() - self.start_time) if self.is_running else int(self.paused_time)
        
        # Update the time entry in the database
        self.db.execute(
            "UPDATE time_entries SET end_time = ?, duration = ? WHERE id = ?",
            (current_datetime, duration, self.current_entry_id)
        )
        
        # Update the total time for the task
        self.db.execute(
            "UPDATE tasks SET total_time = total_time + ? WHERE id = ?",
            (duration, self.current_task_id)
        )
        
        # Record in task history
        self.db.execute(
            "INSERT INTO task_history (task_id, field_name, old_value, new_value) VALUES (?, ?, ?, ?)",
            (self.current_task_id, "total_time", "updated", f"+{duration} seconds")
        )
        
        # Reset the timer state
        self.current_task_id = None
        self.current_entry_id = None
        self.start_time = None
        self.is_running = False
        self.paused_time = 0
        
        return duration
    
    def get_elapsed_time(self):
        """
        Get the elapsed time of the current session in seconds.
        
        Returns:
            float: Elapsed time in seconds, or 0 if timer is not active
        """
        if not self.is_running and self.paused_time == 0:
            return 0
            
        return time.time() - self.start_time if self.is_running else self.paused_time
        
    def format_time(self, seconds):
        """
        Convert seconds to human-readable format (HH:MM:SS).
        
        Args:
            seconds: Time duration in seconds
            
        Returns:
            str: Formatted time string
        """
        hours = int(seconds // 3600)
        minutes = int((seconds % 3600) // 60)
        seconds = int(seconds % 60)
        
        return f"{hours:02d}:{minutes:02d}:{seconds:02d}"
