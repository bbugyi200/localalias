"""Tests command functionality."""

import collections
import json
import os
import tempfile
import unittest.mock as mock

import pytest

from localalias import commands

pytestmark = pytest.mark.usefixtures("debug_mode")


@pytest.fixture
def cleandir():
    """Run tests in an empty directory."""
    newpath = tempfile.mkdtemp()
    os.chdir(newpath)


alias_dict = {'multiline': 'echo "Hello"\necho "world!"',
              'run': 'python main.py',
              'T': 'pytest test_main.py'}
show_expected = {'run': 'run() {{ {0}; }}\n'.format(alias_dict['run']),
                 'T': 'T() {{ {0}; }}\n'.format(alias_dict['T']),
                 'multiline': 'multiline() {{\n\t{0}\n}}\n'.format(alias_dict['multiline'].replace('\n', '\n\t'))}


@pytest.fixture
def local_db():
    """Setup/teardown a local alias database."""
    filename = commands.Command.LOCALALIAS_DB_FILENAME
    with open(filename, 'w') as f:
        json.dump(alias_dict, f)
    yield alias_dict
    os.remove(filename)


@pytest.fixture(params=[
    ('run', False, show_expected['run']),
    ('multiline', False, show_expected['multiline']),
    (None, False, '{0}\n{1}\n{2}'.format(show_expected['T'], show_expected['multiline'], show_expected['run']))
], ids=['run', 'multiline', 'None'])
def cmd_args(request):
    """Returns a named tuple of command arguments and expected results."""
    Args = collections.namedtuple('Args', ['alias', 'color', 'expected'])
    args = Args(request.param[0], request.param[1], request.param[2])
    return args


@pytest.fixture
def show_cmd(cmd_args):
    """Builds and returns show command."""
    show_cmd = commands.Show(cmd_args.alias, color=cmd_args.color)
    show_cmd.expected = cmd_args.expected
    return show_cmd


def test_show_command(capsys, cleandir, local_db, show_cmd):
    """Tests show command."""
    show_cmd()
    captured = capsys.readouterr()
    assert captured.out == show_cmd.expected


def test_show_command_failure(cleandir, show_cmd):
    """Tests show command fails properly when no local alias database exists."""
    with pytest.raises(RuntimeError):
        show_cmd()
