import time

import questionary
from rich.align import Align
from rich.console import Console

from Analyze import HabitAnalyzer
from HabitManager import HabitManager

console = Console()


def run():
    manager = HabitManager()
    analyzer = HabitAnalyzer()

    # Welcome the User
    if manager.db_manager.fetch_all_habits():  # If there is data in database, Welcome Back the USer
        console.print(Align("[bold blue]\n*** Welcome back!! ***[/bold blue]", align="center"))
        time.sleep(1)
    else: # If there isn't Apply Welcome Script
        console.print(
            Align(
                "[bold blue][size=16]\n*** Welcome to the Happy Habit Tracker !! ***[/size][/bold blue]\n",
                align="center"))
        console.print(
            Align(
                "\n[size=16]Let me set up a few pre-defined habits "
                "for you, so you can get a better look and feel of the App's potential.[/size]", align="center"))
        time.sleep(3)
        console.print(
            Align("[italic yellow][size=16]\nSetting up predefined habits...[/size][/italic yellow]",
                  align="center"))
        manager.create_predefined_habits()  # Create predefined habits
        time.sleep(3)
        console.print(Align("[italic yellow][size=16]\nPredefined habits set up successfully"
                            "![/size][/italic yellow]", align="center"))

    # Run the Main Menu Loop
    while True:
        choice = questionary.select(
            "What would you like me to do?\n",
            choices=[
                "[1] Create new Habit",
                "[2] Manage my Habits",
                "[3] Analyze",
                "[4] Exit"
            ]
        ).ask()

        if choice == "[1] Create new Habit":
            manager.create_habit()
        elif choice == "[2] Manage my Habits":
            manager.manage_my_habits()
        elif choice == "[3] Analyze":
            analyzer.analyze()
        elif choice == "[4] Exit":
            console.print(Align("[bold red]Exiting the application... Goodbye!\n[/bold red]", align="center"))
            break


if __name__ == '__main__':
    run()