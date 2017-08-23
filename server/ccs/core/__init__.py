from . import color, settings

__all__ = ['color', 'settings']

# Global singletons
config = settings.Config()
user_settings = settings.UserSettings()
derived_settings = settings.DerivedSettings()

from . import api  # Just to get the functions to initialize
