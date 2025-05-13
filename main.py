# main.py - Entry point for the Time Management application

# Import controllers and database
from app.controllers.task_controller import TaskController
from app.controllers.timer_controller import TimerController
from app.models.database import Database

# Import the UI
from app.views.gui.main_window import TimeApp

def main():
    """Initialize and start the application"""
    # Setup database and controllers
    db = Database()
    task_controller = TaskController(db)
    timer_controller = TimerController(db)
    
    # Start UI
    app = TimeApp(task_controller, timer_controller)
    app.mainloop()
    
    # Cleanup when app closes
    db.close()

if __name__ == "__main__":
    main()
