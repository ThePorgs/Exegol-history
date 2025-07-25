import subprocess
import sys
import pytest
import types
from typing import Any
from exegol_history.cli.functions import HOSTS_SUBCOMMAND, unset_objects
from exegol_history.cli.utils import HOSTS_VARIABLES, write_host_in_profile
from exegol_history.db_api.hosts import Host
from exegol_history.tests.common import (
    HOSTNAME_TEST_VALUE,
    IP_TEST_VALUE,
    ROLE_TEST_VALUE,
)


@pytest.mark.skipif(sys.platform.startswith("win"), reason="require Linux")
def test_unset_host(load_mock_config: dict[str, Any]):
    host = Host("1", IP_TEST_VALUE, HOSTNAME_TEST_VALUE, ROLE_TEST_VALUE)

    write_host_in_profile(host, load_mock_config)
    command_output = subprocess.run(
        [
            "bash",
            "-c",
            f"source {load_mock_config['paths']['profile_sh_path']} && echo ${HOSTS_VARIABLES[0]} ${HOSTS_VARIABLES[1]} ${HOSTS_VARIABLES[2]}",
        ],
        stdout=subprocess.PIPE,
    )
    envs_set = command_output.stdout.decode("utf8")

    # Reference: https://medium.com/python-pandemonium/testing-sys-exit-with-pytest-10c6e5f7726f, https://stackoverflow.com/questions/652276/is-it-possible-to-create-anonymous-objects-in-python
    with pytest.raises(SystemExit) as exit:
        unset_objects(
            types.SimpleNamespace(subcommand=HOSTS_SUBCOMMAND), load_mock_config
        )
        assert exit.value.code == 0

    command_output = subprocess.run(
        [
            "bash",
            "-c",
            f"source {load_mock_config['paths']['profile_sh_path']} && echo ${HOSTS_VARIABLES[0]} ${HOSTS_VARIABLES[1]} ${HOSTS_VARIABLES[2]}",
        ],
        stdout=subprocess.PIPE,
    )
    envs_unset = command_output.stdout.decode("utf8")

    assert envs_set != envs_unset
