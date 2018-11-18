# Copyright 2018 Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: Apache-2.0

import os

from colcon_core.plugin_system import satisfies_version
from colcon_core.task import TaskExtensionPoint
from colcon_ros_bundle.task import logger
from colcon_ros_bundle.task.catkin._rosdep import RosdepWrapper


class RosBundle(TaskExtensionPoint):
    """Bundle task for catkin packages."""

    def __init__(self):  # noqa: D107
        super().__init__()
        satisfies_version(TaskExtensionPoint.EXTENSION_POINT_VERSION, '^1.0')

    def add_arguments(self, *, parser):  # noqa: D102
        parser.add_argument(
            '--exclude-ros-base', action='store_true',
            help='Do not add ros-base package to the bundle')

    async def bundle(self):  # noqa D:102
        args = self.context.args
        logger.info(
            'Bundling ROS package in "{self.context.pkg.path}" '
            'with build type "catkin"'.format_map(locals()))

        rosdep = RosdepWrapper()
        for dependency in self.context.pkg.dependencies['run']:
            if dependency.name in self.context.dependencies:
                logger.info('Skipping {dependency} of {self.context.pkg.name} '
                            'because it is in the workspace'
                            .format_map(locals()))
                continue
            try:
                rule_installer, rule = rosdep.get_rule(dependency.name)
            except KeyError:
                logger.error('Could not find key for {dependency}'.format(
                    dependency=dependency.name))
                continue

            if rule_installer == 'source':
                logger.info(
                    '{dependency} should be built from source.'.format(
                        dependency=dependency.name))
                if 'uri' in rule.keys():
                    if 'rdmanifest' in rule['uri']:
                        args.installers['rdmanifest'].add_to_install_list(
                            dependency.name,
                            rule
                        )
                else:
                    logger.error('{dependency} should be built from source '
                                 'but does not link to an rdmanifest'
                                 .format(dependency=dependency.name))
            else:
                # If the package requires pip, ensure pip is installed
                # in the bundle
                if rule_installer == 'pip':
                    args.installers['apt'].add_to_install_list('python-pip')

                package_name_list = rosdep.resolve(rule)
                if len(package_name_list) > 1:
                    logger.info('{dependency} returned {package_name_list}'
                                .format_map(locals()))
                package_name = package_name_list[0]
                args.installers[rule_installer].add_to_install_list(
                    package_name)
                logger.info(
                    'Resolved {dependency} to {os_specific_dependency} '
                    'for {installer}'.format(
                        dependency=dependency.name,
                        os_specific_dependency=package_name_list,
                        installer=rule_installer))

        if not False:
            logger.info('Including ros-base')
            try:
                ros_distro = os.environ['ROS_DISTRO']
                if ros_distro is not None:
                    args.installers['apt'].add_to_install_list(
                        'ros-{ros_distro}-ros-base'.format(
                            ros_distro=ros_distro))
                else:
                    logger.error('ROS_DISTRO is not defined make sure to'
                                 'source your ROS environment.')
                    raise RuntimeError('ROS_DISTRO environment variable '
                                       'not defined.')
            except KeyError:
                logger.error('Could not find package')
