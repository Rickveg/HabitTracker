from datetime import date, datetime, timedelta

import matplotlib.dates as mdates
import matplotlib.pyplot as plt
import questionary
from rich.console import Console
from rich.table import Table

from DBManager import DatabaseManager

console = Console()


class HabitAnalyzer:
    """
    Provides methods to analyze and manage user habits, including sorting
    habit summaries, viewing habit charts, and displaying habit data.

    The class leverages a `DatabaseManager` for CRUD operations on
    habit-related information. It offers an interactive menu and
    visual representation of habits and their performance.

    :ivar db_manager: Instance managing database operations for habit data.
    :type db_manager: DatabaseManager
    """
    def __init__(self):
        self.db_manager = DatabaseManager()

    def analyze(self):
        """
        Analyze and evaluate habits based on user-selected options. Provides a menu
        for habit data visualization including sorting, checking streak progress,
        reviewing performance, and recent check-off activities.

        :return: None
        """
        console.print(
            "[bold blue][size=16]*** Welcome to your Habit Analyze Menu! ***[/size][/bold blue]\n")
        data = self.view_habits_summary()

        while True:
            choice = questionary.select(
                "Please select an analysis option:",
                choices=[
                    "[1] Sort the Habit Summary Table",
                    "[2] View Charts",
                    "[3] Return to Main Menu"
                ]
            ).ask()

            if choice == "[1] Sort the Habit Summary Table":
                if data:
                    self.sort_habits_summary(data=data)
                else:
                    console.print("[bold red]No habits available for sorting.[/bold red]")

            # Charts SubMenu
            elif choice == "[2] View Charts":
                while True:
                    choice = questionary.select(
                        "Please select an option:",
                        choices=[
                            "[1] View a Habit's Streak Progress",
                            "[2] Review Habit Performance",
                            "[3] Check Recent Check-Off Activity",
                            "[4] Cancel"
                        ]
                    ).ask()

                    if choice == "[1] View a Habit's Streak Progress":
                        self.view_habit_streak_progress()
                    elif choice == "[2] Review Habit Performance":
                        self.view_habit_monthly_performance()
                    elif choice == "[3] Check Recent Check-Off Activity":
                        self.view_checkoff_recent_activity()
                    elif choice == "[4] Cancel":
                        return

            elif choice == "[3] Return to Main Menu":
                return


    # SUMMARY TABLE

    @staticmethod
    def sort_habits_summary(data):
        """
        Sort a list of habits based on user-selected attributes and display the sorted
        data in a formatted table.

        This method enables users to sort data by a specific attribute such as Name,
        Recurrence, Status, etc., in ascending or descending order. The sorted data
        is displayed in a visually styled table with color-coded values based on
        specific conditions.

        :param data: List of habit information, where each habit is represented as
            a list or tuple. Each entry must contain elements in a specific order
            corresponding to the sort map and table column definitions.
        :type data: list
        :raises KeyError: If the sort choice is not found in the pre-defined sort map.
        :raises ValueError: If the `sort_choice` or `ascending_order` inputs are
            invalid or missing.
        :return: None if the sorting operation is canceled by the user.
        :rtype: None
        """
        sort_options = [
            "Name", "Recurrence", "Creation Date", "Status", "Completion Date",
            "Check_off Status", "Current Streak", "Longest Streak",
            "Performance", "Rank", "Cancel"
        ]

        # Prompt user for sorting attribute
        sort_choice = questionary.select(
            "Select attribute to sort by:",
            choices=sort_options
        ).ask()

        if sort_choice == "Cancel":
            return

        ascending_order = questionary.confirm(
            "Sort in ascending order?"
        ).ask()

        # Map user choice to column index
        sort_map = {
            "Name": 0, "Recurrence": 1, "Creation Date": 2, "Status": 3,
            "Completion Date": 4, "Check_off Status": 5, "Current Streak": 6,
            "Longest Streak": 7, "Performance": 8, "Rank": 9
        }
        sort_index = sort_map[sort_choice]

        # Sort data by the selected column and order
        data.sort(key=lambda x: x[sort_index], reverse=not ascending_order)

        # Define table columns and their styles
        columns = [
            ("Name", "bright_white"), ("Recurrence", "cyan"),
            ("Creation Date", "cyan"), ("Status", "cyan"),
            ("Completion Date", "cyan"), ("Check_off Status", None),
            ("Current Streak", None), ("Longest Streak", None),
            ("% Performance", None), ("Rank", None)
        ]

        # Initialize the table
        df_table = Table(title="Habit Summary (Sorted)", header_style="blue bold", show_header=True)
        for col_name, col_style in columns:
            df_table.add_column(col_name, justify="center" if col_style else "left", style=col_style,
                                no_wrap=(col_name == "Name"))

        # Add rows to the table with conditional styling
        for row in data:
            check_off_status_style = "green" if row[5] == "Checked_Off" else "red"
            current_streak_style = "cyan" if row[6] > 0 else "red"
            longest_streak_style = "cyan" if row[7] > 0 else "red"
            habit_performance_style = "green" if row[8] >= 60 else "red"
            rank_style = "green" if row[9] in ["Outstanding", "Excellent", "Very Good"] else "red"

            df_table.add_row(
                row[0], row[1], row[2], row[3],
                row[4] if row[4] else "N/A",
                f"[{check_off_status_style}]{row[5]}[/]",
                f"[{current_streak_style}]{row[6]}[/]",
                f"[{longest_streak_style}]{row[7]}[/]",
                f"[{habit_performance_style}]{row[8]:.2f}%[/]",
                f"[{rank_style}]{row[9]}[/]"
            )
        console.print(df_table)

    def view_habits_summary(self):
        """
        Provides a comprehensive summary of all habits stored in the database.

        This method retrieves habit data from the database, calculates relevant metrics
        for each habit, and organizes the information into a structured summary. The
        summary includes metrics such as current streak, longest streak, habit performance
        percentage, and a corresponding rank based on performance. It also checks if
        the habit is marked as completed for the current recurrence cycle (daily or weekly).

        The summary is then presented in a formatted table for visualization purposes and
        is returned as processed data.

        :returns:
            A list of habit information organized in the following structure:

            - Name (str): The name of the habit.
            - Recurrence (str): The habit's recurrence frequency ("Daily" or "Weekly").
            - Creation Date (datetime): The date when the habit was created.
            - Status (str): The current status of the habit ("Active" or another defined status).
            - Completion Date (datetime or None): The date of completion if completed.
            - Check_off Status (str): Indicates if the habit is marked as "Checked_Off"
              or "Not Checked_Off".
            - Current Streak (int): The current streak count for the habit.
            - Longest Streak (int): The longest recorded streak for the habit.
            - % Performance (float): The performance percentage of the habit over its lifecycle.
            - Rank (str): A textual ranking derived from the performance percentage
              ("Outstanding", "Excellent", "Very Good", "Good", "Inconsistent", "Poor", or "Unknown").

        """
        habits = self.db_manager.fetch_all_habits()
        if not habits:
            console.print("[bold red]No habits found.[/bold red]")
            return

        data = []
        rank_mapping = {
            (100, 101): "Outstanding",
            (91, 100): "Excellent",
            (71, 91): "Very Good",
            (61, 71): "Good",
            (51, 61): "Inconsistent",
            (0, 51): "Poor"
        }

        for habit in habits:
            habit_id, name, description, recurrence, *_ = habit
            creation_date = self.db_manager.get_creation_date(habit_id)
            status = self.db_manager.get_status(habit_id)
            completion_date = self.db_manager.get_completion_date(habit_id)
            current_streak = self.db_manager.get_current_streak(habit_id)
            longest_streak = self.db_manager.get_longest_streak(habit_id)
            habit_performance = self.db_manager.get_habit_performance(habit_id, creation_date)

            # Determine rank based on performance
            rank = next((label for range_key, label in rank_mapping.items()
                         if range_key[0] <= habit_performance < range_key[1]), "Unknown")

            # Check checked_off status for the habit
            checked_off = (self.db_manager.is_habit_checked_off_today(habit_id) if recurrence == "Daily"
                           else self.db_manager.is_habit_checked_off_this_week(habit_id))
            check_off_status = "Checked_Off" if checked_off else "Not Checked_Off"

            # Append habit data
            data.append([
                name, recurrence, creation_date, status, completion_date,
                check_off_status, current_streak, longest_streak,
                habit_performance, rank
            ])

        # Create and display a summary table
        df_table = Table(title="Habit Summary", header_style="blue bold", show_header=True)
        columns = [
            ("Name", "bright_white"), ("Recurrence", "cyan"),
            ("Creation Date", "cyan"), ("Status", "cyan"),
            ("Completion Date", "cyan"), ("Check_off Status", None),
            ("Current Streak", None), ("Longest Streak", None),
            ("% Performance", None), ("Rank", None)
        ]
        for col_name, col_style in columns:
            df_table.add_column(col_name, justify="center" if col_style else "left",
                                style=col_style, no_wrap=(col_name == "Name"))

        for row in data:
            check_off_status_style = "green" if row[5] == "Checked_Off" else "red"
            current_streak_style = "cyan" if row[6] > 0 else "red"
            longest_streak_style = "cyan" if row[7] > 0 else "red"
            habit_performance_style = "green" if row[8] >= 60 else "red"
            rank_style = "green" if row[9] in ["Outstanding", "Excellent", "Very Good"] else "red"

            df_table.add_row(
                row[0], row[1], str(row[2]), row[3] or "N/A", str(row[4]) if row[4] else "N/A",
                f"[{check_off_status_style}]{row[5]}[/]",
                f"[{current_streak_style}]{row[6]}[/]",
                f"[{longest_streak_style}]{row[7]}[/]",
                f"[{habit_performance_style}]{row[8]:.2f}%[/]",
                f"[{rank_style}]{row[9]}[/]"
            )

        console.print(df_table)
        return data

    # CHARTS

    def view_habit_streak_progress(self):
        """
        Displays and plots the progress of streaks for a selected habit, including interactive visualization.

        The method retrieves all habits from the database, allows the user to select a specific habit,
        and calculates streak progress based on recurrence (daily or weekly). The progress is visualized
        using a line plot where streak information is displayed interactively.

        :raises ValueError: If there is an issue with fetching or formatting habit data.
        :param self: Instance reference for the class.
        :returns: None
        """
        habits = self.db_manager.fetch_all_habits()
        if not habits:
            print("No habits found.")
            return

        choices = [f"{habit[1]} - {habit[2]} (Recurrence: {habit[3]})" for habit in habits]
        choice = questionary.select("Select a habit to view progress:", choices=choices + ["Cancel"]).ask()
        if choice == "Cancel":
            return

        selected_habit = habits[choices.index(choice)]
        habit_id, name, description, recurrence, *_ = selected_habit

        # Fetch habit's check-off information
        checkoff_dates = self.db_manager.fetch_daily_checkoff_info(habit_id)
        fixed_checkoff_dates = []
        for d in checkoff_dates:
            fixed_checkoff_dates.append(date.fromisoformat(d[0]))

        if not fixed_checkoff_dates:
            print(f"No progress found for habit: {name}")
            return

        # Create a full date range
        sorted_dates = sorted(fixed_checkoff_dates)
        if recurrence == "Weekly":
            start_date = sorted_dates[0] - timedelta(days=sorted_dates[0].weekday())
            end_date = max(sorted_dates[-1] - timedelta(days=sorted_dates[-1].weekday()),
                           date.today() - timedelta(days=date.today().weekday()))
            full_date_range = [start_date + timedelta(weeks=i) for i in range(((end_date - start_date).days // 7) + 1)]
        else:
            start_date = sorted_dates[0]
            end_date = max(sorted_dates[-1], date.today())
            full_date_range = [start_date + timedelta(days=i) for i in range((end_date - start_date).days + 1)]

        # Calculate streaks
        streaks = []
        current_streak = 0
        for check_date in full_date_range:
            if recurrence == "Weekly":
                if check_date in {d - timedelta(days=d.weekday()) for d in sorted_dates}:
                    current_streak += 1
                else:
                    current_streak = 0
            else:
                if check_date in sorted_dates:
                    current_streak += 1
                else:
                    current_streak = 0
            streaks.append(current_streak)

        # Plot progress graph with improved coloring
        fig, ax = plt.subplots(figsize=(12, 8))  # Set figure size
        line, = ax.plot(full_date_range, streaks, marker="o", label="Streak Count", linestyle='-', color='#003f5c')
        ax.set_facecolor("#f7f7f7")  # Set background color
        ax.set_xlabel("Date", fontsize=14, fontweight="bold",
                      color="#333333")  # Set font size and color for x-axis label
        ax.set_ylabel("Streak", fontsize=14, fontweight="bold",
                      color="#333333")  # Set font size and color for y-axis label
        ax.set_title(f"{name} [Streak Progress]", fontsize=16, fontweight="bold", color='#58508d')
        if recurrence == "Weekly":
            ax.xaxis.set_major_locator(mdates.WeekdayLocator(interval=1))
            ax.xaxis.set_major_formatter(mdates.DateFormatter("%d, %B, %y"))
        else:
            ax.xaxis.set_major_locator(mdates.DayLocator(interval=7))
            ax.xaxis.set_major_formatter(mdates.DateFormatter("%d, %B, %y"))
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)
        ax.spines['bottom'].set_color('#333333')
        ax.spines['left'].set_color('#333333')
        ax.tick_params(axis="x", rotation=45, labelsize=10, colors="#333333")  # Adjust tick label size and color
        ax.tick_params(axis="y", labelsize=10, colors="#333333")  # Adjust y-axis tick label size and color
        ax.grid(color="#d4d4d4", linestyle="--", linewidth=0.6, alpha=0.7)  # Add light gridlines
        ax.legend(fontsize=12, edgecolor="#333333")  # Adjust legend style and edge color

        # Add interactive hover functionality
        annotation = ax.annotate(
            "", xy=(0, 0), xytext=(15, 15), textcoords="offset points",
            bbox=dict(boxstyle="round", fc="white", edgecolor="#333333"),
            arrowprops=dict(arrowstyle="->", color="#333333")
        )
        annotation.set_visible(False)

        def on_hover(event):
            if event.inaxes == ax:
                for x, y in zip(full_date_range, streaks):
                    if line.contains(event)[0]:
                        if abs(event.xdata - mdates.date2num(x)) < 0.5 and abs(event.ydata - y) < 0.5:
                            annotation.set_text(f"Date: {x.strftime('%d-%m-%Y')}\nStreak: {y}")
                            annotation.xy = (mdates.date2num(x), y)
                            annotation.set_visible(True)
                            fig.canvas.draw_idle()
                            return
            annotation.set_visible(False)
            fig.canvas.draw_idle()

        fig.canvas.mpl_connect("motion_notify_event", on_hover)
        plt.tight_layout()
        plt.show()

    def view_habit_monthly_performance(self):
        """
        Evaluates and visualizes the performance of a selected habit on a monthly basis.

        This method fetches habit information from the database, calculates monthly check-offs
        for a selected habit, and generates a bar chart to display the monthly performance.
        The calculated performance percentage for each month is based on the habit's recurrence type
        ("Daily" or "Weekly"). Users can interact with the visualization to view details for each
        month through on-hover annotations.

        :raises ValueError: If the input data or processing steps encounter unexpected issues.

        :param self: Instance of the class that uses this method to access required components like
            the database manager.

        :return: None
        """
        habits = self.db_manager.fetch_all_habits()
        if not habits:
            print("No habits found.")
            return

        # Let user select a habit
        choices = [f"{habit[1]} - {habit[2]} (Recurrence: {habit[3]})" for habit in habits]
        choice = questionary.select("Select a habit to view monthly summary progress:",
                                    choices=choices + ["Cancel"]).ask()
        if choice == "Cancel":
            return

        selected_habit = habits[choices.index(choice)]
        habit_id, name, description, recurrence, *_ = selected_habit

        # Fetch habit's check-off information
        checkoff_dates = self.db_manager.fetch_daily_checkoff_info(habit_id)
        if not checkoff_dates:
            print(f"No check-off data found for habit: {name}")
            return

        fixed_checkoff_dates = [date.fromisoformat(record[0]) for record in checkoff_dates]
        start_date = min(fixed_checkoff_dates)
        end_date = max(fixed_checkoff_dates + [date.today()])

        # Generate month-wise summary
        month_summary = {}
        for d in fixed_checkoff_dates:
            month_key = d.strftime("%Y-%m")
            month_summary[month_key] = month_summary.get(month_key, 0) + 1

        # Fill in gaps for months with no check-offs
        current = start_date.replace(day=1)
        while current <= end_date:
            month_key = current.strftime("%Y-%m")
            month_summary.setdefault(month_key, 0)
            current += timedelta(days=32)
            current = current.replace(day=1)

        # Sort by month keys
        sorted_months = sorted(month_summary.keys())
        counts = [month_summary[key] for key in sorted_months]
        performances = [
            (count / 31 * 100 if recurrence == "Daily" else count / 5 * 100)
            for count in counts
        ]

        # Configure y-axis limit based on recurrence
        if recurrence == "Daily":
            y_limit = 31
        elif recurrence == "Weekly":
            y_limit = 5
        else:
            y_limit = max(counts, default=0)

        # Determine bar colors based on performance
        bar_colors = [
            "#003f5c" if performance >= 90 else
            "#58508d" if 65 < performance < 90 else
            "#bc5090" if 51 <= performance <= 65 else
            "#ff6361" if 20 <= performance < 51 else
            "#ffa600"
            for performance in performances
        ]

        # Plot bar graph with enhanced style
        fig, ax = plt.subplots(figsize=(12, 8))
        bars = ax.bar(sorted_months, counts, color=bar_colors, edgecolor="black", linewidth=1)
        ax.set_ylim(0, y_limit)
        ax.set_xlabel("Month", fontsize=14, fontweight="bold", color="#58508d")
        ax.set_ylabel("Check-offs", fontsize=14, fontweight="bold", color="#58508d")
        ax.set_title(f"{name} [Performance]", fontsize=16, fontweight="bold",color="#003f5c")
        ax.grid(axis="y", linestyle="--", alpha=0.7)

        # Convert the x-ticks to display text with the month name and year
        months_with_year = [datetime.strptime(month, "%Y-%m").strftime("%B (%y)") for month in sorted_months]
        ax.set_xticks(range(len(sorted_months)))
        ax.set_xticklabels(months_with_year, rotation=45, ha="right", fontsize=11, color="#58508d")
        ax.tick_params(axis="y", labelsize=12)
        plt.tight_layout()

        # Add interactive hover functionality
        annotation = ax.annotate(
            "", xy=(0, 0), xytext=(15, 15), textcoords="offset points",
            bbox=dict(boxstyle="round", fc="w", edgecolor="black"),
            arrowprops=dict(arrowstyle="->", color="black")
        )
        annotation.set_visible(False)

        def on_hover(event):
            if event.inaxes == ax:
                for bar, count, performance, month in zip(bars, counts, performances, sorted_months):
                    if bar.contains(event)[0]:
                        annotation.xy = (event.xdata, event.ydata)
                        annotation.set_text(
                            f"Month: {month}\nCheck-offs: {count}\nPerformance: {performance:.2f}%"
                        )
                        annotation.set_visible(True)
                        fig.canvas.draw_idle()
                        return

            annotation.set_visible(False)
            fig.canvas.draw_idle()

        fig.canvas.mpl_connect("motion_notify_event", on_hover)
        plt.show()

    def view_checkoff_recent_activity(self):
        """
        Displays a detailed visualization of recent check-off activity for active habits, either daily or weekly.
        The function allows users to choose between a daily or weekly view of their habits and filters accordingly.
        It calculates the count of habits that have been checked off and those that have not within specified periods
        based on the user's choice. Then, it displays a stacked bar plot representing this data, where users can
        hover over the bars for detailed information.

        :raises ValueError: If there are no active habits found matching the recurrence type selected.
        :raises RuntimeError: If no habits exist in the database with the desired filtering criteria.

        :param self: An instance of the class containing the `db_manager` dependency and methods
                     for accessing database operations related to habits.
                     Also required for interacting with the console output.

        :returns: None. This function creates a bar graph visualization and shows it using matplotlib.
        """
        habits = self.db_manager.fetch_all_active_habits()
        if not habits:
            console.print("[bold red]No active habits found.[/bold red]")
            return

        # Prompt user to choose between daily or weekly view
        recurrence_type = questionary.select(
            "Choose the type of habits to view recent activity:",
            choices=["Daily", "Weekly", "Cancel"]
        ).ask()
        if recurrence_type == "Cancel":
            return

        # Filter habits by selected recurrence
        filtered_habits = [habit for habit in habits if habit[3] == recurrence_type]
        if not filtered_habits:
            console.print(f"[bold red]No active habits with {recurrence_type.lower()} recurrence found.[/bold red]")
            return

        # Define period and dates/weeks to track
        today = date.today()
        if recurrence_type == "Daily":
            tracked_period = [today - timedelta(days=i) for i in range(13, -1, -1)]  # Last 14 days
        else:  # Weekly
            tracked_period = [(today - timedelta(weeks=i)).isocalendar()[:2] for i in range(7, -1, -1)]  # Last 8 weeks

        # Prepare data
        checked_off_counts = []
        not_checked_off_counts = []
        checked_off_habits = {}
        not_checked_off_habits = {}

        for period in tracked_period:
            checked_off = []
            not_checked_off = []

            # Taking into account habits created within the tracked period
            for habit in filtered_habits:
                habit_creation_date = date.fromisoformat(self.db_manager.get_creation_date(habit[0]))
                if recurrence_type == "Daily":
                    if period >= habit_creation_date:
                        if self.db_manager.is_habit_checked_off_given_day(habit[0], period):
                            checked_off.append(habit[1])
                        else:
                            not_checked_off.append(habit[1])
                else:  # Weekly
                    habit_creation_week = habit_creation_date.isocalendar()[:2]

                    if period >= habit_creation_week:
                        if self.db_manager.is_habit_checked_off_weekly(habit[0], period):
                            checked_off.append(habit[1])
                        else:
                            not_checked_off.append(habit[1])

            # Store counts and habit names for hover
            checked_off_counts.append(len(checked_off))
            not_checked_off_counts.append(len(not_checked_off))
            checked_off_habits[period] = checked_off
            not_checked_off_habits[period] = not_checked_off

        # Plot setup
        fig, ax = plt.subplots(figsize=(12, 8))
        bar_width = 0.5
        x = range(len(tracked_period))

        # Bars with custom color codes
        bars_checked_off = ax.bar(x, checked_off_counts, color="#58508d", label="Checked Off", width=bar_width,
                                  edgecolor="black")
        bars_not_checked_off = ax.bar(x, not_checked_off_counts, bottom=checked_off_counts, color="#ff6361",
                                      label="Not Checked Off", width=bar_width, edgecolor="black")

        # Configure plot
        title = f"Check-off Recent Activity [Last {'14 Days' if recurrence_type == 'Daily' else '2 Months'}]"
        ax.set_title(title, fontsize=16, fontweight="bold", color="#003f5c")
        ax.set_xlabel("Date" if recurrence_type == "Daily" else "Week", fontsize=14, fontweight="bold", color="#58508d")
        ax.set_ylabel("Number of Habits", fontsize=14, fontweight="bold", color="#58508d")
        ax.set_xticks(x)
        if recurrence_type == "Daily":
            ax.set_xticklabels([day.strftime("%d-%b") for day in tracked_period], rotation=45, fontsize=12,
                               color="#58508d")
        else:
            ax.set_xticklabels([f"Week {week[1]}" for week in tracked_period], rotation=45, fontsize=12,
                               color="#58508d")
        ax.set_yticks(range(0, max(checked_off_counts + not_checked_off_counts) + 1, 1))
        ax.tick_params(axis="y", labelsize=12, colors="#58508d")
        ax.yaxis.set_minor_locator(plt.MultipleLocator(1))
        ax.grid(axis="y", linestyle="--", linewidth=0.6, color="#d4d4d4", alpha=0.7)
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)
        ax.spines['left'].set_color("#58508d")
        ax.spines['bottom'].set_color("#58508d")
        ax.legend(fontsize=12, edgecolor="#003f5c")

        # Add interactive hover functionality
        annotation = ax.annotate(
            "", xy=(0, 0), xytext=(15, 15), textcoords="offset points",
            bbox=dict(boxstyle="round", fc="white", edgecolor="black"),
            arrowprops=dict(arrowstyle="->", color="black")
        )
        annotation.set_visible(False)

        def on_hover(event):
            if event.inaxes == ax:
                for bar, looped_period in zip(bars_checked_off, tracked_period):
                    if bar.contains(event)[0]:
                        annotation.xy = (event.xdata, event.ydata)
                        annotation.set_text(f"Date: {looped_period}\nChecked Off Habits:\n" +
                                            ("\n".join(checked_off_habits[looped_period]) or "None"))
                        annotation.set_visible(True)
                        fig.canvas.draw_idle()
                        return

                for bar, looped_period in zip(bars_not_checked_off, tracked_period):
                    if bar.contains(event)[0]:
                        annotation.xy = (event.xdata, event.ydata)
                        annotation.set_text(f"Date: {looped_period}\nNot Checked Off Habits:\n" +
                                            ("\n".join(not_checked_off_habits[looped_period]) or "None"))
                        annotation.set_visible(True)
                        fig.canvas.draw_idle()
                        return

            annotation.set_visible(False)
            fig.canvas.draw_idle()

        fig.canvas.mpl_connect("motion_notify_event", on_hover)
        plt.tight_layout()
        plt.show()