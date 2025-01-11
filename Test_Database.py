from datetime import date, timedelta

from DBManager import DatabaseManager
from HabitManager import Habit


class TestHabit:
    def setup_method(self):
        """Setup method to initialize a test database."""
        self.db_manager = DatabaseManager(db_name="test_db")

    def test_create_and_save_habits(self):
        """Test creating and saving habits to the test database."""
        habit1 = Habit(name="Exercise", description="Exercise daily", recurrence="Daily")
        habit2 = Habit(name="Read Books", description="Read a book every week", recurrence="Weekly")
        habit3 = Habit(name="Meditation", description="Practice mindfulness daily", recurrence="Daily")
        self.db_manager.save_habit(habit1)
        self.db_manager.save_habit(habit2)
        self.db_manager.save_habit(habit3)
    
        habits = self.db_manager.fetch_all_habits()
        assert len(habits) == 3
        assert habits[0][1] == "Exercise"
        assert habits[1][1] == "Read Books"
        assert habits[2][1] == "Meditation"
    
    def test_get_current_streak(self):
        """Test the get_current_streak method to return the correct streak value."""
        test_habit = Habit(name="Exercise", description="Exercise daily", recurrence="Daily")
        self.db_manager.save_habit(test_habit)
        test_habit = self.db_manager.get_data_from_last_created_habit()
        habit_id, name, _, recurrence, *_ = test_habit
    
        # Checkoff completions for the habit
        self.db_manager.add_checkoff_entry(habit_id, checkoff_date=date.today())
        self.db_manager.add_checkoff_entry(habit_id, checkoff_date=date.today()-timedelta(days=1))
        self.db_manager.add_checkoff_entry(habit_id, checkoff_date=date.today()-timedelta(days=2))
    
        # Validate the current streak is accurate
        streak = self.db_manager.get_current_streak(habit_id)
        assert streak == 3
    
    def test_get_longest_streak(self):
        """Test the get_longest_streak method to return the correct longest streak value."""
        test_habit = Habit(name="Exercise", description="Exercise daily", recurrence="Daily")
        self.db_manager.save_habit(test_habit)
        test_habit = self.db_manager.get_data_from_last_created_habit()
        habit_id, name, _, recurrence, *_ = test_habit
        
        # Checkoff completions for the habit with a break in between
        self.db_manager.add_checkoff_entry(habit_id, "2023-10-01")
        self.db_manager.add_checkoff_entry(habit_id, "2023-10-02")
        self.db_manager.add_checkoff_entry(habit_id, "2023-10-04")
        self.db_manager.add_checkoff_entry(habit_id, "2023-10-05")
        self.db_manager.add_checkoff_entry(habit_id, "2023-10-06")
        self.db_manager.add_checkoff_entry(habit_id, "2023-10-07")
        
        # Validate the longest streak is accurate
        longest_streak = self.db_manager.get_longest_streak(habit_id)
        assert longest_streak == 4
    
    def teardown_method(self):
        """Teardown method to remove the test database and clear completions."""
        self.db_manager.delete_database()