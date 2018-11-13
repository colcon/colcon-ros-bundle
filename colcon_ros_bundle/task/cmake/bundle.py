# Copyright 2018 Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: Apache-2.0

from ..ros_bundle import RosBundle


class RosCmakeBundle(RosBundle):
    """Bundle task for catkin packages."""

    def add_arguments(self, *, parser):  # noqa: D102, D205, D400
        """
        We override this so that the --exclude-ros-base argument
        isn't added twice (it will cause errors)
        """
        pass
