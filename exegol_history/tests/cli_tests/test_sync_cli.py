import subprocess
import sys
import pytest
import types
from typing import Any
from exegol_history.cli.functions import CREDS_SUBCOMMAND, unset_objects
from exegol_history.cli.utils import CREDS_VARIABLES, write_credential_in_profile
from exegol_history.db_api.creds import Credential
from exegol_history.tests.common import (
    DOMAIN_TEST_VALUE,
    HASH_TEST_VALUE,
    PASSWORD_TEST_VALUE,
    USERNAME_TEST_VALUE,
)

def test_sync_nxc(load_mock_config: dict[str, Any]):
    pass

def test_sync_msf(load_mock_config: dict[str, Any]):
    pass
