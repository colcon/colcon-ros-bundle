from rosdep2 import create_default_installer_context, get_default_installer, \
    RosdepLookup
from rosdep2.rospkg_loader import DEFAULT_VIEW_KEY
from rosdep2.sources_list import SourcesListLoader


class RosdepWrapper():
    """
    Wrapper around rosdep.

    Hides all the configuration of rosdep from the caller.
    """

    def __init__(self):  # noqa: D107
        installer_context = create_default_installer_context(verbose=False)
        self.installer, self.installer_keys, self.default_key, \
            self.os_name, self.os_version = get_default_installer(
                installer_context=installer_context, verbose=False)

        sources_loader = SourcesListLoader.create_default()
        lookup = RosdepLookup.create_from_rospkg(sources_loader=sources_loader)
        lookup.verbose = True

        self.view = lookup.get_rosdep_view(DEFAULT_VIEW_KEY, verbose=False)

    def get_rule(self, name):
        """
        Resolve a ROS package name into an installer and rules for the install.

        :param name: ROS package name
        :return: name, rosdep_rules
        :rtype: tuple(str, dict)
        :raises: :exc:`KeyError` if the package is not in the rosdep database
        :raises: :exc:`ResolutionError` If no rule is available
        :raises: :exc:`InvalidData` If rule data is not valid
        """
        rosdep_dependency = self.view.lookup(name)
        installer_name, rule = rosdep_dependency.get_rule_for_platform(
            self.os_name, self.os_version, self.installer_keys,
            self.default_key)
        return installer_name, rule

    def resolve(self, rule):
        """Resolve a rule into a list of packages."""
        return self.installer.resolve(rule)
