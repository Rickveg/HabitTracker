import sqlite3
from datetime import date, datetime, timedelta, timezone


class DatabaseManager:
    """
    Provides functionality to manage a database of habits and their check-offs.

    This class supports operations such as creating and managing habits, managing
    check-off data, and performing analysis on checked-off habits. It connects to
    and interacts with an SQLite database to store and retrieve habit-related data.
    It provides methods for creating tables, inserting, updating, deleting data,
    and performing advanced queries for habit tracking and analytics purposes.
    """
    def __init__(self, db_name='main.db'):
        self.db_name = db_name
        self.connection = sqlite3.connect(self.db_name)
        self.cursor = self.connection.cursor()
        self.create_tables()

    def create_tables(self):
        """Creates necessary tables in the database."""
        self.cursor.execute('''CREATE TABLE IF NOT EXISTS habit (
                                id INTEGER PRIMARY KEY AUTOINCREMENT,
                                name TEXT,
                                description TEXT,
                                recurrence TEXT,
                                creation_date TEXT,
                                completion_date TEXT,
                                status TEXT
                             )''')
        self.cursor.execute('''CREATE TABLE IF NOT EXISTS checkoff (
                                id INTEGER PRIMARY KEY AUTOINCREMENT,
                                habit_id INTEGER,
                                checkoff_date TEXT,
                                FOREIGN KEY (habit_id) REFERENCES habit (id)
                             )''')
        self.connection.commit()

    def execute_query(self, query, params=()):
        """Executes a query with optional parameters."""
        self.cursor.execute(query, params)
        self.connection.commit()

    def fetch_all(self, query, params=()):
        """Fetches all results for a query."""
        self.cursor.execute(query, params)
        return self.cursor.fetchall()
    
    def empty_database(self):
        """Clears all rows from tables and resets primary keys when both tables are empty."""
        habit_count = self.fetch_all("SELECT COUNT(*) FROM habit")[0][0]
        checkoff_count = self.fetch_all("SELECT COUNT(*) FROM checkoff")[0][0]
    
        if habit_count == 0 and checkoff_count == 0:
            self.execute_query("DELETE FROM habit")
            self.execute_query("DELETE FROM checkoff")
            self.execute_query("DELETE FROM sqlite_sequence WHERE name IN ('habit', 'checkoff')")

    # HABIT MANAGEMENT

    def save_habit(self, habit):
        """Saves a new habit to the database."""
        query = '''INSERT INTO habit (name, description, recurrence, creation_date, completion_date, status) 
                   VALUES (?, ?, ?, ?, ?, ?)'''
        self.execute_query(query, (
            habit.name, habit.description, habit.recurrence, habit.creation_date, habit.completion_date, habit.status))

    def update_habit(self, habit_id, name, description, recurrence):
        """Update an existing habit."""
        query = '''UPDATE habit SET name = ?, description = ?, recurrence = ? WHERE id = ?'''
        self.execute_query(query, (name, description, recurrence, habit_id))

    def delete_habit(self, habit_id):
        """Delete a habit and its check-offs from the database."""
        self.execute_query("DELETE FROM checkoff WHERE habit_id = ?", (habit_id,))
        self.execute_query("DELETE FROM habit WHERE id = ?", (habit_id,))

    def delete_check_offs(self, habit_id):
        """Delete all check-offs for a given habit."""
        self.execute_query("DELETE FROM checkoff WHERE habit_id = ?", (habit_id,))

    def add_checkoff_entry(self, habit_id, checkoff_date):
        """Add a check-off entry."""
        query = '''INSERT INTO checkoff (habit_id, checkoff_date) VALUES (?, ?)'''
        self.execute_query(query, (habit_id, checkoff_date))

    def complete_habit(self, habit_id, status='complete', completion_date=date.today()):
        """Add a completion date and change status to complete"""
        if completion_date is None:
            completion_date = date.today().isoformat()
        query = '''UPDATE habit SET completion_date = ?, status = ? WHERE id = ?'''
        self.execute_query(query, (completion_date, status, habit_id))

    # GETTERS

    def fetch_all_habits(self):
        """Retrieve all habits."""
        query = "SELECT * FROM habit"
        return self.fetch_all(query)

    def fetch_all_active_habits(self):
        """Retrieve all active habits."""
        query = "SELECT * FROM habit WHERE status = 'active'"
        return self.fetch_all(query)

    def get_data_from_last_created_habit(self):
        """Retrieve all data of the last created habit."""
        query = "SELECT * FROM habit WHERE id = (SELECT MAX(id) FROM habit)"
        result = self.fetch_all(query)
        return result[0] if result else None
    
    def get_habit_id_from_last_habit(self):
        """Retrieve the ID of the last created habit."""
        query = "SELECT id FROM habit WHERE id = (SELECT MAX(id) FROM habit)"
        result = self.fetch_all(query)
        return result[0][0] if result else None

     
    def get_creation_date(self, habit_id):
        """Retrieve the creation date of a habit."""
        query = "SELECT creation_date FROM habit WHERE id = ?"
        result = self.fetch_all(query, (habit_id,))
        return result[0][0] if result else None

    def get_completion_date(self, habit_id):
        """Retrieve the completion date of a habit."""
        query = "SELECT completion_date FROM habit WHERE id = ?"
        completion_date = self.fetch_all(query, (habit_id,))
        return completion_date[0][0] if completion_date else None

    def get_status(self, habit_id):
        """Retrieve the status of a habit."""
        query = "SELECT status FROM habit WHERE id = ?"
        status = self.fetch_all(query, (habit_id,))
        return status[0][0] if status else None

    def get_recurrence(self, habit_id):
        """Retrieve the recurrence of a habit (Daily or Weekly)."""
        query = "SELECT recurrence FROM habit WHERE id = ?"
        recurrence = self.fetch_all(query, (habit_id,))
        return recurrence[0][0] if recurrence else None

    # ANALYSIS

    def fetch_daily_checkoff_info(self, habit_id):
        """Fetch the daily check-off dates and details for the given habit_id."""
        query = '''SELECT checkoff_date FROM checkoff WHERE habit_id = ? ORDER BY checkoff_date'''
        return self.fetch_all(query, (habit_id,))

    def is_habit_checked_off_today(self, habit_id):
        """Check if a daily habit has been checked_off today (UTC normalized)."""
        today = datetime.now(timezone.utc).date().isoformat()
        query = '''SELECT 1 FROM checkoff WHERE habit_id = ? AND checkoff_date = ?'''
        result = self.fetch_all(query, (habit_id, today))
        return len(result) > 0

    def is_habit_checked_off_this_week(self, habit_id):
        """Check if a weekly habit has been checked_off this week (UTC normalized)"""
        today = datetime.now(timezone.utc).date()
        start_of_week = today - timedelta(days=today.weekday())
        query = '''SELECT 1 FROM checkoff WHERE habit_id = ? AND checkoff_date >= ?'''
        result = self.fetch_all(query, (habit_id, start_of_week.isoformat()))
        return len(result) > 0

    def is_habit_checked_off_weekly(self, habit_id, period):
        """Check if a habit has been checked off during the given weekly period (year, week)."""
        year, week = period  # Expect period to be in the format (year, week)
        start_of_week = datetime.fromisocalendar(year, week, 1).date()  # First day of the week (Monday)
        end_of_week = start_of_week + timedelta(days=6)  # Last day of the week (Sunday)
        query = '''SELECT 1 FROM checkoff WHERE habit_id = ? AND checkoff_date BETWEEN ? AND ?'''
        result = self.fetch_all(query, (habit_id, start_of_week.isoformat(), end_of_week.isoformat()))
        return len(result) > 0

    def is_habit_checked_off_given_day(self, habit_id, given_day):
        """Check if a daily habit has been checked_off for the given day (UTC normalized)."""
        query = '''SELECT 1 FROM checkoff WHERE habit_id = ? AND checkoff_date = ?'''
        result = self.fetch_all(query, (habit_id, given_day.isoformat()))
        return len(result) > 0

    def get_current_streak(self, habit_id):
        """Calculate the current streak for a habit, taking into account the habit's recurrence."""
        recurrence = self.get_recurrence(habit_id)
        query = '''SELECT checkoff_date FROM checkoff WHERE habit_id = ? ORDER BY checkoff_date DESC'''
        checkoffs = self.fetch_all(query, (habit_id,))

        # Calculate streak
        current_streak = 0
        if recurrence == 'Daily':
            increment = timedelta(days=1)
        elif recurrence == 'Weekly':
            increment = timedelta(weeks=1)
        else:
            raise ValueError("Unsupported recurrence type")

        current_date = date.today()
        for checkoff in checkoffs:
            try:
                checkoff_date = date.fromisoformat(checkoff[0].split("T")[0])
            except ValueError:
                continue
            if checkoff_date == current_date:
                current_streak += 1
                current_date -= increment
            else:
                break
        return current_streak

    def get_longest_streak(self, habit_id):
        """Calculate the longest streak for a habit, taking into account that habit's recurrence."""
        recurrence = self.get_recurrence(habit_id)
        query = '''SELECT checkoff_date FROM checkoff WHERE habit_id = ? ORDER BY checkoff_date '''
        checkoffs = self.fetch_all(query, (habit_id,))

        longest_streak = 0
        streak = 0
        previous_date = None

        for checkoff in checkoffs:
            try:
                checkoff_date = date.fromisoformat(checkoff[0].split("T")[0])
            except ValueError:
                continue

            if recurrence == 'Daily':
                increment = timedelta(days=1)
            elif recurrence == 'Weekly':
                increment = timedelta(weeks=1)
            else:
                raise ValueError("Unsupported recurrence type")

            if previous_date is None or checkoff_date == previous_date + increment:
                streak += 1
            else:
                longest_streak = max(longest_streak, streak)
                streak = 1  # Restart streak

            previous_date = checkoff_date

        longest_streak = max(longest_streak, streak)
        return longest_streak

    def get_habit_performance(self, habit_id, creation_date):
        """Calculate the percentage of times a habit has been checked off."""
        recurrence = self.get_recurrence(habit_id)
        query = '''SELECT COUNT(*) FROM checkoff WHERE habit_id = ?'''
        result = self.fetch_all(query, (habit_id,))
        checked_off_count = result[0][0] if result else 0

        habit_creation_date = date.fromisoformat(creation_date)
        if recurrence == "Daily":
            total_days = (date.today() - habit_creation_date).days + 1  # Include the creation day
        elif recurrence == "Weekly":
            total_days = ((date.today() - habit_creation_date).days // 7) + 1  # Total weeks since creation
        else:
            raise ValueError("Unsupported recurrence type")

        return (checked_off_count / total_days) * 100 if total_days > 0 else 0