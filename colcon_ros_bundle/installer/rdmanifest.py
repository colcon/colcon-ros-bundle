# Copyright 2018 Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: Apache-2.0

import os
import stat
import subprocess
from subprocess import PIPE
import tempfile
from urllib.request import urlretrieve

from colcon_bundle.installer import BundleInstallerExtensionPoint
from colcon_core.logging import colcon_logger
from rosdep2.platforms.source import download_rdmanifest, get_file_hash, \
    load_rdmanifest, SourceInstall

logger = colcon_logger.getChild(__name__)


class RdmanifestBundleInstallerExtensionPoint(BundleInstallerExtensionPoint):
    """
    Install a library defined by an rdmanifest into a bundle.

    rdmanifest format is defined here: http://www.ros.org/reps/rep-0112.html

    This installer expects that the rdmanifest uses the environment variable
    COLCON_BUNDLE_INSTALL_PREFIX when configuring the installation
    of the library.

    Example:

        cmake -DCMAKE_INSTALL_PREFIX:PATH=${COLCON_BUNDLE_INSTALL_PREFIX}

    """

    def __init__(self):  # noqa: D107
        self._items = {}

    def initialize(self, context):  # noqa: D102
        self.context = context

    def add_to_install_list(self, name, metadata=None):  # noqa: D102
        self._items[name] = metadata

    def remove_from_install_list(self, name, metadata=None):  # noqa: D102
        pass

    def install(self):  # noqa: D102
        for name, metadata in self._items.items():
            logger.info('Installing {name}'.format(name=name))
            uri = metadata['uri']
            usr_prefix_path = os.path.join(self.context.prefix_path, 'usr')
            _install_rdmanifest(uri, usr_prefix_path)


def _install_rdmanifest(uri, prefix):
    if os.path.isfile(uri):
        with open(uri, 'r') as f:
            contents = f.read()
            manifest = load_rdmanifest(contents)
            source_install = SourceInstall.from_manifest(manifest, uri)
            _install_source(source_install)
    else:
        logger.info('Downloading rdmanifest')
        manifest, url = download_rdmanifest(uri, None)
        source_install = SourceInstall.from_manifest(manifest, url)
        _install_source(source_install, prefix)


def _install_source(resolved, prefix):
    import shutil
    import tarfile
    import tempfile

    tempdir = tempfile.mkdtemp()
    logger.info('created tmpdir [%s]' % (tempdir))

    logger.info('Fetching tarball %s' % resolved.tarball)

    # compute desired download path
    filename = os.path.join(tempdir, os.path.basename(resolved.tarball))
    f = urlretrieve(resolved.tarball, filename)
    assert f[0] == filename

    if resolved.tarball_md5sum:
        logger.info('Checking md5sum on tarball')
        hash1 = get_file_hash(filename)
        if resolved.tarball_md5sum != hash1:
            # try backup tarball if it is defined
            if resolved.alternate_tarball:
                f = urlretrieve(resolved.alternate_tarball)
                filename = f[0]
                hash2 = get_file_hash(filename)
                if resolved.tarball_md5sum != hash2:
                    logger.error('md5checksum failed')
                    raise RuntimeError()
            else:
                logger.error('md5checksum failed')
                raise RuntimeError()
    else:
        logger.info('No md5sum defined for tarball, not checking.')

    tarf = tarfile.open(filename)
    tarf.extractall(tempdir)

    command = resolved.install_command
    path = os.path.join(tempdir, resolved.exec_path)
    success = _execute(command, prefix, path)

    if success:
        logger.info('Successfully installed from source.')
    else:
        raise RuntimeError()

    logger.info('cleaning up tmpdir [%s]' % tempdir)
    shutil.rmtree(tempdir)


def _execute(script, prefix=None, path=None):
    """
    Execute a shell script.

    Setting prefix will add the environment variable
    COLCON_BUNDLE_INSTALL_PFREFIX equal to the passed in value

    :param str script: script to execute
    :param str prefix: the installation prefix
    :param str path: (optional) path to temp directory, or ``None`` to use
    default temp directory, ``str``
    """
    path = tempfile.gettempdir() if path is None else path
    result = 1
    try:
        fh = tempfile.NamedTemporaryFile('w', delete=False)
        fh.write(script)
        fh.close()
        print('Executing script below with cwd=%s\n{{{\n%s\n}}}\n' %
              (path, script))
        try:
            os.chmod(fh.name, stat.S_IRWXU)
            env = os.environ.copy()
            if prefix is not None:
                env['COLCON_BUNDLE_INSTALL_PREFIX'] = prefix
            result = subprocess.run(
                fh.name, cwd=path, env=env, stdout=PIPE, stderr=PIPE,
                universal_newlines=True)
            if result.stdout is not None:
                logger.debug('stdout output: \n' + result.stdout)
            if result.stderr is not None:
                logger.warn('stderr output: \n' + result.stderr)
        except OSError as ex:
            print('Execution failed with OSError: %s' % ex)
    finally:
        if os.path.exists(fh.name):
            os.remove(fh.name)
    logger.info('Return code was: %s' % result)
    return result.returncode == 0
