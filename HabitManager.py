import random
from datetime import date, datetime, timedelta

import questionary
from rich.console import Console

from DBManager import DatabaseManager
from Habit import Habit

console = Console()


def print_habit_information(name, description, recurrence):
    """
    Prints detailed information about a habit including its name, description, and
    recurrence details to the console.

    :param name: The name of the habit.
    :type name: str
    :param description: A brief description of the habit.
    :type description: str
    :param recurrence: The recurrence frequency of the habit.
    :type recurrence: str
    :return: None
    """
    console.print(f"[bold]Name: \t\t\t[bright_blue]{name}[/]\n"
                  f"Description: \t\t{description}\n"
                  f"Recurrence: \t\t{recurrence}[/]")


class HabitManager:
    """
    Handles the management of habits, including creation, editing, check-offs, and deletions.

    The `HabitManager` class provides utilities to perform operations related to habits such as creating
    predefined habits, adding custom habits, and managing user interactions for habit-related actions.

    :ivar db_manager: An instance of DatabaseManager, which handles database operations for storing
        and managing habit details.
    :type db_manager: DatabaseManager
    """
    def __init__(self):
        self.db_manager = DatabaseManager()

    def create_predefined_habits(self):
        """
        This function creates a set of predefined habits, saves them to the database,
        and generates check-off entries to mimic user activity for these habits over
        a specified time period. It utilizes random date generation to produce mock
        data that simulates user interactions with the habits, including maintaining
        streaks.

        The generated and stored habits include:
        1. Drink 1.5l of Water
        2. Have a Siesta
        3. Read a Book
        4. Cook Special Meal
        5. Run

        The function configures each habit differently in terms of creation dates,
        recurrence types (daily or weekly), and check-off data. It employs the
        `generate_random_dates` helper function to create random check-off dates
        while ensuring predefined streak lengths for each habit.

        :param self: The instance of the class that contains the method.

        """

        # Helper function to generate random check-off dates
        def generate_random_dates(start_date, end_date, num_dates, min_streak_length=5, given_recurrence="Daily"):
            delta = end_date - start_date
            if given_recurrence == "Weekly":
                available_weeks = (delta.days // 7) + 1
                if num_dates > available_weeks:
                    num_dates = available_weeks
                random_given_dates = random.sample(
                    [start_date + timedelta(weeks=i) for i in range(available_weeks)],
                    max(0, num_dates - min_streak_length)
                )
                streak_start = random.choice(
                    [start_date + timedelta(weeks=i) for i in range(available_weeks - min_streak_length + 1)])
                streak_dates = [streak_start + timedelta(weeks=i) for i in range(min_streak_length)]
            else:
                available_days = delta.days + 1
                if num_dates > available_days:
                    num_dates = available_days
                random_given_dates = random.sample(
                    [start_date + timedelta(days=i) for i in range(available_days)],
                    max(0, num_dates - min_streak_length)
                )
                streak_start = random.choice(
                    [start_date + timedelta(days=i) for i in range(available_days - min_streak_length + 1)])
                streak_dates = [streak_start + timedelta(days=i) for i in range(min_streak_length)]
            all_dates = random_given_dates + streak_dates
            return sorted(all_dates)

        current_date = datetime.today()
        six_months_ago = current_date - timedelta(days=180)
        four_months_ago = current_date - timedelta(days=120)
        three_months_ago = current_date - timedelta(days=90)

        # Habit 1
        habit_1 = Habit("Drink 1.5l of Water", "Keep Hydrated", "Daily", creation_date=six_months_ago.date())
        self.db_manager.save_habit(habit_1)
        habit = self.db_manager.get_data_from_last_created_habit()
        habit_id, name, description, recurrence, *_ = habit
        random_dates = generate_random_dates(six_months_ago, current_date, 130, min_streak_length=8)
        for given_date in random_dates:
            self.db_manager.add_checkoff_entry(habit_id, checkoff_date=given_date.strftime("%Y-%m-%d"))

        # Habit 2
        habit_2 = Habit("Have a Siesta", "Reset the brain after work", "Daily", creation_date=four_months_ago.date())
        self.db_manager.save_habit(habit_2)
        habit = self.db_manager.get_data_from_last_created_habit()
        habit_id, name, description, recurrence, *_ = habit
        random_dates = generate_random_dates(six_months_ago, current_date, 73, min_streak_length=7)
        for given_date in random_dates:
            self.db_manager.add_checkoff_entry(habit_id, checkoff_date=given_date.strftime("%Y-%m-%d"))

        # Habit 3
        habit_3 = Habit("Read a Book", "Remain intellectual", "Weekly", creation_date=six_months_ago.date())
        self.db_manager.save_habit(habit_3)
        habit = self.db_manager.get_data_from_last_created_habit()
        habit_id, name, description, recurrence, *_ = habit
        random_dates = generate_random_dates(six_months_ago, current_date, 23, min_streak_length=2)
        for given_date in random_dates:
            self.db_manager.add_checkoff_entry(habit_id, checkoff_date=given_date.strftime("%Y-%m-%d"))

        # Habit 4
        habit_4 = Habit("Cook Special Meal", "Impress the family with new skills", "Weekly",
                        creation_date=three_months_ago.date())
        self.db_manager.save_habit(habit_4)
        habit = self.db_manager.get_data_from_last_created_habit()
        habit_id, name, description, recurrence, *_ = habit
        random_dates = generate_random_dates(six_months_ago, current_date, 9, min_streak_length=1)
        for given_date in random_dates:
            self.db_manager.add_checkoff_entry(habit_id, checkoff_date=given_date.strftime("%Y-%m-%d"))

        # Habit 5
        habit_5 = Habit("Run", "Go for daily run in the mountains", "Daily", creation_date=six_months_ago.date())
        self.db_manager.save_habit(habit_5)
        habit = self.db_manager.get_data_from_last_created_habit()
        habit_id, name, description, recurrence, *_ = habit
        random_dates = generate_random_dates(six_months_ago, current_date, 148, min_streak_length=10)
        for given_date in random_dates:
            self.db_manager.add_checkoff_entry(habit_id, checkoff_date=given_date.strftime("%Y-%m-%d"))

    def create_habit(self):
        """
        Creates a new habit by prompting the user for input and saves it to the database.
        Additionally, displays the details of the created habit after it is saved successfully.

        The user is prompted to enter the name, description, and recurrence of the habit.
        Once the input is provided, a new `Habit` object is created with the gathered information.
        The habit is then saved using the database manager. Finally, the created habit's details
        are displayed to the user.

        :raises:
            Exceptions may occur due to invalid user input or database operation failures.

        """
        name = questionary.text("Enter the name of the habit:").ask()
        description = questionary.text("Enter a description for the habit:").ask()
        recurrence = questionary.select("Choose the recurrence for the habit:",
                                        choices=["Daily", "Weekly"]).ask()

        new_habit = Habit(name=name, description=description, recurrence=recurrence)
        self.db_manager.save_habit(new_habit)
        print(f"\nHabit '{name}' created successfully!\n")
        print(f"[bold]Your new habit:[/]")
        print_habit_information(name, description, recurrence)
        print(f"\n\n")

    # MANAGE MY HABITS SUBMENU

    def manage_my_habits(self):
        """
        Manages existing habits by providing a menu for the user to choose specific operations.
        The method offers options to check off a habit, edit it, mark it as complete, delete it,
        or cancel the operation. The choice is presented interactively, and the corresponding method
        is invoked based on the user's selection.

        :raises UserInputError: If the choice selected by the user is invalid or not recognized
        """
        console.print(
            "[bold blue][size=16]*** Here you can manage your existing habits! ***[/size][/bold blue]\n")
        while True:
            choice = questionary.select(
                "Please select an option:",
                choices=[
                    "[1] Check Off Habit",
                    "[2] Edit Habit",
                    "[3] Complete Habit",
                    "[4] Delete Habit",
                    "[5] Cancel"
                ]
            ).ask()

            if choice == "[1] Check Off Habit":
                self.check_off_habit()
            elif choice == "[2] Edit Habit":
                self.edit_habit()
            elif choice == "[3] Complete Habit":
                self.complete_habit()
            elif choice == "[4] Delete Habit":
                self.delete_habit()
            elif choice == "[5] Cancel":
                return

    def check_off_habit(self):
        """
        Marks a habit as checked off for a user-selected habit and the respective recurrence period.
        The function fetches active habits, allows the user to pick one, and checks its eligibility
        for being marked as done either on the same day (for daily recurrence) or within the same
        week (for weekly recurrence). If it hasn't been previously checked off, an entry is added
        to the database.

        :raises ValueError: Raised if the selected index is invalid for the list of habits.
        :param self: Instance of the class containing the method.
        :return: None
        """
        habits = self.db_manager.fetch_all_active_habits()
        if not habits:
            print("No active habits found.")
            return

        # Prompt the user to select a habit to check
        choices = [f"{habit[1]} - {habit[2]} (Recurrence: {habit[3]})" for habit in habits]
        choice = questionary.select("Which habit would you like to check off?",
                                    choices=choices + ["Cancel"]).ask()
        if choice == "Cancel":
            return
        selected_habit = habits[choices.index(choice)]
        habit_id, name, description, recurrence, *_ = selected_habit
        checked_off = None

        # Check if habit has already been checked off that day or week, depending on recurrence
        if recurrence == "Daily":
            checked_off = self.db_manager.is_habit_checked_off_today(habit_id)
        elif recurrence == "Weekly":
            checked_off = self.db_manager.is_habit_checked_off_this_week(habit_id)

        if checked_off:
            print("Habit already checked off.")
            return
        else:
            # Add check-off entry if it hasn't been checked off yet
            self.db_manager.add_checkoff_entry(selected_habit[0], checkoff_date=date.today())
            print(f"\nHabit: {name}\nDescription: {description}\nRecurrence: {recurrence}\nChecked-Off")

    def edit_habit(self):
        """
        Edits an existing habit by updating its name, description, or recurrence interval.
        The function retrieves all available habits from the database, displays them
        for selection, and allows the user to modify the selected habit's details.
        If no habits are available or the user cancels the process, the operation is aborted.

        :raises ValueError: Raised if an invalid choice is made from the selection menu.

        :param self: The instance of the class containing this method.

        :return: None
        """
        habits = self.db_manager.fetch_all_habits()
        if not habits:
            print("No habits to edit.")
            return

        choices = [f"{habit[1]} - {habit[2]} (Recurrence: {habit[3]})" for habit in habits]
        choice = questionary.select("Which habit would you like to edit?", choices=choices + ["Cancel"]).ask()
        if choice == "Cancel":
            return

        selected_habit = habits[choices.index(choice)]

        name = questionary.text("Enter new name:", default=selected_habit[1]).ask()
        description = questionary.text("Enter new description:", default=selected_habit[2]).ask()
        recurrence = questionary.select("Choose new recurrence:", choices=["Daily", "Weekly"],
                                        default=selected_habit[3]).ask()

        self.db_manager.update_habit(selected_habit[0], name, description, recurrence)

    def complete_habit(self):
        """
        Marks a habit as completed by the user. The method retrieves all active
        habits from the database and allows the user to select the habit they
        have completed from a list of options. If no active habits are
        available, an appropriate message is displayed. The selected habit is
        then marked as completed in the database.

        :raises ValueError: If the selected choice is not valid or cannot be
            processed.
        """
        habits = self.db_manager.fetch_all_active_habits()
        if not habits:
            print("No active habits to complete.")
            return

        choices = [f"{habit[1]} - {habit[2]} (Recurrence: {habit[3]})" for habit in habits]
        choice = questionary.select("Which habit have you completed?", choices=choices + ["Cancel"]).ask()
        if choice == "Cancel":
            return
        selected_habit = habits[choices.index(choice)]

        self.db_manager.complete_habit(selected_habit[0])

    def delete_habit(self):
        """
        Deletes a habit chosen by the user from the database.

        The method fetches all available habits from the database using the
        `self.db_manager.fetch_all_habits()` function and presents them to the user
        through a selectable interface. The user can then choose a habit to delete or
        cancel the operation. If no habits are available, a message is displayed and
        the operation is terminated. Upon selection, the chosen habit is deleted from
        the database with `self.db_manager.delete_habit()`.

        :raises ValueError: Raised if there is an inconsistency between the selected
                            habit and the list of available choices.
        """
        habits = self.db_manager.fetch_all_habits()
        if not habits:
            print("No habits to delete.")
            return

        choices = [f"Name: {habit[1]}\nDescription: {habit[2]}\n(Recurrence: {habit[3]})\nStatus: {habit[6]}"
                   for habit in habits]
        choice = questionary.select("Which habit would you like to delete?",
                                    choices=choices + ["Cancel"]).ask()
        if choice == "Cancel":
            return
        selected_habit = habits[choices.index(choice)]

        self.db_manager.delete_habit(selected_habit[0])