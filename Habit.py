from datetime import date


class Habit:
    """
    Represents a habit along with its details and states.
    
    This class is used to define and manage a habit. It includes its name, a description
    of the habit, its recurrence pattern, creation date, optional completion date, and
    its current status. Habits can be tracked and updated dynamically.
    
    :ivar name: The name of the habit.
    :ivar description: A detailed description of the habit.
    :ivar recurrence: The recurrence pattern of the habit.
    :ivar creation_date: The date when the habit is created. Defaults to the current date.
    :ivar completion_date: The date when the habit was completed, if applicable.
    :ivar status: The current status of the habit. Defaults to 'active'.
    """

    def __init__(self, name, description, recurrence, creation_date=date.today(), completion_date=None,
                 status='active'):
        self.name = name
        self.description = description
        self.recurrence = recurrence
        self.creation_date = creation_date
        self.completion_date = completion_date
        self.status = status
