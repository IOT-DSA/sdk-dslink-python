from dslink.Node import Node


class Profile:
    def __init__(self, name):
        self.name = name
        self.invoke_callback = None
        self.set_callback = None

    def run_callback(self, parameters):
        """
        Invoke the invoke callback.
        :param parameters: Parameters for callback(Node, Parameters).
        :return: Results.
        """
        if hasattr(self.invoke_callback, "__call__"):
            return self.invoke_callback(parameters)
        else:
            raise TypeError("Profile %s does not define an invoke callback" % self.name)

    def run_set_callback(self, parameters):
        """
        Invoke the set callback.
        :param parameters: Parameters for callback(Node, Value).
        :return: Results.
        """
        if hasattr(self.set_callback, "__call__"):
            return self.set_callback(parameters)
        else:
            raise TypeError("Profile %s does not define a set callback" % self.name)


class ProfileManager:
    """
    Class that holds Profiles.
    """

    def __init__(self, link):
        """
        ProfileManager Constructor.
        :param link: DSLink instance.
        """
        self.profiles = {}
        self.link = link

    def create_profile(self, profile):
        """
        Create a Profile.
        :param profile: Profile name.
        :return: Profile instance.
        """
        profile_node = self.link.responder.get_super_root().get("/defs/profile/")
        if profile in self.profiles and profile_node.has_child(profile):
            raise ValueError("Profile %s already exists" % profile)
        profile_inst = Profile(profile)
        self.profiles[profile] = profile_inst
        profile_node.add_child(Node(profile, profile_node))
        return profile_inst

    def get_profile(self, profile):
        """
        Get Profile with specified name.
        :param profile: Profile name.
        :return: Profile.
        """
        if profile not in self.profiles:
            raise ValueError("Profile %s doesn't exist" % profile)
        return self.profiles[profile]

    def register_callback(self, profile, callback):
        """
        Register a callback when the Node is invoked.
        :param profile: Profile name.
        :param callback: Callback.
        """
        if profile not in self.profiles:
            raise ValueError("Profile %s doesn't exist" % profile)
        self.profiles[profile].invoke_callback = callback

    def deregister_callback(self, profile):
        """
        Deregister an invoke callback.
        :param profile: Profile name.
        """
        if profile not in self.profiles:
            raise ValueError("Profile %s doesn't exist" % profile)
        del self.profiles[profile].invoke_callback

    def register_set_callback(self, profile, callback):
        """
        Register a callback when the Node's value is set.
        :param profile: Profile name.
        :param callback: Callback.
        """
        if profile not in self.profiles:
            raise ValueError("Profile %s doesn't exist" % profile)
        self.profiles[profile].set_callback = callback

    def deregister_set_callback(self, profile):
        """
        Deregister a set callback.
        :param profile: Profile name.
        """
        if profile not in self.profiles:
            raise ValueError("Profile %s doesn't exist" % profile)
        del self.profiles[profile].set_callback

    def get_profile_node(self, profile):
        """
        Get a profile's Node.
        :param profile: Profile name.
        :return: Profile's Node.
        """
        if profile not in self.profiles:
            raise ValueError("Profile %s doesn't exist" % profile)
        return self.link.responder.get_super_root().get("/defs/profile/%s")
