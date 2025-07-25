from textual.keys import Keys
from pykeepass import PyKeePass
from typing import Any
import pytest
import subprocess
import sys
from exegol_history.cli.utils import (
    HOSTS_VARIABLES,
    write_host_in_profile,
)
from common import (
    HOSTNAME_TEST_VALUE,
    IP_TEST_VALUE,
    ROLE_TEST_VALUE,
    select_input_and_enter_text,
)
from exegol_history.db_api.hosts import Host
from exegol_history.tui.db_hosts import DbHostsApp
from exegol_history.tui.widgets.credential_form import (
    ID_CONFIRM_BUTTON,
)
from exegol_history.tui.widgets.host_form import (
    ID_HOSTNAME_INPUT,
    ID_IP_INPUT,
    ID_ROLE_INPUT,
)


@pytest.mark.asyncio
async def test_set_host_without_selecting(
    open_keepass: PyKeePass, load_mock_config: dict[str, Any]
):
    kp = open_keepass
    app = DbHostsApp(load_mock_config, kp)

    async with app.run_test() as pilot:
        with pytest.raises(TypeError):
            host = await pilot.exit(0)
            write_host_in_profile(Host(*host), load_mock_config)


@pytest.mark.skipif(sys.platform.startswith("win"), reason="require Linux")
@pytest.mark.asyncio
async def test_set_host_only_ip_linux(
    open_keepass: PyKeePass, load_mock_config: dict[str, Any]
):
    kp = open_keepass
    app = DbHostsApp(load_mock_config, kp)
    add_host_keybind = load_mock_config["keybindings"]["add_host"]

    async with app.run_test() as pilot:
        await pilot.press(add_host_keybind)
        await select_input_and_enter_text(pilot, f"#{ID_IP_INPUT}", IP_TEST_VALUE)
        await pilot.click(f"#{ID_CONFIRM_BUTTON}")
        await pilot.press(Keys.Enter)

        write_host_in_profile(Host(*pilot.app.return_value), load_mock_config)

    command_output = subprocess.run(
        [
            "bash",
            "-c",
            f"source {load_mock_config['paths']['profile_sh_path']} && echo ${HOSTS_VARIABLES[0]} ${HOSTS_VARIABLES[1]}",
        ],
        stdout=subprocess.PIPE,
    )
    envs = command_output.stdout.decode("utf8")

    assert IP_TEST_VALUE in envs

    command_output = subprocess.run(
        [
            "bash",
            "-c",
            f"source {load_mock_config['paths']['profile_sh_path']} && echo ${HOSTS_VARIABLES[2]} ${HOSTS_VARIABLES[3]} ${HOSTS_VARIABLES[4]} ${HOSTS_VARIABLES[5]}",
        ],
        stdout=subprocess.PIPE,
    )
    envs = command_output.stdout.decode("utf8")

    assert envs.strip() == ""


@pytest.mark.skipif(sys.platform.startswith("win"), reason="require Linux")
@pytest.mark.asyncio
async def test_set_host_half_linux(
    open_keepass: PyKeePass, load_mock_config: dict[str, Any]
):
    kp = open_keepass
    app = DbHostsApp(load_mock_config, kp)
    add_host_keybind = load_mock_config["keybindings"]["add_host"]

    async with app.run_test() as pilot:
        await pilot.press(add_host_keybind)
        await select_input_and_enter_text(pilot, f"#{ID_IP_INPUT}", IP_TEST_VALUE)
        await select_input_and_enter_text(
            pilot, f"#{ID_HOSTNAME_INPUT}", HOSTNAME_TEST_VALUE
        )
        await pilot.click(f"#{ID_CONFIRM_BUTTON}")
        await pilot.press(Keys.Enter)

        write_host_in_profile(Host(*pilot.app.return_value), load_mock_config)

    command_output = subprocess.run(
        [
            "bash",
            "-c",
            f"source {load_mock_config['paths']['profile_sh_path']} && echo ${HOSTS_VARIABLES[0]} ${HOSTS_VARIABLES[1]} ${HOSTS_VARIABLES[2]}",
        ],
        stdout=subprocess.PIPE,
    )
    envs = command_output.stdout.decode("utf8")

    assert IP_TEST_VALUE in envs
    assert HOSTNAME_TEST_VALUE in envs

    command_output = subprocess.run(
        [
            "bash",
            "-c",
            f"source {load_mock_config['paths']['profile_sh_path']} && echo ${HOSTS_VARIABLES[3]} ${HOSTS_VARIABLES[4]} ${HOSTS_VARIABLES[5]}",
        ],
        stdout=subprocess.PIPE,
    )
    envs = command_output.stdout.decode("utf8")

    assert envs.strip() == ""


