# Copyright 2018 Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: Apache-2.0

from colcon_bundle.verb.bundle import BundlePackageArguments
from colcon_core.dependency_descriptor import DependencyDescriptor
from colcon_core.package_descriptor import PackageDescriptor
from colcon_core.task import TaskContext
from colcon_ros_bundle.task.ros_bundle import RosBundle
from mock import MagicMock, patch
import pytest


def test_add_arguments():
    parser = MagicMock()
    task = RosBundle()
    task.add_arguments(parser=parser)

    calls = parser.add_argument.call_args_list

    assert calls[0][0][0] == '--exclude-ros-base'


@pytest.mark.asyncio
async def test_bundle():
    pkg = PackageDescriptor('package/path')
    pkg.name = 'MyPackageName'
    pkg.dependencies['run'] = {
        DependencyDescriptor('source_pkg'),
        DependencyDescriptor('other_pkg'),
        DependencyDescriptor('system_pkg')
    }
    installers = {
        'rdmanifest': MagicMock(),
        'system': MagicMock(),
        'other': MagicMock()
    }
    top_level_args = MagicMock(build_base='build/base',
                               install_base='install/base',
                               bundle_base='bundle/base')
    args = BundlePackageArguments(pkg, installers, top_level_args)
    args.ros_distribution = 'kinetic'
    args.exclude_ros_base = True

    context = TaskContext(pkg=pkg, args=args, dependencies={})
    task = RosBundle()
    task.set_context(context=context)

    # Concise read on why it's patched this way.
    # http://www.voidspace.org.uk/python/mock/patch.html#where-to-patch
    with patch('colcon_ros_bundle.task.ros_bundle.RosdepWrapper') as wrapper: # noqa: E501
        wrapper().get_rule.side_effect = _get_rule_side_effect
        wrapper().resolve.side_effect = _resolve_side_effect
        await task.bundle()

    installers['rdmanifest'].add_to_install_list.assert_called_with(
        'source_pkg', {'s': 'ource', 'uri': 'rdmanifest'})
    installers['other'].add_to_install_list.assert_called_with(
        'other_pkg_name')
    installers['system'].add_to_install_list.assert_called_with(
        'system_pkg_name')


def _get_rule_side_effect(name):
    if name == 'source_pkg':
        return 'source', {'s': 'ource', 'uri': 'rdmanifest'}
    if name == 'other_pkg':
        return 'other', {'o': 'ther'}
    if name == 'system_pkg':
        return 'system', {'s': 'ystem'}
    else:
        raise RuntimeError()


def _resolve_side_effect(rule):
    if rule == {'o': 'ther'}:
        return ['other_pkg_name']
    if rule == {'s': 'ystem'}:
        return ['system_pkg_name']
    else:
        raise RuntimeError()


@pytest.mark.asyncio
async def test_include_ros_base():
    pkg = PackageDescriptor('package/path')
    pkg.name = 'MyPackageName'
    pkg.dependencies['run'] = {}
    installers = {
        'apt': MagicMock(),
    }
    top_level_args = MagicMock(build_base='build/base',
                               install_base='install/base',
                               bundle_base='bundle/base')
    args = BundlePackageArguments(pkg, installers, top_level_args)
    args.ros_distribution = 'kinetic'
    args.exclude_ros_base = False

    context = TaskContext(pkg=pkg, args=args, dependencies={})
    task = RosBundle()
    task.set_context(context=context)

    # Concise read on why it's patched this way.
    # http://www.voidspace.org.uk/python/mock/patch.html#where-to-patch
    with patch('colcon_ros_bundle.task.ros_bundle.RosdepWrapper') as wrapper: # noqa: E501
        with patch('os.environ') as environ:
            environ.__getitem__.side_effect = access_var
            wrapper().get_rule.side_effect = _get_rule_side_effect
            wrapper().resolve.side_effect = _resolve_side_effect
            await task.bundle()

    installers['apt'].add_to_install_list.assert_called_with(
        'ros-kinetic-ros-base')


def access_var(key):
    if key == 'ROS_DISTRO':
        return 'kinetic'
    else:
        return None


@pytest.mark.asyncio
async def test_exclude_ros_base():
    pkg = PackageDescriptor('package/path')
    pkg.name = 'MyPackageName'
    pkg.dependencies['run'] = {}
    installers = {
        'apt': MagicMock(),
    }
    top_level_args = MagicMock(build_base='build/base',
                               install_base='install/base',
                               bundle_base='bundle/base')
    args = BundlePackageArguments(pkg, installers, top_level_args)
    args.ros_distribution = 'kinetic'
    args.exclude_ros_base = False

    context = TaskContext(pkg=pkg, args=args, dependencies={})
    task = RosBundle()
    task.set_context(context=context)

    # Concise read on why it's patched this way.
    # http://www.voidspace.org.uk/python/mock/patch.html#where-to-patch
    with patch('colcon_ros_bundle.task.ros_bundle.RosdepWrapper') as wrapper: # noqa: E501
        wrapper().get_rule.side_effect = _get_rule_side_effect
        wrapper().resolve.side_effect = _resolve_side_effect
        await task.bundle()

    installers['apt'].add_to_install_list.assert_not_called()
