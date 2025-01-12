import time

import questionary
from prompt_toolkit.styles import Style
from rich.console import Console
from rich.theme import Theme

from Analyze import HabitAnalyzer
from DBManager import DatabaseManager
from HabitManager import HabitManager


def text_enrichment():
    """ Provides a text enrichment function to configure and return a console with a custom
    theme as well as a pre-defined custom style for Questionary. """

    # Define Console Rich. Theme
    custom_theme = Theme({"title": "bold blue", "info": "bold cyan", "warning": "yellow",
                          "exit": "red", "error": "bold red", "success": "bold green", "processing": "italic yellow"})

    console = Console(theme=custom_theme)

    # Define custom style for Questionary
    custom_style = Style([
        ('qmark', 'fg:#ff9d00 bold'),  # Question mark color
        ('question', 'bold'),  # Question text color
        ('answer', 'fg:#00ffb3 bold'),  # Selected answer color
        ('pointer', 'fg:#ff9d00 bold'),  # Pointer color
        ('highlighted', 'fg:#ff9d00 bold'),  # Highlighted menu option
        ('separator', 'fg:#6C6C6C'),  # Separator color
        ('instruction', ''),  # Instruction (not used in this case)
        ('text', ''),  # General text
        ('disabled', 'fg:#858585 italic')  # Disabled option text
    ])
    return console, custom_style

