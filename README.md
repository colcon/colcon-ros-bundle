# colcon-ros-bundle [![GitHub Action Status][action-badge]][action-workflow]

This package is a plugin to [colcon-core](https://github.com/colcon/colcon-core.git),
that contains extensions for [colcon-bundle](https://github.com/colcon/colcon-bundle).

**NOTE:** `colcon-ros-bundle` only supports Ubuntu Xenial, Ubuntu Bionic, Ubuntu Focal operating systems and x86, ARMHF, and ARM64 architectures. All other operating systems and architectures are currently not supported. This code is in active development and **should not** be considered stable. 

With this package you can use `colcon bundle` to create bundles of ROS applications. A
bundle is a portable environment that allows for execution  of the
bundled application on a Linux host that does not have the application
or its dependencies installed in the root filesystem.

[action-badge]: https://github.com/colcon/colcon-ros-bundle/workflows/Test%20colcon-ros-bundle/badge.svg
[action-workflow]: https://github.com/colcon/colcon-ros-bundle/actions
