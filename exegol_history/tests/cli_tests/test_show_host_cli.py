import io
import os
from rich.console import Console
from exegol_history.cli.functions import show_objects
from exegol_history.cli.utils import HOSTS_VARIABLES
from exegol_history.tests.common import (
    HOSTNAME_TEST_VALUE,
    IP_TEST_VALUE,
    ROLE_TEST_VALUE,
)


def test_show_host_only_ip():
    os.environ[HOSTS_VARIABLES[0]] = IP_TEST_VALUE

    console = Console(file=io.StringIO())
    show_objects(console)

    assert (
        f"""{HOSTS_VARIABLES[0]}:{IP_TEST_VALUE}\n"""
        in console.file.getvalue()
    )


def test_show_host_half():
    os.environ[HOSTS_VARIABLES[0]] = IP_TEST_VALUE
    os.environ[HOSTS_VARIABLES[1]] = HOSTNAME_TEST_VALUE

    console = Console(file=io.StringIO())
    show_objects(console)

    assert (
        f"""{HOSTS_VARIABLES[0]}:{IP_TEST_VALUE}\n{HOSTS_VARIABLES[1]}:{HOSTNAME_TEST_VALUE}\n"""
        in console.file.getvalue()
    )


def test_show_host_full():
    os.environ[HOSTS_VARIABLES[0]] = IP_TEST_VALUE
    os.environ[HOSTS_VARIABLES[1]] = HOSTNAME_TEST_VALUE
    os.environ[HOSTS_VARIABLES[2]] = ROLE_TEST_VALUE

    console = Console(file=io.StringIO())
    show_objects(console)

    assert (
        f"""{HOSTS_VARIABLES[0]}:{IP_TEST_VALUE}\n{HOSTS_VARIABLES[1]}:{HOSTNAME_TEST_VALUE}\n{HOSTS_VARIABLES[2]}:{ROLE_TEST_VALUE}\n"""
        in console.file.getvalue()
    )
