# Copyright 2018 Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: Apache-2.0

from setuptools import setup, find_packages
from os import path

here = path.abspath(path.dirname(__file__))

with open(path.join(here, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()

setup(
    name="colcon-ros-bundle",
    version="0.0.11",
    author="Matthew Murphy",
    author_email="matmur@amazon.com",
    maintainer="Matthew Murphy",
    maintainer_email="matmur@amazon.com",
    url="https://github.com/colcon/colcon-bundle/",
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Environment :: Console',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: Apache Software License',
        'Operating System :: MacOS',
        'Operating System :: Microsoft :: Windows',
        'Operating System :: POSIX',
        'Programming Language :: Python',
        'Topic :: Software Development :: Build Tools',
    ],
    license="Apache License, Version 2.0",
    keywords="colcon",
    description="Plugin for colcon to bundle ros applications",
    long_description=long_description,
    python_requires = ">=3.5",
    install_requires = [
        "colcon-bundle>=0.0.10",
        "colcon-ros>=0.3.5",
        "rosdep<=0.14.0",
        "setuptools>=30.3.0",
    ],
    tests_require=[
        'flake8',
        'flake8-blind-except',
        'flake8-builtins',
        'flake8-class-newline',
        'flake8-comprehensions',
        'flake8-deprecated',
        'flake8-docstrings',
        'flake8-import-order',
        'flake8-quotes',
        'mock',
        'pep8-naming',
        'pyenchant',
        'pylint',
        'pytest',
        'pytest-cov',
        'pytest-asyncio',
    ],
    zip_safe=True,
    include_package_data=True,
    packages=find_packages(exclude=['test', 'test.*']),
    entry_points={
        'colcon_bundle.task.bundle':[
            'ros.catkin = colcon_ros_bundle.task.catkin.bundle:RosCatkinBundle'
            'ros.cmake = colcon_ros_bundle.task.cmake.bundle:RosCmakeBundle'
        ],
        'colcon_bundle.installer':[
            'rdmanifest = colcon_ros_bundle.installer.rdmanifest:RdmanifestBundleInstallerExtensionPoint'
        ]
    }
)
