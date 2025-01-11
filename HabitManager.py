import random
from datetime import date, datetime, timedelta

import questionary

from DBManager import DatabaseManager
from Habit import Habit


class HabitManager:
    """
    The `HabitManager` class provides utilities to perform operations related to habits and including the following:

     - create_habit: Creates a new habit, prompting the user to add a name, a description and a recurrence.
     - check_off_habit: Checks-off a selected habit.
     - edit_habit: Allows editing an existing habit. The user can change either the name, description, or recurrence.
     - complete_habit: Marks a habit as completed in the database.
     - delete_habit: Deletes a habit and all its check-offs from the database.
     - create_predefined_habits: Creates predefined habits and generates check-off entries.

    """
    def __init__(self, text_theme):
        self.db_manager = DatabaseManager()
        self.console, self.custom_style = text_theme

    def create_habit(self):
        """ Creates a new habit by prompting the user for input and saves it to the database."""

        # Prompt the user to name the habit. Also validates the name field isn't empty; only spaces or duplicate entry.
        name = questionary.text("Enter the name of your new habit:", validate=lambda text: (
            "You must name your habit. Your habit's name cannot be empty spaces"
            if text.strip() == "" else
            "A habit with this name already exists. Please choose a different name."
            if any(habit[1] == text.strip() for habit in self.db_manager.fetch_all_habits())
            else True
        )).ask()

        # Prompt the user to add a description. If field is empty asks user for confirmation.
        description = questionary.text("Enter a description for the habit:").ask()
        while description.strip() == "":
            if not questionary.confirm("Are you sure you want to leave the description empty?").ask():
                description = questionary.text("Enter a valid description for the habit:").ask()
        
        # Prompt the user to choose a recurrence out of Daily or Weekly.
        recurrence = questionary.select("Choose the recurrence for the habit:",
                                        choices=["Daily", "Weekly"], style=self.custom_style).ask()

        # Save new habit into database and display outcome message to user.
        try:
            self.db_manager.save_habit(Habit(name=name, description=description, recurrence=recurrence))
            self.console.print(f"\nHabit '{name}' created successfully!\n", style="success")
            self.console.print(
                f"[title]Name: [/title]\t\t{name}\n[title]Description: [/title]\t{description}\n"
                f"[title]Recurrence: [/title]\t{recurrence}\n", style="info"
            )
        except Exception as e:
            raise RuntimeError(f"An error occurred while saving the habit: {e}")

    def check_off_habit(self, selected_habit):
        """ Checks-off a daily or weekly habit, upon validating whether it has already been checked off."""
        if selected_habit in [None, "Cancel"] or self.db_manager.get_status(selected_habit[0])[0] == "Complete":
            self.console.print("No active habits to check-off. You must first create a new habit.", style="warning")
            return

        habit_id, name, _, recurrence, *_ = selected_habit

        # Check whether habit has already been checked off today (daily) or this week (weekly)
        checked_off = (
            self.db_manager.is_habit_checked_off_today(habit_id)
            if recurrence == "Daily"
            else self.db_manager.is_habit_checked_off_this_week(habit_id)
        )

        if checked_off:
            self.console.print("Habit already checked off.", style="warning")
        else:
            self.db_manager.add_checkoff_entry(habit_id, checkoff_date=date.today())
            self.console.print(
                f"\nHabit [yellow italic]{name}[/] which takes place [yellow italic]{recurrence}[/] "
                f"successfully checked-Off.\n", style="success"
            )

    def edit_habit(self, selected_habit):
        """ Edits an existing habit by updating its name, description, or recurrence."""
        if selected_habit in [None, "Cancel"]:
            return

        habit_id, name, description, recurrence, *_ = selected_habit

        # Allow editing only of Active habits. Warn user habit has been completed.
        if self.db_manager.get_status(habit_id)[0] == "Complete":
            self.console.print("Habit cannot be edited because it has already been completed.", style="warning")
            return

        # Prompt user to text new value for each attribute. Have by default existing values.
        name = questionary.text("Enter new name:", default=name).ask()
        description = questionary.text("Enter new description:", default=description).ask()
        new_recurrence = questionary.select("Choose new recurrence:", choices=["Daily", "Weekly"],
                                            style=self.custom_style, default=recurrence).ask()

        # Verify if user wishes to change recurrence. Warn user that changing recurrence deletes all check off entries.
        if new_recurrence != recurrence:
            self.console.print(
                f"You have selected a different habit recurrence! "
                f"Changing the recurrence will [bold red underline]delete[/bold red underline] "
                f"all previous check-offs.", style="warning"
            )
            if not questionary.confirm(
                    f"Proceed with changing '{recurrence}' to '{new_recurrence}'?"
            ).ask():
                self.console.print("Editing canceled.", style="warning")
                return

            self.db_manager.delete_check_offs(habit_id)
        
        # Save edited changes in database.
        try:
            self.db_manager.update_habit(habit_id, name, description, new_recurrence)
            self.console.print(f"\nHabit '{name}' edited successfully!\n", style="success")
            self.console.print(
                f"[title]Name: [/title]\t\t{name}\n[title]Description: [/title]\t{description}\n"
                f"[title]Recurrence: [/title]\t{new_recurrence}\n", style="info"
            )
        except Exception as e:
            raise RuntimeError(f"An error occurred while saving the habit: {e}")

    def complete_habit(self, selected_habit):
        """ Marks a habit as completed by the user. """
        if selected_habit in [None, "Cancel"]:
            return

        try:
            # Completes selected habit
            self.db_manager.complete_habit(selected_habit[0])
            self.console.print(f"\nHabit '{selected_habit[1]}' completed successfully!\n", style="success")
        except Exception as e:
            self.console.print(f"An error occurred while completing the habit: {e}", style="error")

    def delete_habit(self, selected_habit):
        """ Deletes a habit and all its check-offs. Lets the user know action cannot be reversed. """
        if selected_habit in [None, "Cancel"]:
            return

        try:
            # Prompts user to confirm deletion.
            if questionary.confirm(
                    f"Are you sure you want to delete the habit '{selected_habit[1]}'? This action cannot be undone."
            ).ask():
                self.db_manager.delete_habit(selected_habit[0])
                self.console.print(f"The habit '{selected_habit[1]}' has been successfully deleted.", style="success")
                # Delete database if there are no habits left
                if not self.db_manager.fetch_all_habits():
                    self.db_manager.delete_empty_database()
                    self.console.print("All habits have been deleted. Database has been deleted.", style="success")
            else:
                self.console.print("Deletion canceled.", style="warning")
        except Exception as e:
            self.console.print(f"An error occurred while deleting the habit: {e}", style="error")

    def create_predefined_habits(self):
        """
        Creates predefined habits with check-off entries to mimic user activity, ensuring no duplicate dates.
        """

        # Helper function to generate unique random check-off dates
        def generate_random_dates(start_date, end_date, num_dates, min_streak_length=5, recurrence="Daily"):
            delta = end_date - start_date
            dates = set()  # Use a set to ensure no duplicates

            if recurrence == "Weekly":
                total_weeks = (delta.days // 7) + 1
                available_dates = [start_date + timedelta(weeks=i) for i in range(total_weeks)]
            else:  # Daily
                available_dates = [start_date + timedelta(days=i) for i in range(delta.days + 1)]

            # Ensure enough dates exist
            num_dates = min(len(available_dates), num_dates)

            # Generate the minimum streak
            streak_start_idx = random.randint(0, len(available_dates) - min_streak_length)
            streak_dates = available_dates[streak_start_idx:streak_start_idx + min_streak_length]
            dates.update(streak_dates)

            # Generate remaining random dates if needed
            while len(dates) < num_dates:
                random_date = random.choice(available_dates)
                dates.add(random_date)  # Ensures no duplicate dates are added

            return sorted(dates)

        current_date = datetime.today()
        six_months_ago = current_date - timedelta(days=180)
        four_months_ago = current_date - timedelta(days=120)
        three_months_ago = current_date - timedelta(days=90)

        predefined_habits = [
            {
                "name": "Drink 1.5l of Water",
                "description": "Keep Hydrated",
                "recurrence": "Daily",
                "creation_date": six_months_ago.date(),
                "num_checkoffs": 130,
                "min_streak_length": 8,
            },
            {
                "name": "Have a Siesta",
                "description": "Reset the brain after work",
                "recurrence": "Daily",
                "creation_date": four_months_ago.date(),
                "num_checkoffs": 73,
                "min_streak_length": 7,
            },
            {
                "name": "Read a Book",
                "description": "Remain intellectual",
                "recurrence": "Weekly",
                "creation_date": six_months_ago.date(),
                "num_checkoffs": 23,
                "min_streak_length": 2,
            },
            {
                "name": "Cook Special Meal",
                "description": "Impress the family with new skills",
                "recurrence": "Weekly",
                "creation_date": three_months_ago.date(),
                "num_checkoffs": 9,
                "min_streak_length": 1,
            },
            {
                "name": "Run",
                "description": "Go for daily run in the mountains",
                "recurrence": "Daily",
                "creation_date": six_months_ago.date(),
                "num_checkoffs": 148,
                "min_streak_length": 10,
            },
        ]

        for habit_data in predefined_habits:
            habit = Habit(
                name=habit_data["name"],
                description=habit_data["description"],
                recurrence=habit_data["recurrence"],
                creation_date=habit_data["creation_date"]
            )
            self.db_manager.save_habit(habit)

            # Fetch the newly created habit details
            habit_record = self.db_manager.get_data_from_last_created_habit()
            habit_id = habit_record[0]

            # Generate unique checkoff dates
            random_dates = generate_random_dates(
                start_date=six_months_ago,
                end_date=current_date,
                num_dates=habit_data["num_checkoffs"],
                min_streak_length=habit_data["min_streak_length"],
                recurrence=habit_data["recurrence"],
            )

            # Add the checkoff entries to the database
            for checkoff_date in random_dates:
                self.db_manager.add_checkoff_entry(habit_id, checkoff_date=checkoff_date.strftime("%Y-%m-%d"))