@pytest.mark.skipif(sys.platform.startswith("win"), reason="require Linux")
@pytest.mark.asyncio
async def test_set_host_full_linux(
    open_keepass: PyKeePass, load_mock_config: dict[str, Any]
):
    kp = open_keepass
    app = DbHostsApp(load_mock_config, kp)
    add_host_keybind = load_mock_config["keybindings"]["add_host"]

    async with app.run_test() as pilot:
        await pilot.press(add_host_keybind)
        await select_input_and_enter_text(pilot, f"#{ID_IP_INPUT}", IP_TEST_VALUE)
        await select_input_and_enter_text(
            pilot, f"#{ID_HOSTNAME_INPUT}", HOSTNAME_TEST_VALUE
        )
        await select_input_and_enter_text(pilot, f"#{ID_ROLE_INPUT}", ROLE_TEST_VALUE)
        await pilot.click(f"#{ID_CONFIRM_BUTTON}")
        await pilot.press(Keys.Enter)

        write_host_in_profile(Host(*pilot.app.return_value), load_mock_config)

    command_output = subprocess.run(
        [
            "bash",
            "-c",
            f"source {load_mock_config['paths']['profile_sh_path']} && echo ${HOSTS_VARIABLES[0]} ${HOSTS_VARIABLES[1]} ${HOSTS_VARIABLES[2]} ${HOSTS_VARIABLES[5]}",
        ],
        stdout=subprocess.PIPE,
    )
    envs = command_output.stdout.decode("utf8")

    assert IP_TEST_VALUE in envs
    assert HOSTNAME_TEST_VALUE in envs
    assert ROLE_TEST_VALUE in envs

    command_output = subprocess.run(
        [
            "bash",
            "-c",
            f"source {load_mock_config['paths']['profile_sh_path']} && echo ${HOSTS_VARIABLES[3]} ${HOSTS_VARIABLES[4]}",
        ],
        stdout=subprocess.PIPE,
    )
    envs = command_output.stdout.decode("utf8")

    assert IP_TEST_VALUE in envs
    assert HOSTNAME_TEST_VALUE in envs


# Test the special case of a DC host, if we select an host that is not a DC,
# the DC_HOST and DC_IP variable shouldn't change
@pytest.mark.skipif(sys.platform.startswith("win"), reason="require Linux")
@pytest.mark.asyncio
async def test_set_host_dc_linux(
    open_keepass: PyKeePass, load_mock_config: dict[str, Any]
):
    kp = open_keepass
    app = DbHostsApp(load_mock_config, kp)
    add_host_keybind = load_mock_config["keybindings"]["add_host"]

    async with app.run_test() as pilot:
        await pilot.press(add_host_keybind)
        await select_input_and_enter_text(pilot, f"#{ID_IP_INPUT}", IP_TEST_VALUE)
        await select_input_and_enter_text(
            pilot, f"#{ID_HOSTNAME_INPUT}", HOSTNAME_TEST_VALUE
        )
        await select_input_and_enter_text(pilot, f"#{ID_ROLE_INPUT}", ROLE_TEST_VALUE)
        await pilot.click(f"#{ID_CONFIRM_BUTTON}")
        await pilot.press(Keys.Enter)

        write_host_in_profile(Host(*pilot.app.return_value), load_mock_config)

    command_output = subprocess.run(
        [
            "bash",
            "-c",
            f"source {load_mock_config['paths']['profile_sh_path']} && echo ${HOSTS_VARIABLES[0]} ${HOSTS_VARIABLES[1]} ${HOSTS_VARIABLES[2]} ${HOSTS_VARIABLES[3]} ${HOSTS_VARIABLES[4]}",
        ],
        stdout=subprocess.PIPE,
    )
    envs = command_output.stdout.decode("utf8")

    assert IP_TEST_VALUE in envs
    assert HOSTNAME_TEST_VALUE in envs

    app = DbHostsApp(
        load_mock_config, kp
    )  # Initialize a new app so we can use the Textualize pilot again

    async with app.run_test() as pilot:
        await pilot.press(add_host_keybind)
        await select_input_and_enter_text(pilot, f"#{ID_IP_INPUT}", "192.168.0.22")
        await select_input_and_enter_text(pilot, f"#{ID_HOSTNAME_INPUT}", "MSSQL01")
        await select_input_and_enter_text(pilot, f"#{ID_ROLE_INPUT}", "MSSQL")
        await pilot.click(f"#{ID_CONFIRM_BUTTON}")
        await pilot.press(Keys.Down)
        await pilot.press(Keys.Enter)

        write_host_in_profile(Host(*pilot.app.return_value), load_mock_config)

    command_output = subprocess.run(
        [
            "bash",
            "-c",
            f"source {load_mock_config['paths']['profile_sh_path']} && echo ${HOSTS_VARIABLES[0]} ${HOSTS_VARIABLES[1]} ${HOSTS_VARIABLES[2]} ${HOSTS_VARIABLES[3]} ${HOSTS_VARIABLES[4]}",
        ],
        stdout=subprocess.PIPE,
    )
    envs = command_output.stdout.decode("utf8")

    assert "192.168.0.22" in envs
    assert "MSSQL01" in envs
    assert IP_TEST_VALUE in envs
    assert HOSTNAME_TEST_VALUE in envs


