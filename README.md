# Happy Habit Tracker App

A fully functional habit tracker app to manage your recurrent habits and improve your lifestyle

## 1. Introduction
This project is the outcome of a university assignment having the purpose to build a simple app following an OOP approach.

While this app has the basic functionalities of a habit tracker, such as the creation, editing, deletion of habits, as well as checking them off in a daily and weekly recurrence,
it does combine the programming-app-development aspect with data analytics, by introducing some interesting graphic visualizations of your habits activity and performance.

Options available from the Analyze section, include:
- The display of a summary table where the user has the ability to sort it by different attributes
- The display of a plot showing how streaks were built and broken across time, for a chosen habit
- The display of monthly performance, as a bar graph, for a chosen habit (measuring the amount of check-offs)
- The graph display of the user's recent check-off activity, contrasting which habits were checked-off vs those that were not

While there is margin for improvement, these graphic displays are interactive and the user has the ability to mouse over to obtain additional details over the selected area.

## 2. Getting Started

### 2.1. Pre-requisites
- Python 3.x
- Sqlite3

### 2.2 Installation
Clone the following repository from GitHub:


### 2.3. Dependencies
pip install -r requirements.txt

## 3. Usage

### 3.1 Starting the App
Upon setting up your environment and installing the dependencies, run the main.py file from your terminal, 
making sure it's aimed at the correct path directory where the file is. Code to start the app.

python main.py

### 3.2. First Experience
When running for the first time, the App will welcome you; "show you around" and create 5 predefined habits for you to play around.
As these habits are created, they will be saved into a new database where going forward all your progress will be saved.

### 3.3. Navigating the App
To explore all of the app features, you will interact with the terminal where a menu and submenus will be presented to you, made available through the questionary library.

## 4. Known Limitations / Issues
As it is meant to be a simple app, some features / logics have been thought of but have not necessarily been applied 
which can either have an impact on the realistic side of the app, or instead simple expansion opportunities. These include:
- User related features: Multiple user creation; login features; first time user validation...
- Advanced habit tracking: setting up targets; flexible recurrences (not being strict to Daily vs Weekly); completion summary...
- Storing and reverting decisions: delete a check-off if the user accidentally checked-off; deleting a habit makes it irreversible and is fully removed from db...