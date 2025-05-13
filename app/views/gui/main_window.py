import tkinter as tk
from tkinter import ttk, messagebox, simpledialog, filedialog
from tkcalendar import DateEntry
import datetime
from datetime import timedelta

class TimeApp(tk.Tk):
    def __init__(self, task_controller, timer_controller):
        super().__init__()
        
        # Store controllers for later use
        self.task_controller = task_controller
        self.timer_controller = timer_controller
        self.active_task_id = None
        
        # Configure window
        self.title("My_Time_Tamer")
        self.geometry("1100x650")  # Made wider to accommodate details panel
        self.minsize(900, 600) # Smallest window size
        self.configure(bg="#2c3e50")
        
        # Fix resizable flag to maintain proper layout
        self.resizable(True, True)
        
        # configure cell weights for correct resizing
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)
        
        # Apply functional styling
        self._setup_styles()
        
        # Create UI components
        self._create_header()
        
        # Create main content frame
        content_frame = ttk.Frame(self)
        content_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
        
        # Create main frame containing filters and buttons
        filter_button_frame = ttk.Frame(content_frame)
        filter_button_frame.pack(fill=tk.X, pady=5)
        
        # Filter frame
        filter_frame = ttk.Frame(filter_button_frame)
        filter_frame.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        # Implement filters (All tasks, WIP, Completed)
        self._create_filter_panel(filter_frame)
        
        # "Sort by" moved to the right side
        sort_frame = ttk.Frame(filter_button_frame)
        sort_frame.pack(side=tk.RIGHT)
        
        ttk.Label(sort_frame, text="Sort by:").pack(side=tk.LEFT, padx=5)
        self.sort_var = tk.StringVar(value="name")
        sort_options = ttk.Combobox(sort_frame, 
                                textvariable=self.sort_var,
                                values=["name", "deadline", "priority", "category"],
                                width=15,
                                state="readonly")
        sort_options.pack(side=tk.LEFT, padx=5)
        sort_options.bind("<<ComboboxSelected>>", lambda e: self.refresh_tasks())
        
        # Button frame beaneath filter frame
        button_frame = ttk.Frame(content_frame)
        button_frame.pack(fill=tk.X, pady=5)
        
        # Buttons reduced in size
        add_button = ttk.Button(button_frame, text="Add Task", command=self.add_task)
        add_button.pack(side=tk.LEFT, padx=5)
        
        edit_button = ttk.Button(button_frame, text="Edit Task", command=self.edit_task)
        edit_button.pack(side=tk.LEFT, padx=5)
        
        delete_button = ttk.Button(button_frame, text="Delete Task", command=self.delete_task)
        delete_button.pack(side=tk.LEFT, padx=5)
        
        complete_button = ttk.Button(button_frame, 
                                text="Toggle Complete", 
                                style="Complete.TButton",
                                command=self.toggle_complete)
        complete_button.pack(side=tk.LEFT, padx=5)
        
        # Timer frame - below button frame
        self.timer_frame = ttk.Frame(content_frame)
        self.timer_frame.pack(fill=tk.X, pady=5)
        self._create_timer_section(self.timer_frame)
        
        # Create left panel (task list)
        left_panel = ttk.Frame(content_frame)
        left_panel.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        # Create task view inside the left_panel
        self._create_task_view(left_panel)
        # Create filter section
        # self._create_filter_panel(left_panel)
        
        
        # Create right panel (task details)
        right_panel = ttk.Frame(content_frame, width=300)
        right_panel.pack(side=tk.RIGHT, fill=tk.BOTH, padx=(20, 0))
        self._create_details_panel(right_panel)
        
        self._create_footer()
        
        # Load initial data
        self.current_filter = "all"  # Default filter
        self.refresh_tasks()
        
        # Start the timer update loop
        self._update_timer_display()
    
    def _setup_styles(self):
        """Setup custom styles for a modern look"""
        style = ttk.Style(self)
        style.theme_use('clam')
        
        # Button styles
        style.configure('TButton',
                      font=('Helvetica', 12),
                      padding=10, 
                      background='#2980b9',
                      foreground='white')
        style.map('TButton', 
                background=[('active', '#3498db')])
        
        # Special button styles
        style.configure('Start.TButton', background='#27ae60')
        style.map('Start.TButton', background=[('active', '#2ecc71')])
        
        style.configure('Stop.TButton', background='#c0392b')
        style.map('Stop.TButton', background=[('active', '#e74c3c')])
        
        style.configure('Priority.TButton', background='#e67e22')
        style.map('Priority.TButton', background=[('active', '#f39c12')])
        
        style.configure('Complete.TButton', background='#8e44ad')
        style.map('Complete.TButton', background=[('active', '#9b59b6')])
        
        # Label styles
        style.configure('TLabel', 
                      background='#2c3e50',
                      foreground='white', 
                      font=('Helvetica', 12))
        
        # Heading style
        style.configure('Heading.TLabel', 
                      font=('Helvetica', 20, 'bold'),
                      padding=10)
        
        # Timer display style
        style.configure('Timer.TLabel', 
                      font=('Helvetica', 36, 'bold'),
                      foreground='#f1c40f')
        
        # Task list style
        style.configure('Treeview', 
                      background='#34495e',
                      foreground='white', 
                      rowheight=30,
                      fieldbackground='#34495e',
                      font=('Helvetica', 12))
        style.map('Treeview', 
                background=[('selected', '#2980b9')],
                foreground=[('selected', 'white')])
        
        # Configure Treeview heading style
        style.configure('Treeview.Heading', 
                      background='#2c3e50',
                      foreground='white',
                      font=('Helvetica', 14, 'bold'))
        
        # Frame style for details panel
        style.configure('Details.TFrame', background='#34495e', relief='groove')
        
        # Details header style
        style.configure('DetailsHeader.TLabel', 
                       font=('Helvetica', 16, 'bold'),
                       background='#34495e')
        
        # Text style
        style.configure('Details.TLabel', 
                       background='#34495e',
                       font=('Helvetica', 12))
        
        # Radio button style
        style.configure('TRadiobutton', 
                       background='#2c3e50',
                       foreground='white',
                       font=('Helvetica', 12))
        style.map('TRadiobutton', 
                background=[('active', '#34495e')])
    
    def _create_header(self):
        """Create the app header with title"""
        header_frame = ttk.Frame(self)
        header_frame.pack(fill=tk.X, pady=(20, 10))
        
        title_label = ttk.Label(header_frame, 
                               text="⏱️ My Time Tamer", 
                               style='Heading.TLabel')
        title_label.pack()
    
    def _create_filter_panel(self, parent):
        """Create panel with filtering options - semplificato"""
        # Create a variable for filter selection
        self.filter_var = tk.StringVar(value="all")
        
        # Radio buttons for filters
        ttk.Radiobutton(parent, 
                    text="All Tasks", 
                    variable=self.filter_var, 
                    value="all",
                    command=self.refresh_tasks).pack(side=tk.LEFT, padx=10)
        
        ttk.Radiobutton(parent, 
                    text="WIP", 
                    variable=self.filter_var, 
                    value="wip",
                    command=self.refresh_tasks).pack(side=tk.LEFT, padx=10)
        
        ttk.Radiobutton(parent, 
                    text="Completed", 
                    variable=self.filter_var, 
                    value="completed",
                    command=self.refresh_tasks).pack(side=tk.LEFT, padx=10)

    
    def _create_task_view(self, parent):
        """Create the task list with scrollbar"""
        # Main frame for task section
        task_frame = ttk.Frame(parent)
        task_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=10)
        
        # Task list with scrollbar
        tree_frame = ttk.Frame(task_frame)
        tree_frame.pack(fill=tk.BOTH, expand=True)
        
        self.task_tree = ttk.Treeview(tree_frame, 
                                    columns=("Name", "Category", "Deadline", "Total Time", "Status"),
                                    show='headings', 
                                    height=12)
        
        # Configure columns
        self.task_tree.heading("Name", text="Task Name")
        self.task_tree.heading("Category", text="Category")
        self.task_tree.heading("Deadline", text="Deadline")
        self.task_tree.heading("Total Time", text="Total Time")
        self.task_tree.heading("Status", text="Status")
        
        self.task_tree.column("Name", width=250, anchor='w')
        self.task_tree.column("Category", width=120, anchor='center') 
        self.task_tree.column("Deadline", width=120, anchor='center')
        self.task_tree.column("Total Time", width=120, anchor='center')
        self.task_tree.column("Status", width=100, anchor='center')
        
        # Bind selection event
        self.task_tree.bind('<<TreeviewSelect>>', self.on_task_select)
    
        # Add scrollbar
        scrollbar = ttk.Scrollbar(tree_frame, orient="vertical", command=self.task_tree.yview)
        self.task_tree.configure(yscrollcommand=scrollbar.set)
        
        self.task_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

    
    def _create_details_panel(self, parent):
        """Create panel to display task details including description"""
        details_frame = ttk.Frame(parent, style='Details.TFrame', padding=15)
        details_frame.pack(fill=tk.BOTH, expand=True)
        
        # Details header
        ttk.Label(details_frame, 
                 text="Task Details", 
                 style="DetailsHeader.TLabel").pack(anchor='w', pady=(0, 15))
        
        # Task info (will be populated when a task is selected)
        detail_fields = ["Name:", "Category:", "Created:", "Deadline:", "Status:"]
        self.detail_labels = {}
        
        for field in detail_fields:
            field_frame = ttk.Frame(details_frame)
            field_frame.pack(fill=tk.X, pady=3)
            
            ttk.Label(field_frame, 
                     text=field,
                     width=12, 
                     style="Details.TLabel").pack(side=tk.LEFT)
            
            # Store label for later updates
            self.detail_labels[field] = ttk.Label(field_frame, 
                                                text="-", 
                                                style="Details.TLabel")
            self.detail_labels[field].pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        # Description section
        ttk.Label(details_frame, 
                 text="Description:", 
                 style="Details.TLabel").pack(anchor='w', pady=(15, 5))
        
        # Text area for description
        self.description_text = tk.Text(details_frame, 
                                      height=10, 
                                      width=30, 
                                      bg="#34495e", 
                                      fg="white",
                                      font=("Helvetica", 12),
                                      wrap=tk.WORD,
                                      state=tk.DISABLED)
        self.description_text.pack(fill=tk.BOTH, expand=True)
    
    def _create_timer_section(self, parent_frame):
        """Create timer display and controls direttamente nel frame passato"""
        # Current task label
        self.current_task_label = ttk.Label(parent_frame, 
                                        text="No Task Selected", 
                                        anchor='center')
        self.current_task_label.pack(fill=tk.X, pady=5)
        
        # Timer display
        self.timer_display = ttk.Label(parent_frame, 
                                    text="00:00:00", 
                                    style='Timer.TLabel',
                                    anchor='center')
        self.timer_display.pack(fill=tk.X, pady=5)
        
        # Timer buttons
        button_frame = ttk.Frame(parent_frame)
        button_frame.pack(pady=5)
        
        self.start_button = ttk.Button(button_frame, 
                                    text="▶ Start", 
                                    style='Start.TButton',
                                    command=self.start_timer)
        self.start_button.grid(row=0, column=0, padx=10)
        
        self.pause_button = ttk.Button(button_frame, 
                                    text="⏸ Pause", 
                                    command=self.pause_timer)
        self.pause_button.grid(row=0, column=1, padx=10)
        
        self.stop_button = ttk.Button(button_frame, 
                                    text="⏹ Stop", 
                                    style='Stop.TButton',
                                    command=self.stop_timer)
        self.stop_button.grid(row=0, column=2, padx=10)
        
        # Initial button states
        self.pause_button.config(state='disabled')
        self.stop_button.config(state='disabled')

    
    def _create_footer(self):
        """Create footer with status and export options"""
        footer_frame = ttk.Frame(self)
        footer_frame.pack(fill=tk.X, padx=20, pady=15)
        
        # Status label
        self.status_label = ttk.Label(footer_frame, 
                                     text="Ready", 
                                     anchor='w')
        self.status_label.pack(side=tk.LEFT)
        
        # Export options
        export_button = ttk.Button(footer_frame, 
                                  text="Export Data",
                                  command=self.export_data)
        export_button.pack(side=tk.RIGHT)
    
    def refresh_tasks(self):
        """Load and display tasks from the database with applied filters"""
        # Clear current items
        for item in self.task_tree.get_children():
            self.task_tree.delete(item)
        
        # Get filter values
        current_filter = self.filter_var.get()
        sort_by = self.sort_var.get()
        
        # Get tasks with filters
        tasks = []
        if current_filter == "all":
            tasks = self.task_controller.get_all_tasks(sort_by=sort_by)
        elif current_filter == "wip":
            tasks = self.task_controller.get_all_tasks(include_completed=False, sort_by=sort_by)
        elif current_filter == "completed":
            tasks = self.task_controller.get_filtered_tasks(completed=True, sort_by=sort_by)
        
        # Insert tasks into tree
        for task in tasks:
            # Format the deadline if it exists
            deadline = "-"
            if task['deadline']:
                if isinstance(task['deadline'], str):
                    deadline = task['deadline']
                else:
                    deadline = task['deadline'].strftime("%Y-%m-%d")
            
            # Format the total time
            total_time = self._format_duration(task['total_time'])
            
            # Task status
            status = "✓ Done" if task['completed'] else "In Progress"
            
            # Priority indicator
            name_display = "❗ " + task['name'] if task['priority'] else task['name']
            
            self.task_tree.insert("", tk.END, 
                                 iid=task['id'], 
                                 values=(name_display, 
                                        task['category'] or "-", 
                                        deadline, 
                                        total_time,
                                        status))
    
    def _format_duration(self, seconds):
        """Format seconds into human-readable time"""
        if not seconds:
            return "0:00:00"
        
        hours, remainder = divmod(seconds, 3600)
        minutes, seconds = divmod(remainder, 60)
        return f"{int(hours)}:{int(minutes):02d}:{int(seconds):02d}"
    
    def on_task_select(self, event):
        """Handle task selection from the tree"""
        selected_items = self.task_tree.selection()
        if selected_items:
            self.active_task_id = int(selected_items[0])
            task = self.task_controller.get_task(self.active_task_id)
            
            # Update current task label
            self.current_task_label.config(text=f"Selected: {task['name']}")
            
            # Enable start button
            self.start_button.config(state='normal')
            
            # Update task details panel
            self.detail_labels["Name:"].config(text=task['name'])
            self.detail_labels["Category:"].config(text=task['category'] or "-")
            self.detail_labels["Created:"].config(text=task['created_at'])
            
            deadline_text = "-"
            if task['deadline']:
                if isinstance(task['deadline'], str):
                    deadline_text = task['deadline']
                else:
                    deadline_text = task['deadline'].strftime("%Y-%m-%d")
            self.detail_labels["Deadline:"].config(text=deadline_text)
            
            # Corretto: usa parentesi quadre invece di get()
            status_text = "Completed" if task['completed'] else "In Progress"
            priority_text = " (Priority)" if task['priority'] else ""
            self.detail_labels["Status:"].config(text=f"{status_text}{priority_text}")
            
            # Update description text
            self.description_text.config(state=tk.NORMAL)
            self.description_text.delete("1.0", tk.END)
            if task['description']:
                self.description_text.insert("1.0", task['description'])
            else:
                self.description_text.insert("1.0", "No description available.")
            self.description_text.config(state=tk.DISABLED)
        else:
            self.active_task_id = None
            self.current_task_label.config(text="No Task Selected")
            self.start_button.config(state='disabled')
            
            # Clear details panel
            for label in self.detail_labels.values():
                label.config(text="-")
            
            self.description_text.config(state=tk.NORMAL)
            self.description_text.delete("1.0", tk.END)
            self.description_text.insert("1.0", "Select a task to view details.")
            self.description_text.config(state=tk.DISABLED)
    
    def _update_timer_display(self):
        """Update timer display every second"""
        if self.timer_controller.is_running:
            elapsed = self.timer_controller.get_elapsed_time()
            display_time = self._format_duration(elapsed)
            self.timer_display.config(text=display_time)
        
        # Schedule next update
        self.after(1000, self._update_timer_display)
    
    def start_timer(self):
        """Start timing the selected task"""
        if not self.active_task_id:
            messagebox.showerror("Error", "Please select a task first")
            return
        
        try:
            self.timer_controller.start(self.active_task_id)
            # Update UI
            self.start_button.config(state='disabled')
            self.pause_button.config(state='normal')
            self.stop_button.config(state='normal')
            self.status_label.config(text="Timer running...")
        except Exception as e:
            messagebox.showerror("Error", str(e))
    
    def pause_timer(self):
        """Pause the current timer"""
        try:
            self.timer_controller.pause()
            # Update UI
            self.start_button.config(state='normal', text="▶ Resume")
            self.pause_button.config(state='disabled')
            self.status_label.config(text="Timer paused")
        except Exception as e:
            messagebox.showerror("Error", str(e))
    
    def stop_timer(self):
        """Stop and save the current timing session"""
        try:
            duration = self.timer_controller.stop()
            # Update UI
            self.timer_display.config(text="00:00:00")
            self.start_button.config(state='normal', text="▶ Start")
            self.pause_button.config(state='disabled')
            self.stop_button.config(state='disabled')
            self.status_label.config(text=f"Session completed: {self._format_duration(duration)}")
            # Refresh task list to show updated total time
            self.refresh_tasks()
            
            # Update task details if the same task is still selected
            if self.active_task_id:
                self.on_task_select(None)
        except Exception as e:
            messagebox.showerror("Error", str(e))
    
    def add_task(self):
        """Open dialog to add a new task with all fields"""
        # Create a dialog window
        dialog = tk.Toplevel(self)
        dialog.title("New Task")
        dialog.geometry("400x350")
        dialog.configure(bg="#2c3e50")
        dialog.transient(self)  # Make it modal
        dialog.grab_set()  # Make it modal
        
        # Task name
        ttk.Label(dialog, text="Task Name:").grid(row=0, column=0, padx=10, pady=10, sticky='w')
        name_entry = ttk.Entry(dialog, width=30)
        name_entry.grid(row=0, column=1, padx=10, pady=10)
        
        # Category
        ttk.Label(dialog, text="Category:").grid(row=1, column=0, padx=10, pady=10, sticky='w')
        category_entry = ttk.Entry(dialog, width=30)
        category_entry.grid(row=1, column=1, padx=10, pady=10)
        
        # Deadline with DateEntry widget
        ttk.Label(dialog, text="Deadline:").grid(row=2, column=0, padx=10, pady=10, sticky='w')
        deadline_frame = ttk.Frame(dialog)
        deadline_frame.grid(row=2, column=1, padx=10, pady=10, sticky='w')
        
        # Create date selector (more user-friendly)
        cal = DateEntry(deadline_frame, width=12, background='darkblue',
                      foreground='white', borderwidth=2, date_pattern='yyyy-mm-dd')
        cal.pack(padx=10, pady=10)
        
        # Priority checkbox
        priority_var = tk.BooleanVar(value=False)
        priority_check = ttk.Checkbutton(dialog, text="Mark as Priority/Urgent", variable=priority_var)
        priority_check.grid(row=3, column=0, columnspan=2, padx=10, pady=5, sticky='w')
        
        # Description
        ttk.Label(dialog, text="Description:").grid(row=4, column=0, padx=10, pady=10, sticky='w')
        description_text = tk.Text(dialog, width=30, height=5)
        description_text.grid(row=4, column=1, padx=10, pady=10)
        
        # Buttons
        button_frame = ttk.Frame(dialog)
        button_frame.grid(row=5, column=0, columnspan=2, pady=20)
        
        # Save function
        def save_task():
            name = name_entry.get()
            if not name:
                messagebox.showerror("Error", "Task name is required")
                return
                
            try:
                category = category_entry.get() if category_entry.get() else None
                description = description_text.get("1.0", tk.END).strip() or None
                
                # Get date from DateEntry widget - convert to datetime object
                selected_date = cal.get_date()
                
                # Create task
                task_id = self.task_controller.create_task(
                    name=name, 
                    description=description, 
                    category=category, 
                    deadline=selected_date,
                    priority=priority_var.get()
                )
                
                self.refresh_tasks()
                self.status_label.config(text=f"Task '{name}' created")
                dialog.destroy()
                
                # Select the new task
                self.task_tree.selection_set(task_id)
                self.task_tree.focus(task_id)
                self.on_task_select(None)
            except Exception as e:
                messagebox.showerror("Error", str(e))
        
        ttk.Button(button_frame, text="Save", command=save_task).pack(side=tk.LEFT, padx=10)
        ttk.Button(button_frame, text="Cancel", command=dialog.destroy).pack(side=tk.LEFT, padx=10)
        
        # Set focus on name entry
        name_entry.focus_set()
        
    def edit_task(self):
        """Edit the selected task"""
        if not self.active_task_id:
            messagebox.showerror("Error", "Please select a task first")
            return
            
        # Get the selected task
        task = self.task_controller.get_task(self.active_task_id)
        if not task:
            messagebox.showerror("Error", "Could not load task data")
            return
        
        # Create a dialog window
        dialog = tk.Toplevel(self)
        dialog.title("Edit Task")
        dialog.geometry("400x350")
        dialog.configure(bg="#2c3e50")
        dialog.transient(self)  # Make it modal
        dialog.grab_set()  # Make it modal
        
        # Task name
        ttk.Label(dialog, text="Task Name:").grid(row=0, column=0, padx=10, pady=10, sticky='w')
        name_entry = ttk.Entry(dialog, width=30)
        name_entry.grid(row=0, column=1, padx=10, pady=10)
        name_entry.insert(0, task['name'])
        
        # Category
        ttk.Label(dialog, text="Category:").grid(row=1, column=0, padx=10, pady=10, sticky='w')
        category_entry = ttk.Entry(dialog, width=30)
        category_entry.grid(row=1, column=1, padx=10, pady=10)
        if task['category']:
            category_entry.insert(0, task['category'])
        
        # Deadline with DateEntry widget
        ttk.Label(dialog, text="Deadline:").grid(row=2, column=0, padx=10, pady=10, sticky='w')
        deadline_frame = ttk.Frame(dialog)
        deadline_frame.grid(row=2, column=1, padx=10, pady=10, sticky='w')
        
        # Create date selector with current date if available
        cal = DateEntry(deadline_frame, width=12, background='darkblue',
                    foreground='white', borderwidth=2, date_pattern='yyyy-mm-dd')
        cal.pack(padx=10, pady=10)
        
        # Set the current deadline date if exists
        if task['deadline']:
            if isinstance(task['deadline'], str):
                try:
                    # Parse the date string
                    deadline_date = datetime.datetime.strptime(task['deadline'], "%Y-%m-%d").date()
                    cal.set_date(deadline_date)
                except ValueError:
                    pass  # Use default date if parsing fails
            else:
                # It's already a datetime object
                cal.set_date(task['deadline'])
        
        # Priority checkbox
        priority_var = tk.BooleanVar(value=task['priority'])
        priority_check = ttk.Checkbutton(dialog, text="Mark as Priority/Urgent", variable=priority_var)
        priority_check.grid(row=3, column=0, columnspan=2, padx=10, pady=5, sticky='w')
        
        # Description
        ttk.Label(dialog, text="Description:").grid(row=4, column=0, padx=10, pady=10, sticky='w')
        description_text = tk.Text(dialog, width=30, height=5)
        description_text.grid(row=4, column=1, padx=10, pady=10)
        
        # Insert current description if available
        if task['description']:
            description_text.insert("1.0", task['description'])
        
        # Buttons
        button_frame = ttk.Frame(dialog)
        button_frame.grid(row=5, column=0, columnspan=2, pady=20)
        
        # Save function
        def save_edited_task():
            name = name_entry.get()
            if not name:
                messagebox.showerror("Error", "Task name is required")
                return
                
            try:
                category = category_entry.get() if category_entry.get() else None
                description = description_text.get("1.0", tk.END).strip() or None
                
                # Get date from DateEntry widget
                selected_date = cal.get_date()
                
                # Update task
                self.task_controller.update_task(
                    self.active_task_id,
                    name=name, 
                    description=description, 
                    category=category, 
                    deadline=selected_date,
                    priority=priority_var.get()
                )
                
                self.refresh_tasks()
                self.status_label.config(text=f"Task '{name}' updated")
                dialog.destroy()
                
                # Re-select the task to update details view
                self.task_tree.selection_set(self.active_task_id)
                self.task_tree.focus(self.active_task_id)
                self.on_task_select(None)
            except Exception as e:
                messagebox.showerror("Error", str(e))
        
        ttk.Button(button_frame, text="Save", command=save_edited_task).pack(side=tk.LEFT, padx=10)
        ttk.Button(button_frame, text="Cancel", command=dialog.destroy).pack(side=tk.LEFT, padx=10)
        
        # Set focus on name entry
        name_entry.focus_set()

    
    def delete_task(self):
        """Delete the selected task"""
        if not self.active_task_id:
            messagebox.showerror("Error", "Please select a task first")
            return
            
        if messagebox.askyesno("Confirm", "Are you sure you want to delete this task?"):
            try:
                self.task_controller.delete_task(self.active_task_id)
                self.refresh_tasks()
                self.active_task_id = None
                self.current_task_label.config(text="No Task Selected")
                self.status_label.config(text="Task deleted")
                
                # Clear details
                self.on_task_select(None)
            except Exception as e:
                messagebox.showerror("Error", str(e))
    
    def toggle_complete(self):
        """Toggle the completion status of the selected task"""
        if not self.active_task_id:
            messagebox.showerror("Error", "Please select a task first")
            return
            
        try:
            task = self.task_controller.get_task(self.active_task_id)
            new_status = not task['completed']
            
            self.task_controller.update_task(
                self.active_task_id, 
                completed=new_status
            )
            
            status_text = "completed" if new_status else "reopened"
            self.status_label.config(text=f"Task {status_text}")
            
            # Refresh the UI
            self.refresh_tasks()
            self.on_task_select(None)
        except Exception as e:
            messagebox.showerror("Error", str(e))
    
    def toggle_priority(self):
        """Toggle the priority status of the selected task"""
        if not self.active_task_id:
            messagebox.showerror("Error", "Please select a task first")
            return
            
        try:
            task = self.task_controller.get_task(self.active_task_id)
            new_status = not task['priority']
            
            self.task_controller.update_task(
                self.active_task_id, 
                priority=new_status
            )
            
            status_text = "marked as priority" if new_status else "unmarked as priority"
            self.status_label.config(text=f"Task {status_text}")
            
            # Refresh the UI
            self.refresh_tasks()
            self.on_task_select(None)
        except Exception as e:
            messagebox.showerror("Error", str(e))
    
    def export_data(self):
        """Export task data to CSV"""
        filename = filedialog.asksaveasfilename(
            defaultextension=".csv",
            filetypes=[("CSV files", "*.csv"), ("All files", "*.*")]
        )
        if filename:
            try:
                # Call export controller here
                # For now we'll just show a message
                self.status_label.config(text=f"Data exported to {filename}")
            except Exception as e:
                messagebox.showerror("Error", str(e))