class Menu:
    """
    Represents the main menu and its related functionalities for the habit tracker application.

    This class serves as the primary interface for managing the habits, analyzing data, and interacting
    with the user. It utilizes various managers and analyzers to provide a seamless experience for
    habit tracking and progress monitoring.

    """
    def __init__(self):
        self.db_manager = DatabaseManager()
        self.analyzer = HabitAnalyzer(text_enrichment())
        self.manager = HabitManager(text_enrichment())
        self.console, self.custom_style = text_enrichment()

    def welcome(self):
        if self.db_manager.fetch_all_habits():  # If there is data in database, Welcome Back the User
            self.console.print("[size=18]\n[][][] *** Welcome back!! *** [][][][/size]\n", style="title")
            time.sleep(1)
        else:  # If there isn't Apply Welcome Script
            self.console.print("[size=18]\n[][][] ***  Welcome to your Habit Tracker !! *** [][][][/size]\n",
                               style="title")
            time.sleep(3)
            self.console.print("Since this is your first time, shall we take a quick tour?!\n", style="info")
            time.sleep(3)
            self.console.print("Navigating through the App is very straightforward.", style="info")
            time.sleep(3)
            self.console.print("Simply use your keyboard 'Up' and 'Down' arrows while selecting from the menu "
                               "options and type in your keyboard your inputs when prompted.\n", style="info")
            time.sleep(5)
            self.console.print("From the main menu you can choose to:\n", style="info")
            time.sleep(3)
            self.console.print("- \t Get started straight away creating your new habits!\n", style="info")
            time.sleep(3)
            self.console.print("- \t You can access the 'Manage your Habits' submenu, where you can checkoff, "
                               "edit, delete or complete your habits!\n", style="info")
            time.sleep(6)
            self.console.print("- \t Or you can access the 'Analyze your Habits' menu, where you can track your "
                               "habits' performance; view a summary of your habits, your streaks, or even see how your "
                               "habits fare through different chart visualizations!\n", style="info")
            time.sleep(6)
            self.console.print("- \t You can, of course, exit the application at any time.\n", style="info")
            time.sleep(3)
            self.console.print("There is a lot more to it, but I promised you a quick tour but you wouldn't "
                               "want all the spoilers, right?", style="info")
            time.sleep(4)
            self.console.print("\nFor now, let me set up a few pre-defined habits for you, so you have months "
                               "worth of data to explore the App and get the real look and feel!", style="info")
            time.sleep(6)
            self.console.print("\nSetting up 5 predefined habits...", style="processing")
            time.sleep(3)
            try:
                self.manager.create_predefined_habits()  # Create predefined habits
                self.console.print("All predefined habits set up successfully!\n", style="success")
            except Exception as e:
                self.console.print(f"An error occurred while setting up predefined habits: {e}", style="error")
            time.sleep(4)
            self.console.print("Let's get started!\n\n", style="info")

    def select_habit(self, status):
        """ Selects a habit from the database based on user input. """

        habits = (
            self.db_manager.fetch_all_active_habits()
            if status == "active"
            else self.db_manager.fetch_all_habits()
        )

        if not habits:
            self.console.print("No habits found.", style="warning")
            return

        choices = [habit[1] for habit in habits]
        choice = questionary.select(
            "Which habit would you like to manage?",
            choices=choices + ["Cancel"],
            style=self.custom_style
        ).ask()

        return "Cancel" if choice == "Cancel" else habits[choices.index(choice)]

    def run_main_menu(self):

        # Run the main menu
        options = {
            "[1] Create new Habit": lambda: self.manager.create_habit(),
            "[2] Manage my Habits": lambda: self.manage_my_habits(),
            "[3] Analyze": lambda: self.analyze(),
            "[4] Exit": lambda: None
        }

        while True:
            choice = questionary.select(
                "Please select an option:",
                choices=list(options.keys()),
                style=self.custom_style
            ).ask()

            if choice == "[4] Exit":
                self.console.print("Exiting the application for now... Goodbye!", style="exit")
                break

            options[choice]()


    def manage_my_habits(self):
        self.console.print("[][][] *** Here you can manage your existing habits! *** [][][]\n", style="title")

        # Include all habit management submenu options in a dictionary with its corresponding function
        options = {
            "[1] Check Off Habit": lambda: self.manager.check_off_habit(self.select_habit(status="active")),
            "[2] Edit Habit": lambda: self.manager.edit_habit(self.select_habit(status=None)),
            "[3] Complete Habit": lambda: self.manager.complete_habit(self.select_habit(status="active")),
            "[4] Delete Habit": lambda: self.manager.delete_habit(self.select_habit(status=None)),
            "[5] Cancel": lambda: None
        }

        # Prompt the user to select their option
        while True:
            choice = questionary.select(
                "Please select an option:",
                choices=list(options.keys()),
                style=self.custom_style
            ).ask()

            if choice == "[5] Cancel":
                return

            options[choice]()

    def analyze(self):
        """ Submenu for the user to navigate and choose different analysis options. """

        # Welcome Message
        self.console.print("[][][] *** Welcome to your Habit Analysis Menu! *** [][][]\n", style="title")
        data = self.analyzer.view_habits_summary()

        analyze_menu_options = {
            "[1] Sort the Habit Summary Table": lambda:
            self.analyzer.sort_habits_summary(data, self.console, self.custom_style) if data else self.console.print(
                "No habits available for sorting.", style="warning"),
            "[2] View Charts": lambda: self.view_charts_submenu(),
            "[3] Return to Main Menu": lambda: "return"
        }

        while True:
            choice = questionary.select(
                "Please select an analysis option:",
                choices=list(analyze_menu_options.keys()), style=self.custom_style
            ).ask()

            if analyze_menu_options[choice]() == "return":
                return

    def view_charts_submenu(self):
        """ Submenu to view habit-related charts. """

        charts_menu_options = {
            "[1] View a Habit's Streak Progress": lambda: self.analyzer.view_habit_streak_progress(
                self.select_habit(status=None)),
            "[2] Review Habit Performance": lambda: self.analyzer.view_habit_monthly_performance(
                self.select_habit(status=None)),
            "[3] Review All Habits Performance": lambda: self.analyzer.view_all_habits_performance(),
            "[4] Check Recent Check-Off Activity": lambda: self.analyzer.view_checkoff_recent_activity(),
            "[5] Cancel": lambda: "return"
        }

        while True:
            choice = questionary.select(
                "Please select an option:",
                choices=list(charts_menu_options.keys()), style=self.custom_style
            ).ask()

            if charts_menu_options[choice]() == "return":
                return