@pytest.mark.skipif(sys.platform != "Windows", reason="require Windows")
@pytest.mark.asyncio
async def test_set_host_only_ip_windows(
    open_keepass: PyKeePass, load_mock_config: dict[str, Any]
):
    kp = open_keepass
    app = DbHostsApp(load_mock_config, kp)
    add_host_keybind = load_mock_config["keybindings"]["add_host"]

    async with app.run_test() as pilot:
        await pilot.press(add_host_keybind)
        await select_input_and_enter_text(pilot, f"#{ID_IP_INPUT}", IP_TEST_VALUE)
        await pilot.click(f"#{ID_CONFIRM_BUTTON}")
        await pilot.press(Keys.Enter)

        write_host_in_profile(Host(*pilot.app.return_value), load_mock_config)

    command_output = subprocess.run(
        [
            "powershell",
            "-Command",
            f". {load_mock_config['paths']['profile_sh_path']}; if ($?) {{ echo ${HOSTS_VARIABLES[0]} ${HOSTS_VARIABLES[1]} }}",
        ],
        stdout=subprocess.PIPE,
    )
    envs = command_output.stdout.decode("utf8")

    assert IP_TEST_VALUE in envs

    command_output = subprocess.run(
        [
            "powershell",
            "-Command",
            f". {load_mock_config['paths']['profile_sh_path']}; if ($?) {{ echo ${HOSTS_VARIABLES[2]} }}",
        ],
        stdout=subprocess.PIPE,
    )
    envs = command_output.stdout.decode("utf8")

    assert envs.strip() == ""


@pytest.mark.skipif(sys.platform != "Windows", reason="require Windows")
@pytest.mark.asyncio
async def test_set_host_half_windows(
    open_keepass: PyKeePass, load_mock_config: dict[str, Any]
):
    kp = open_keepass
    app = DbHostsApp(load_mock_config, kp)
    add_host_keybind = load_mock_config["keybindings"]["add_host"]

    async with app.run_test() as pilot:
        await pilot.press(add_host_keybind)
        await select_input_and_enter_text(pilot, f"#{ID_IP_INPUT}", IP_TEST_VALUE)
        await select_input_and_enter_text(
            pilot, f"#{ID_HOSTNAME_INPUT}", HOSTNAME_TEST_VALUE
        )
        await pilot.click(f"#{ID_CONFIRM_BUTTON}")
        await pilot.press(Keys.Enter)

        write_host_in_profile(Host(*pilot.app.return_value), load_mock_config)

    command_output = subprocess.run(
        [
            "powershell",
            "-Command",
            f". {load_mock_config['paths']['profile_sh_path']}; if ($?) {{ echo ${HOSTS_VARIABLES[0]} ${HOSTS_VARIABLES[1]} ${HOSTS_VARIABLES[2]} }}",
        ],
        stdout=subprocess.PIPE,
    )
    envs = command_output.stdout.decode("utf8")

    assert IP_TEST_VALUE in envs
    assert HOSTNAME_TEST_VALUE in envs

    command_output = subprocess.run(
        [
            "powershell",
            "-Command",
            f". {load_mock_config['paths']['profile_sh_path']}; if ($?) {{ echo ${HOSTS_VARIABLES[3]} ${HOSTS_VARIABLES[4]} ${HOSTS_VARIABLES[5]} }}",
        ],
        stdout=subprocess.PIPE,
    )
    envs = command_output.stdout.decode("utf8")

    assert envs.strip() == ""


