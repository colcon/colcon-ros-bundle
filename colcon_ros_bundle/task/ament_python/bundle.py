# Copyright 2018 Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: Apache-2.0

import os

from colcon_core.dependency_descriptor import DependencyDescriptor
from colcon_core.plugin_system import satisfies_version
from colcon_core.task import TaskExtensionPoint
from colcon_ros_bundle.task import logger

from ..ros_bundle import RosBundle


class RosAmentPythonBundleTask(RosBundle):
    """Bundles python packages in the workspace."""

    def __init__(self):  # noqa: D107
        super().__init__()
        satisfies_version(TaskExtensionPoint.EXTENSION_POINT_VERSION, '^1.0')

    async def bundle(self):  # noqa: D102
        args = self.context.args
        verbose = False
        logger.info(
            'Bundling python package in "{self.context.pkg.path}" with build '
            'type "ament_python"'.format_map(locals()))

        await super().bundle()

        # TODO: The Pip managers should be doing this
        apt = args.installers['apt']
        apt.add_to_install_list('libpython3-dev')
        apt.add_to_install_list('python3-pip')
