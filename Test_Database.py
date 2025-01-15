from datetime import date, timedelta

from DBManager import DatabaseManager
from HabitManager import Habit, HabitManager


class TestHabit:
    def setup_method(self):
        """Setup method to initialize a test database."""
        self.db_manager = DatabaseManager(db_name="test_db")

    def test_create_predefined_habits(self):
        """Test the create_predefined_habits method from HabitManager."""
        predefined_habits = [
            Habit(name="Drink Water", description="Stay hydrated", recurrence="Daily"),
            Habit(name="Walk 10k Steps", description="Achieve 10k steps in a day", recurrence="Daily"),
            Habit(name="Weekly Meeting", description="Attend the weekly meeting", recurrence="Weekly"),
        ]
        # Mock the method to create predefined habits in HabitManager
        for habit in predefined_habits:
            self.db_manager.save_habit(habit)
    
        # Fetch habits from the database
        saved_habits = self.db_manager.fetch_all_habits()
        
        # Validate that all predefined habits were saved correctly
        assert len(saved_habits) == len(predefined_habits)
        for i, habit in enumerate(predefined_habits):
            assert saved_habits[i][1] == habit.name
            assert saved_habits[i][2] == habit.description
            assert saved_habits[i][3] == habit.recurrence
    
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
    
    def test_get_longest_streak_daily(self):
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

    def test_get_longest_streak_weekly(self):
        """Test the get_longest_streak method to return the correct longest streak value."""
        test_habit = Habit(name="Exercise", description="Exercise weekly", recurrence="Weekly")
        self.db_manager.save_habit(test_habit)
        test_habit = self.db_manager.get_data_from_last_created_habit()
        habit_id, name, _, recurrence, *_ = test_habit

        # Checkoff completions for the habit with a break in between
        self.db_manager.add_checkoff_entry(habit_id, "2023-10-01")
        self.db_manager.add_checkoff_entry(habit_id, "2023-10-08")
        self.db_manager.add_checkoff_entry(habit_id, "2023-10-22")
        self.db_manager.add_checkoff_entry(habit_id, "2023-10-29")
        self.db_manager.add_checkoff_entry(habit_id, "2023-11-05")

        # Validate the longest streak is accurate
        longest_streak = self.db_manager.get_longest_streak(habit_id)
        assert longest_streak == 3
    
    def teardown_method(self):
        """Teardown method to remove the test database and clear completions."""
        self.db_manager.delete_database()