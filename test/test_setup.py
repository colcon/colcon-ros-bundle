# Copyright 2018 Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: Apache-2.0

import colcon_ros_bundle


def test_version():
    version = colcon_ros_bundle.__version__
    assert version == '0.0.4'
