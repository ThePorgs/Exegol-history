import io
import os
from rich.console import Console
from exegol_history.cli.functions import show_objects
from exegol_history.cli.utils import CREDS_VARIABLES
from exegol_history.tests.common import (
    DOMAIN_TEST_VALUE,
    HASH_TEST_VALUE,
    PASSWORD_TEST_VALUE,
    USERNAME_TEST_VALUE,
)


def test_show_credential_only_username():
    os.environ[CREDS_VARIABLES[0]] = USERNAME_TEST_VALUE

    console = Console(file=io.StringIO())
    show_objects(console)

    assert (
        f"""{CREDS_VARIABLES[0]}:{USERNAME_TEST_VALUE}{os.linesep}"""
        in console.file.getvalue()
    )


def test_show_credential_half():
    os.environ[CREDS_VARIABLES[0]] = USERNAME_TEST_VALUE
    os.environ[CREDS_VARIABLES[1]] = PASSWORD_TEST_VALUE

    console = Console(file=io.StringIO())
    show_objects(console)

    assert (
        f"""{CREDS_VARIABLES[0]}:{USERNAME_TEST_VALUE}{os.linesep}{CREDS_VARIABLES[1]}:{PASSWORD_TEST_VALUE}{os.linesep}"""
        in console.file.getvalue()
    )


def test_show_credential_full():
    os.environ[CREDS_VARIABLES[0]] = USERNAME_TEST_VALUE
    os.environ[CREDS_VARIABLES[1]] = PASSWORD_TEST_VALUE
    os.environ[CREDS_VARIABLES[2]] = HASH_TEST_VALUE
    os.environ[CREDS_VARIABLES[3]] = DOMAIN_TEST_VALUE

    console = Console(file=io.StringIO())
    show_objects(console)

    assert (
        f"""{CREDS_VARIABLES[0]}:{USERNAME_TEST_VALUE}{os.linesep}{CREDS_VARIABLES[1]}:{PASSWORD_TEST_VALUE}{os.linesep}{CREDS_VARIABLES[2]}:{HASH_TEST_VALUE}{os.linesep}{CREDS_VARIABLES[3]}:{DOMAIN_TEST_VALUE}{os.linesep}"""
        in console.file.getvalue()
    )
