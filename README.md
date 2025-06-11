# Todo App

A robust, multi-role To-Do List web application built with Django.

## Features

- **User Authentication**: Sign up, login, logout functionality with role-based access control (Admin, User)
- **Task Management**:
  - **Admin**: Full control (create, edit, delete, assign, view all tasks)
  - **User**: Limited access (view assigned tasks, mark as completed)
- **Task Properties**:
  - Title, description, deadline, priority level (Low/Medium/High)
  - Status tracking (Pending, In Progress, Completed)
  - Assignment to specific users
- **Dashboard**:
  - Task statistics and summary views
  - Visual representation of task priorities and status
- **Comments System**:
  - Users and Admins can leave comments on tasks
  - Track discussion history
- **Search & Filtering**:
  - Filter tasks by user, status, priority, deadline
  - Search functionality for finding specific tasks

## Setup Instructions

### Prerequisites

- Python 3.8+
- pip (Python package manager)

### Installation

1. Clone the repository:
   ```
   git clone <repository-url>
   cd todo-app
   ```

2. Create and activate a virtual environment:
   ```
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install dependencies:
   ```
   pip install -r requirements.txt
   ```

4. Apply database migrations:
   ```
   python manage.py migrate
   ```

5. Set up initial data (creates admin and regular user accounts):
   ```
   python manage.py setup_todo_app
   ```

6. Run the development server:
   ```
   python manage.py runserver
   ```

7. Access the application at http://127.0.0.1:8000/

### Default Login Credentials

- **Admin User**:
  - Username: admin
  - Password: adminpassword

- **Regular User**:
  - Username: user
  - Password: userpassword

## Project Structure

- `todo_project/`: Main Django project settings
- `todo_app/`: Todo application code
  - `models.py`: Database models (Task, Comment)
  - `views.py`: View functions
  - `forms.py`: Form classes
  - `urls.py`: URL routing
  - `templates/`: HTML templates
  - `management/commands/`: Custom management commands

## License

This project is licensed under the MIT License - see the LICENSE file for details. 