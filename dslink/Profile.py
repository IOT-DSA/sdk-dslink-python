from dslink.Node import Node


class Profile:
    def __init__(self, name):
        self.name = name
        self.callback = None

    def run_callback(self, parameters):
        if hasattr(self.callback, "__call__"):
            return self.callback(parameters)
        else:
            raise TypeError("Profile %s does not define a callback" % self.name)


class ProfileManager:
    def __init__(self, link):
        self.profiles = {}
        self.link = link

    def create_profile(self, profile):
        profile_node = self.link.super_root.get("/defs/profile/")
        if profile in self.profiles and profile_node.has_child(profile):
            raise ValueError("Profile %s already exists" % profile)
        self.profiles[profile] = Profile(profile)
        profile_node.add_child(Node(profile, profile_node))

    def get_profile(self, profile):
        if profile not in self.profiles:
            raise ValueError("Profile %s doesn't exist" % profile)
        return self.profiles[profile]

    def register_callback(self, profile, callback):
        if profile not in self.profiles:
            raise ValueError("Profile %s doesn't exist" % profile)
        self.profiles[profile].callback = callback

    def deregister_callback(self, profile):
        if profile not in self.profiles:
            raise ValueError("Profile %s doesn't exist" % profile)
        self.profiles[profile].callback = None

    def get_profile_node(self, profile):
        if profile not in self.profiles:
            raise ValueError("Profile %s doesn't exist" % profile)
        return self.link.super_root.get("/defs/profile/%s")
