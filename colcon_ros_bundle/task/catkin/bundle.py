# Copyright 2018 Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: Apache-2.0

from colcon_core.plugin_system import satisfies_version
from colcon_core.task import TaskExtensionPoint
from colcon_ros_bundle.task import logger
from rosdep2 import create_default_installer_context, get_default_installer, \
    RosdepLookup
from rosdep2.rospkg_loader import DEFAULT_VIEW_KEY
from rosdep2.sources_list import SourcesListLoader


class RosCatkinBundle(TaskExtensionPoint):
    """Bundle task for catkin packages."""

    def __init__(self):  # noqa: D107
        super().__init__()
        satisfies_version(TaskExtensionPoint.EXTENSION_POINT_VERSION, '^1.0')

    def add_arguments(self, *, parser):  # noqa: D102
        # TODO: This should probably use the environment variable and
        parser.add_argument(
            '--ros-distribution', default='kinetic',
            help='ROS distribution version default: kinetic')
        parser.add_argument(
            '--exclude-ros-base', action='store_true',
            help='Include ros-base in the bundle.')

    async def bundle(self):  # noqa D:102
        args = self.context.args
        verbose = False
        logger.info(
            'Bundling ROS package in "{args.path}" with build type "catkin"'
            .format_map(locals()))

        installer_context = create_default_installer_context(verbose=verbose)
        installer, installer_keys, default_key, \
            os_name, os_version = get_default_installer(
                installer_context=installer_context,
                verbose=verbose)

        sources_loader = SourcesListLoader.create_default()
        lookup = RosdepLookup.create_from_rospkg(sources_loader=sources_loader)
        lookup.verbose = True

        view = lookup.get_rosdep_view(DEFAULT_VIEW_KEY, verbose=verbose)

        for dependency in self.context.args.runtime_dependencies:
            if dependency.name in self.context.dependencies:
                logger.info('Skipping {dependency} of {args.path} because it '
                            'is in the workspace'.format_map(locals()))
                continue
            try:
                rosdep_dependency = view.lookup(dependency.name)
            except KeyError as e:
                logger.error('Could not find key for {dependency}'.format(
                    dependency=dependency.name))
                continue
            rule_installer, rule = rosdep_dependency.get_rule_for_platform(
                os_name, os_version, installer_keys, default_key)
            if rule_installer == 'source':
                logger.error(
                    '{dependency} should be built from source.'.format(
                        dependency=dependency.name))
                if 'uri' in rule.keys():
                    if 'rdmanifest' in rule['uri']:
                        args.installers['rdmanifest'].add_to_install_list(
                            dependency.name,
                            rule
                        )
            else:
                package_name_list = installer.resolve(rule)
                if len(package_name_list) > 1:
                    logger.info('{dependency} returned {package_name_list}'
                                .format_map(locals()))
                package_name = package_name_list[0]
                args.installers[rule_installer].add_to_install_list(
                    package_name)
                logger.error(
                    'Resolved {dependency} to {os_specific_dependency} '
                    'for {installer}'.format(
                        dependency=dependency.name,
                        os_specific_dependency=package_name_list,
                        installer=rule_installer))

        if not self.context.args.exclude_ros_base:
            logger.info('Including ros-base')
            try:
                ros_distro = self.context.args.ros_distribution
                args.installers['apt'].add_to_install_list(
                    'ros-{ros_distro}-ros-base'.format_map(locals()))
            except KeyError:
                logger.error('Could not find package')
