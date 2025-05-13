import datetime

class TaskController:
    def __init__(self, db_connection):
        """
        Initialize the task controller with database connection.
        
        Args:
            db_connection: Database instance for CRUD operations
        """
        self.db = db_connection
    
    def create_task(self, name, description=None, category=None, deadline=None, priority=False):
        """
        Create a new task with optional deadline.
        
        Args:
            name: Task name (required)
            description: Task description (optional)
            category: Task category (optional)
            deadline: Task deadline as datetime (optional)
            priority: Whether task is priority (default False)
            
        Returns:
            int: ID of the created task
            
        Raises:
            ValueError: If name is empty
        """
        # Validate input data
        if not name or len(name.strip()) == 0:
            raise ValueError("Task name is required")
        
        # Insert into database
        query = """
        INSERT INTO tasks (name, description, category, deadline, priority) 
        VALUES (?, ?, ?, ?, ?)
        """
        task_id = self.db.execute(query, (name, description, category, deadline, priority))
        
        # Log creation in history
        self.db.execute(
            "INSERT INTO task_history (task_id, field_name, old_value, new_value) VALUES (?, ?, ?, ?)",
            (task_id, "creation", None, f"Task created: {name}")
        )
        
        return task_id
    
    def update_task(self, task_id, **kwargs):
        """
        Update task fields and track changes in history.
        
        Args:
            task_id: ID of the task to update
            **kwargs: Fields to update (name, description, category, deadline, completed, priority)
            
        Returns:
            bool: True if successful
            
        Raises:
            ValueError: If task doesn't exist
        """
        # Check if task exists
        task = self.get_task(task_id)
        if not task:
            raise ValueError(f"Task with ID {task_id} does not exist")
        
        # Build update query dynamically based on provided fields
        updates = []
        params = []
        history_updates = []
        
        # Process each field
        for field, new_value in kwargs.items():
            if field not in ['name', 'description', 'category', 'deadline', 'completed', 'priority']:
                continue
                
            updates.append(f"{field} = ?")
            params.append(new_value)
            
            # Track change in history
            old_value = task[field] if field in task.keys() else None
            history_updates.append((
                task_id,
                field,
                str(old_value) if old_value is not None else None,
                str(new_value) if new_value is not None else None
            ))
        
        if not updates:
            return False
            
        # Update the task
        query = f"UPDATE tasks SET {', '.join(updates)} WHERE id = ?"
        params.append(task_id)
        self.db.execute(query, params)
        
        # Add entries to history table
        for update in history_updates:
            self.db.execute(
                "INSERT INTO task_history (task_id, field_name, old_value, new_value) VALUES (?, ?, ?, ?)",
                update
            )
            
        return True
    
    def delete_task(self, task_id):
        """
        Delete a task and all its related data.
        
        Args:
            task_id: ID of the task to delete
            
        Returns:
            bool: True if successful
            
        Raises:
            ValueError: If task doesn't exist
        """
        # Check if task exists
        task = self.get_task(task_id)
        if not task:
            raise ValueError(f"Task with ID {task_id} does not exist")
            
        # Delete task (cascading will delete related entries)
        self.db.execute("DELETE FROM tasks WHERE id = ?", (task_id,))
        return True
    
    def get_task(self, task_id):
        """
        Get a single task by ID.
        
        Args:
            task_id: ID of the task to retrieve
            
        Returns:
            dict: Task data or None if not found
        """
        return self.db.execute(
            "SELECT * FROM tasks WHERE id = ?", 
            (task_id,), 
            fetchone=True
        )
    
    def get_all_tasks(self, include_completed=True, sort_by='name'):
        """
        Get all tasks with optional filtering.
        
        Args:
            include_completed: Whether to include completed tasks (default True)
            sort_by: Sorting criterion (name, deadline, priority, category)
            
        Returns:
            list: List of task dictionaries
        """
        query = "SELECT * FROM tasks"
        params = []
        
        # Apply filter for completed tasks
        if not include_completed:
            query += " WHERE completed = 0"
            
        # Add sorting
        if sort_by == 'name':
            query += " ORDER BY name"
        elif sort_by == 'deadline':
            query += " ORDER BY CASE WHEN deadline IS NULL THEN 1 ELSE 0 END, deadline, name"
        elif sort_by == 'priority':
            query += " ORDER BY priority DESC, name"
        elif sort_by == 'category':
            query += " ORDER BY category, name"
        
        return self.db.execute(query, tuple(params), fetchall=True)
    
    def get_filtered_tasks(self, completed=None, priority=None, category=None, sort_by='name'):
        """
        Get tasks with specific filters applied.
        
        Args:
            completed: Filter by completion status (True/False/None)
            priority: Filter by priority status (True/False/None)
            category: Filter by category (string/None)
            sort_by: Sorting criterion (name, deadline, priority, category)
            
        Returns:
            list: List of task dictionaries
        """
        query = "SELECT * FROM tasks WHERE 1=1"
        params = []
        
        # Apply filters
        if completed is not None:
            query += " AND completed = ?"
            params.append(completed)
            
        if priority is not None:
            query += " AND priority = ?"
            params.append(priority)
            
        if category is not None:
            query += " AND category = ?"
            params.append(category)
            
        # Add sorting
        if sort_by == 'name':
            query += " ORDER BY name"
        elif sort_by == 'deadline':
            query += " ORDER BY CASE WHEN deadline IS NULL THEN 1 ELSE 0 END, deadline, name"
        elif sort_by == 'priority':
            query += " ORDER BY priority DESC, name"
        elif sort_by == 'category':
            query += " ORDER BY category, name"
        
        return self.db.execute(query, tuple(params), fetchall=True)
    
    def get_task_history(self, task_id):
        """
        Get history of changes for a specific task.
        
        Args:
            task_id: ID of the task
            
        Returns:
            list: List of history entries
        """
        return self.db.execute(
            "SELECT * FROM task_history WHERE task_id = ? ORDER BY change_date DESC",
            (task_id,),
            fetchall=True
        )
