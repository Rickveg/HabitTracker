from datetime import date, datetime, timedelta

import matplotlib.dates as mdates
import matplotlib.pyplot as plt
import questionary
from rich.table import Table

from DBManager import DatabaseManager
from HabitManager import HabitManager


class HabitAnalyzer:
    """ Provides methods to analyze user habits, including sorting habit summaries and viewing different chart types."""
    def __init__(self, text_theme):
        self.db_manager = DatabaseManager()
        self.manager = HabitManager(text_theme)
        self.console, self.custom_style = text_theme

    # SUMMARY TABLE

    def view_habits_summary(self):
        """
        Provides a comprehensive summary of all habits stored in the database.

        This method retrieves habit data from the database, calculates relevant metrics
        for each habit, and organizes the information into a structured summary.

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
              or "Not Checked_Off", for current day.
            - Current Streak (int): The current streak count for the habit.
            - Longest Streak (int): The longest recorded streak for the habit.
            - % Performance (float): The performance percentage of the habit over its lifecycle.
            - Rank (str): A textual ranking derived from the performance percentage
              ("Outstanding", "Excellent", "Very Good", "Good", "Inconsistent", "Poor", or "Unknown").

        """
        habits = self.db_manager.fetch_all_habits()
        if not habits:
            self.console.print("[bold red]No habits found.[/bold red]")
            return

        data = []

        # Attribute a rank to a % value
        rank_mapping = {
            (100, 101): "Outstanding",
            (91, 100): "Excellent",
            (70, 91): "Very Good",
            (60, 70): "Good",
            (40, 60): "Inconsistent",
            (0, 40): "Poor"
        }

        # Get all stats for each habit in the database, including streaks and performance.
        for habit in habits:
            habit_id, name, description, recurrence, *_ = habit
            creation_date = self.db_manager.get_creation_date(habit_id)
            status = self.db_manager.get_status(habit_id)
            completion_date = self.db_manager.get_completion_date(habit_id)
            current_streak = self.db_manager.get_current_streak(habit_id)
            if isinstance(current_streak, str):
                try:
                    current_streak = int(current_streak.split()[0])
                except ValueError:
                    current_streak = 0
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

        # Apply text enrichment in conditional formatting
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

        self.console.print(df_table)
        return data

    @staticmethod
    def sort_habits_summary(data, console=None, custom_style=None):
        """
        Sort a list of habits based on user-selected attributes and display the sorted
        data in a formatted table.
        """
        sort_options = [
            "Name", "Recurrence", "Creation Date", "Status", "Completion Date",
            "Check_off Status", "Current Streak", "Longest Streak",
            "Performance", "Rank", "Cancel"
        ]

        # Prompt user for sorting attribute
        sort_choice = questionary.select(
            "Select attribute to sort by:",
            choices=sort_options, style=custom_style
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
            habit_performance_style = "green" if row[8] >= 65 else "red"
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

    def view_habit_streak_progress(self, selected_habit):
        """
        Displays and plots the progress of streaks for a selected habit, including interactive visualization.

        The method retrieves all habits from the database, allows the user to select a specific habit,
        and calculates streak progress based on recurrence (daily or weekly). The progress is visualized
        using a line plot where streak information is displayed interactively.

        """

        if selected_habit == "Cancel":
            return

        # Check whether there are any existing habits.
        if not selected_habit:
            self.console.print("No habits to view. You must first create a habit and progress.", style="warning")
            return

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
        line, = ax.plot(full_date_range, streaks, marker="o", label="Streak Count", linestyle='-', color='olivedrab')
        ax.set_facecolor("#f7f7f7")  # Set background color
        ax.set_xlabel("Date", fontsize=14, fontweight="bold",
                      color="#333333")  # Set font size and color for x-axis label
        ax.set_ylabel("Streak", fontsize=14, fontweight="bold",
                      color="#333333")  # Set font size and color for y-axis label
        ax.set_title(f"Streak Progress", fontsize=16, fontweight="bold", loc="left")
        ax.set_title(f"Habit: {name}", fontsize=16, color="grey", loc="right")
        if recurrence == "Weekly":
            ax.xaxis.set_major_locator(mdates.WeekdayLocator(interval=2))
            ax.xaxis.set_major_formatter(mdates.DateFormatter("%d - %b - %Y"))
        else:
            ax.xaxis.set_major_locator(mdates.DayLocator(interval=14))
            ax.xaxis.set_major_formatter(mdates.DateFormatter("%d - %b - %Y"))
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)
        ax.spines['bottom'].set_color('#333333')
        ax.spines['left'].set_color('#333333')
        ax.tick_params(axis="x", rotation=45, labelsize=10, colors="#333333")  # Adjust tick label size and color
        ax.tick_params(axis="y", labelsize=10, colors="#333333")  # Adjust y-axis tick label size and color
        ax.legend(fontsize=12, edgecolor="#333333")  # Adjust legend style and edge color

        # Add interactive hover functionality
        annotation = ax.annotate(
            "", xy=(0, 0), xytext=(15, 15), textcoords="offset points",
            bbox=dict(boxstyle="round", fc="white", edgecolor="navajowhite"),
            arrowprops=dict(arrowstyle="->", color="navajowhite")
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

    @staticmethod
    def calculate_performance_data(fixed_checkoff_dates, recurrence):
        """
        Calculate performance data for monthly performance analysis.
        Handles recurring habits (Daily/Weekly) and calculates percentages.
        """
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

        # Calculate performances
        performances = []
        sorted_months = sorted(month_summary.keys())
        for month_key in sorted_months:
            year, month = map(int, month_key.split("-"))
            days_in_month = (date(year, month + 1, 1) - date(year, month, 1)).days if month < 12 else 31
            if month == date.today().month and year == date.today().year:
                days_in_month = date.today().day
            if recurrence == "Weekly":
                weeks_in_month = (days_in_month + date(year, month, 1).weekday()) // 7 + 1
                performances.append((month_summary[month_key] / weeks_in_month) * 100)
            else:  # Daily
                performances.append((month_summary[month_key] / days_in_month) * 100)
        return sorted_months, performances

    def view_habit_monthly_performance(self, selected_habit):
        """
        Evaluates and visualizes the performance of a selected habit on a monthly basis.
        """

        if selected_habit == "Cancel":
            return

        # Check whether there are any existing habits.
        if not selected_habit:
            self.console.print("No habits to view. You must first create a habit and progress.", style="warning")
            return

        habit_id, name, description, recurrence, *_ = selected_habit

        # Fetch habit's check-off information
        checkoff_dates = self.db_manager.fetch_daily_checkoff_info(habit_id)
        if not checkoff_dates:
            print(f"No check-off data found for habit: {name}")
            return

        fixed_checkoff_dates = [date.fromisoformat(record[0]) for record in checkoff_dates]
        sorted_months, performances = self.calculate_performance_data(fixed_checkoff_dates, recurrence)

        # Configure x-axis limit based on recurrence
        x_limit = 31 if recurrence == "Daily" else 5

        # Calculate the actual check-off counts per month
        month_summary = {}
        for d in fixed_checkoff_dates:
            month_key = d.strftime("%Y-%m")
            month_summary[month_key] = month_summary.get(month_key, 0) + 1

        counts = [month_summary.get(month, 0) for month in sorted_months]

        # Determine bar colors based on performance
        import matplotlib.cm as cm
        import matplotlib.colors as mcolors

        cmap = cm.get_cmap('RdYlGn', 100)  # Use the 'YlGn' colormap for sequential color
        norm = mcolors.Normalize(vmin=1, vmax=100)  # Normalize performance range to 1-100

        bar_colors = [mcolors.to_hex(cmap(norm(performance))) for performance in performances]

        # Plot horizontal bar graph with enhanced style
        fig, ax = plt.subplots(figsize=(12, 8))
        bars = ax.barh(sorted_months, counts, color=bar_colors, edgecolor="black", linewidth=1)
        ax.set_xlim(0, x_limit)
        ax.set_ylabel("Month", fontsize=14, fontweight="bold")
        ax.set_xlabel("Check-offs", fontsize=14, fontweight="bold")
        ax.set_title(f"Monthly Performance", fontsize=16, fontweight="bold", loc="left")
        ax.set_title(f"Habit: {name}", fontsize=16, color="grey", loc="right")
        ax.grid(axis="x", linestyle="--", alpha=0.7)

        # Convert the y-ticks to display text with the month name and year
        months_with_year = [datetime.strptime(month, "%Y-%m").strftime("%b - %Y") for month in sorted_months]
        ax.set_yticks(range(len(sorted_months)))
        ax.set_yticklabels(months_with_year, fontsize=11)
        ax.tick_params(axis="x", labelsize=12)
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
                for bar, count, performance, given_month in zip(bars, counts, performances, sorted_months):
                    if bar.contains(event)[0]:
                        annotation.xy = (event.xdata, event.ydata)
                        annotation.set_text(
                            f"Month: {given_month}\nCheck-offs: {count}\nPerformance: {performance:.2f}%"
                        )
                        annotation.set_visible(True)
                        fig.canvas.draw_idle()
                        return

            annotation.set_visible(False)
            fig.canvas.draw_idle()

        fig.canvas.mpl_connect("motion_notify_event", on_hover)
        plt.show()

    def view_all_habits_performance(self):
        """
        Displays a multi-line chart showing the performance of all habits over time.
        """
        habits = self.db_manager.fetch_all_habits()
        if not habits:
            self.console.print("[bold red]No habits found to display performance.[/bold red]")
            return

        # Prepare data for each habit
        habit_data = {}
        for habit in habits:
            habit_id, name, description, recurrence, *_ = habit
            checkoff_dates = self.db_manager.fetch_daily_checkoff_info(habit_id)
            if not checkoff_dates:
                continue

            fixed_checkoff_dates = [date.fromisoformat(record[0]) for record in checkoff_dates]
            sorted_months, performances = self.calculate_performance_data(fixed_checkoff_dates, recurrence)
            habit_data[name] = (sorted_months, performances)

        if not habit_data:
            self.console.print("[bold yellow]No performance data available for the selected habits.[/bold yellow]")
            return

        # Plot data
        fig, ax = plt.subplots(figsize=(14, 8))
        ax.set_title("All Habits Performance Over Time", fontsize=16, fontweight="bold", loc="left")
        ax.set_xlabel("Month", fontsize=14, fontweight="bold")
        ax.set_ylabel("% Performance", fontsize=14, fontweight="bold")
        ax.set_ylim(0, 100)  # Performance percentage range
        ax.grid(axis="y", linestyle="--", alpha=0.7)

        lines = {}
        for habit, (months, performances) in habit_data.items():
            months_numeric = [mdates.date2num(datetime.strptime(month, "%Y-%m")) for month in months]
            line, = ax.plot(
                months_numeric,
                performances,
                marker="o", label=habit, linestyle="-"
            )
            lines[line] = (months_numeric, performances, months, habit)

        ax.legend(fontsize=12, loc="upper left", bbox_to_anchor=(1, 1))

        # Combine and sort months from all habits for x-ticks
        all_months = sorted(set(m for habit in habit_data.values() for m in habit[0]))
        all_months_numeric = [mdates.date2num(datetime.strptime(month, "%Y-%m")) for month in all_months]
        plt.xticks(
            all_months_numeric,
            [datetime.strptime(month, "%Y-%m").strftime("%b - %Y") for month in all_months],
            rotation=45
        )
        plt.tight_layout()

        # Hover functionality
        annotation = ax.annotate(
            "", xy=(0, 0), xytext=(15, 15), textcoords="offset points",
            bbox=dict(boxstyle="round", fc="white", edgecolor="black"),
            arrowprops=dict(arrowstyle="->", color="black")
        )
        annotation.set_visible(False)

        def on_hover(event):
            if event.inaxes == ax:
                for l, (xdata, ydata, given_months, hab) in lines.items():
                    if l.contains(event)[0]:
                        for x, y, month in zip(xdata, ydata, given_months):
                            if abs(event.xdata - x) < 0.5 and abs(event.ydata - y) < 5:
                                annotation.set_text(
                                    f"Habit: {hab}\nMonth: {month}\n% Performance: {y:.2f}")
                                annotation.xy = (x, y)
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
        """

        habits = self.db_manager.fetch_all_habits()
        if not habits:
            self.console.print("No habits found.", style="warning")
            return

        # Prompt user to choose between daily or weekly view
        recurrence_type = questionary.select(
            "Choose the type of habits to view recent activity:",
            choices=["Daily", "Weekly", "Cancel"], style=self.custom_style
        ).ask()
        if recurrence_type == "Cancel":
            return

        # Filter habits by selected recurrence
        filtered_habits = [habit for habit in habits if habit[3] == recurrence_type]
        if not filtered_habits:
            self.console.print(f"No active habits with {recurrence_type.lower()} recurrence found.", style="warning")
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
        title = f"Last {'14 Days' if recurrence_type == 'Daily' else '2 Months'}"
        ax.set_title(f"Check-off Recent Activity", fontsize=16, fontweight="bold", loc="left")
        ax.set_title(title, fontsize=16, color="silver", loc="right")
        ax.set_xlabel("Date" if recurrence_type == "Daily" else "Week", fontsize=14, fontweight="bold")
        ax.set_ylabel("Active Habits", fontsize=14, fontweight="bold")
        ax.set_xticks(x)
        if recurrence_type == "Daily":
            ax.set_xticklabels([day.strftime("%d-%b") for day in tracked_period], rotation=45, fontsize=12)
        else:
            ax.set_xticklabels([f"Week {week[1]}" for week in tracked_period], rotation=45, fontsize=12)
        ax.set_yticks(range(0, max(checked_off_counts + not_checked_off_counts) + 1, 1))
        ax.tick_params(axis="y", labelsize=12)
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
            bbox=dict(boxstyle="round", fc="white", edgecolor="#58508d"),
            arrowprops=dict(arrowstyle="->", color="black")
        )
        annotation.set_visible(False)

        def on_hover(event):
            if event.inaxes == ax:
                for bar, looped_period in zip(bars_checked_off, tracked_period):
                    if bar.contains(event)[0]:
                        annotation.xy = (event.xdata, event.ydata)
                        annotation.set_text(f"Date: {looped_period}\nChecked Off:\n" +
                                            ("\n".join(checked_off_habits[looped_period]) or "None"))
                        annotation.set_visible(True)
                        fig.canvas.draw_idle()
                        return

                for bar, looped_period in zip(bars_not_checked_off, tracked_period):
                    if bar.contains(event)[0]:
                        annotation.xy = (event.xdata, event.ydata)
                        annotation.set_text(f"Date: {looped_period}\nNot Checked Off:\n" +
                                            ("\n".join(not_checked_off_habits[looped_period]) or "None"))
                        annotation.set_visible(True)
                        fig.canvas.draw_idle()
                        return

            annotation.set_visible(False)
            fig.canvas.draw_idle()

        fig.canvas.mpl_connect("motion_notify_event", on_hover)
        plt.tight_layout()
        plt.show()