@pytest.mark.skipif(sys.platform != "Windows", reason="require Windows")
@pytest.mark.asyncio
async def test_set_host_full_windows(
    open_keepass: PyKeePass, load_mock_config: dict[str, Any]
):
    kp = open_keepass
    app = DbHostsApp(load_mock_config, kp)
    add_host_keybind = load_mock_config["keybindings"]["add_host"]

    async with app.run_test() as pilot:
        await pilot.press(add_host_keybind)
        await select_input_and_enter_text(pilot, f"#{ID_IP_INPUT}", IP_TEST_VALUE)
        await select_input_and_enter_text(
            pilot, f"#{ID_HOSTNAME_INPUT}", HOSTNAME_TEST_VALUE
        )
        await select_input_and_enter_text(pilot, f"#{ID_ROLE_INPUT}", ROLE_TEST_VALUE)
        await pilot.click(f"#{ID_CONFIRM_BUTTON}")
        await pilot.press(Keys.Enter)

        write_host_in_profile(Host(*pilot.app.return_value), load_mock_config)

    command_output = subprocess.run(
        [
            "powershell",
            "-Command",
            f". {load_mock_config['paths']['profile_sh_path']}; if ($?) {{ echo ${HOSTS_VARIABLES[0]} ${HOSTS_VARIABLES[1]} ${HOSTS_VARIABLES[2]} ${HOSTS_VARIABLES[5]} }}",
        ],
        stdout=subprocess.PIPE,
    )
    envs = command_output.stdout.decode("utf8")

    assert IP_TEST_VALUE in envs
    assert HOSTNAME_TEST_VALUE in envs
    assert ROLE_TEST_VALUE in envs

    command_output = subprocess.run(
        [
            "powershell",
            "-Command",
            f". {load_mock_config['paths']['profile_sh_path']}; if ($?) {{ echo ${HOSTS_VARIABLES[3]} ${HOSTS_VARIABLES[4]} }}",
        ],
        stdout=subprocess.PIPE,
    )
    envs = command_output.stdout.decode("utf8")

    assert IP_TEST_VALUE in envs
    assert HOSTNAME_TEST_VALUE in envs


# Test the special case of a DC host, if we select an host that is not a DC,
# the DC_HOST and DC_IP variable shouldn't change
@pytest.mark.skipif(sys.platform != "Windows", reason="require Windows")
@pytest.mark.asyncio
async def test_set_host_dc_windows(
    open_keepass: PyKeePass, load_mock_config: dict[str, Any]
):
    kp = open_keepass
    app = DbHostsApp(load_mock_config, kp)
    add_host_keybind = load_mock_config["keybindings"]["add_host"]

    async with app.run_test() as pilot:
        await pilot.press(add_host_keybind)
        await select_input_and_enter_text(pilot, f"#{ID_IP_INPUT}", IP_TEST_VALUE)
        await select_input_and_enter_text(
            pilot, f"#{ID_HOSTNAME_INPUT}", HOSTNAME_TEST_VALUE
        )
        await select_input_and_enter_text(pilot, f"#{ID_ROLE_INPUT}", ROLE_TEST_VALUE)
        await pilot.click(f"#{ID_CONFIRM_BUTTON}")
        await pilot.press(Keys.Enter)

        write_host_in_profile(Host(*pilot.app.return_value), load_mock_config)

    command_output = subprocess.run(
        [
            "powershell",
            "-Command",
            f". {load_mock_config['paths']['profile_sh_path']}; if ($?) {{ echo ${HOSTS_VARIABLES[0]} ${HOSTS_VARIABLES[1]} ${HOSTS_VARIABLES[2]} ${HOSTS_VARIABLES[3]} ${HOSTS_VARIABLES[4]} }}",
        ],
        stdout=subprocess.PIPE,
    )
    envs = command_output.stdout.decode("utf8")

    assert IP_TEST_VALUE in envs
    assert HOSTNAME_TEST_VALUE in envs

    app = DbHostsApp(
        load_mock_config, kp
    )  # Initialize a new app so we can use the Textualize pilot again

    async with app.run_test() as pilot:
        await pilot.press(add_host_keybind)
        await select_input_and_enter_text(pilot, f"#{ID_IP_INPUT}", "192.168.0.22")
        await select_input_and_enter_text(pilot, f"#{ID_HOSTNAME_INPUT}", "MSSQL01")
        await select_input_and_enter_text(pilot, f"#{ID_ROLE_INPUT}", "MSSQL")
        await pilot.click(f"#{ID_CONFIRM_BUTTON}")
        await pilot.press(Keys.Down)
        await pilot.press(Keys.Enter)

        write_host_in_profile(Host(*pilot.app.return_value), load_mock_config)

    command_output = subprocess.run(
        [
            "powershell",
            "-Command",
            f". {load_mock_config['paths']['profile_sh_path']}; if ($?) {{ echo ${HOSTS_VARIABLES[0]} ${HOSTS_VARIABLES[1]} ${HOSTS_VARIABLES[2]} ${HOSTS_VARIABLES[3]} ${HOSTS_VARIABLES[4]} }}",
        ],
        stdout=subprocess.PIPE,
    )
    envs = command_output.stdout.decode("utf8")

    assert "192.168.0.22" in envs
    assert "MSSQL01" in envs
    assert IP_TEST_VALUE in envs
    assert HOSTNAME_TEST_VALUE in envs
