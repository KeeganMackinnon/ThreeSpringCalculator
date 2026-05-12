# configs.py

from copy import deepcopy


class ConfigLibrary:
    """
    Temporary in-memory config library.

    This saves spring stack configurations without saving/changing global test inputs
    like applied load, preload turns, adjuster pitch, or measured collar length.
    """

    def __init__(self):
        self._configs = {}

    def save_config(self, name, stack):
        if not name:
            raise ValueError("Config name cannot be empty.")

        self._configs[name] = deepcopy(stack)

    def load_config(self, name):
        if name not in self._configs:
            raise KeyError(f"Config '{name}' does not exist.")

        return deepcopy(self._configs[name])

    def delete_config(self, name):
        if name in self._configs:
            del self._configs[name]

    def names(self):
        return sorted(self._configs.keys())

    def all_configs(self):
        return {
            name: deepcopy(stack)
            for name, stack in self._configs.items()
        }