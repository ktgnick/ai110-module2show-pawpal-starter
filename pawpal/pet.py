"""Pet: one animal and the care tasks belonging to it."""


class Pet:
    """A pet owned by an Owner. Holds its own list of Tasks."""

    def __init__(self, name, species=None, breed=None):
        """
        name: str
        species: str or None, e.g. "dog" | "cat"
        breed: str or None
        """
        self.name = name
        self.species = species
        self.breed = breed
        self.tasks = []  # list[Task]

    def add_task(self, task):
        """Attach a Task to this pet. STUB."""
        raise NotImplementedError

    def remove_task(self, task):
        """Detach a Task from this pet. STUB."""
        raise NotImplementedError

    def get_tasks(self):
        """Return this pet's tasks. STUB."""
        raise NotImplementedError
