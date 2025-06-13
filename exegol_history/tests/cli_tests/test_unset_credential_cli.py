import subprocess
import sys
import pytest
from typing import Any
from exegol_history.cli.functions import unset_objects
from exegol_history.cli.utils import CREDS_VARIABLES, write_credential_in_profile
from exegol_history.db_api.creds import Credential
from exegol_history.tests.common import (
    DOMAIN_TEST_VALUE,
    HASH_TEST_VALUE,
    PASSWORD_TEST_VALUE,
    USERNAME_TEST_VALUE,
)


@pytest.mark.skipif(sys.platform.startswith("win"), reason="require Linux")
def test_unset_credential(load_mock_config: dict[str, Any]):
    credential = Credential(
        "1",
        USERNAME_TEST_VALUE,
        PASSWORD_TEST_VALUE,
        HASH_TEST_VALUE,
        DOMAIN_TEST_VALUE,
    )

    write_credential_in_profile(credential, load_mock_config)
    command_output = subprocess.run(
        [
            "bash",
            "-c",
            f"source {load_mock_config['paths']['profile_sh_path']} && echo ${CREDS_VARIABLES[0]} ${CREDS_VARIABLES[1]} ${CREDS_VARIABLES[2]} ${CREDS_VARIABLES[3]}",
        ],
        stdout=subprocess.PIPE,
    )
    envs_set = command_output.stdout.decode("utf8")

    # Reference: https://medium.com/python-pandemonium/testing-sys-exit-with-pytest-10c6e5f7726f
    with pytest.raises(SystemExit) as exit:
        unset_objects(load_mock_config, {})
        assert exit.value.code == 0

    command_output = subprocess.run(
        [
            "bash",
            "-c",
            f"source {load_mock_config['paths']['profile_sh_path']} && echo ${CREDS_VARIABLES[0]} ${CREDS_VARIABLES[1]} ${CREDS_VARIABLES[2]} ${CREDS_VARIABLES[3]}",
        ],
        stdout=subprocess.PIPE,
    )
    envs_unset = command_output.stdout.decode("utf8")

    assert envs_set != envs_unset
