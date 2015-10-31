class Profile:
    def __init__(self, name):
        self.name = name
        self.callback = None


class ProfileManager:
    def __init__(self):
        self.profiles = {}

    def create_profile(self, profile):
        if profile.name in self.profiles:
            raise ValueError("Profile %s already exists" % profile.name)
        self.profiles[profile.name] = profile

    def register_callback(self, profile, callback):
        if profile not in self.profiles:
            raise ValueError("Profile %s doesn't exist" % profile)
        self.profiles[profile].callback = callback

    def deregister_callback(self, profile):
        if profile not in self.profiles:
            raise ValueError("Profile %s doesn't exist" % profile)
        self.profiles[profile].callback = None
