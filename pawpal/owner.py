"""Owner: the pet owner, their pets, preferences, and daily time budget."""


class Owner:
    """A pet owner. Holds pets, preferences, and available time for the day."""

    def __init__(self, name, available_minutes=0, preferences=None):
        """
        name: str
        available_minutes: int, total time budget for today's plan
        preferences: dict or None, e.g. {"no_meds_after": "20:00"}
        """
        self.name = name
        self.available_minutes = available_minutes
        self.preferences = preferences if preferences is not None else {}
        self.pets = []  # list[Pet]

    def add_pet(self, pet):
        """Attach a Pet to this owner. STUB."""
        raise NotImplementedError

    def set_available_time(self, minutes):
        """Set the daily time budget in minutes. STUB."""
        raise NotImplementedError

    def set_preference(self, key, value):
        """Set a single preference. STUB."""
        raise NotImplementedError
