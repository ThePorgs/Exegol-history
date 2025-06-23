from textual.keys import Keys
from pykeepass import PyKeePass
from typing import Any
import pytest
import subprocess
import sys
from exegol_history.cli.utils import CREDS_VARIABLES, write_credential_in_profile
from exegol_history.db_api.creds import Credential
from exegol_history.tui.db_creds import DbCredsApp
from common import (
    USERNAME_TEST_VALUE,
    PASSWORD_TEST_VALUE,
    HASH_TEST_VALUE,
    DOMAIN_TEST_VALUE,
    select_input_and_enter_text,
)
from exegol_history.tui.widgets.credential_form import (
    ID_CONFIRM_BUTTON,
    ID_DOMAIN_INPUT,
    ID_HASH_INPUT,
    ID_PASSWORD_INPUT,
    ID_USERNAME_INPUT,
)

@pytest.mark.asyncio
async def test_set_credential_without_selecting(
    open_keepass: PyKeePass, load_mock_config: dict[str, Any]
):
    kp = open_keepass
    app = DbCredsApp(load_mock_config, kp)

    async with app.run_test() as pilot:
        with pytest.raises(TypeError):
            credential = await pilot.exit(0)
            write_credential_in_profile(Credential(*credential), load_mock_config)


@pytest.mark.skipif(sys.platform.startswith("win"), reason="require Linux")
@pytest.mark.asyncio
async def test_set_credential_only_username_linux(
    open_keepass: PyKeePass, load_mock_config: dict[str, Any]
):
    kp = open_keepass
    app = DbCredsApp(load_mock_config, kp)
    add_credential_keybind = load_mock_config["keybindings"]["add_credential"]

    async with app.run_test() as pilot:
        await pilot.press(add_credential_keybind)
        await select_input_and_enter_text(
            pilot, f"#{ID_USERNAME_INPUT}", USERNAME_TEST_VALUE
        )
        await pilot.click(f"#{ID_CONFIRM_BUTTON}")
        await pilot.press(Keys.Enter)

        write_credential_in_profile(
            Credential(*pilot.app.return_value), load_mock_config
        )

    command_output = subprocess.run(
        [
            "bash",
            "-c",
            f"source {load_mock_config['paths']['profile_sh_path']} && echo ${CREDS_VARIABLES[0]}",
        ],
        stdout=subprocess.PIPE,
    )
    envs = command_output.stdout.decode("utf8")

    assert USERNAME_TEST_VALUE in envs

    command_output = subprocess.run(
        [
            "bash",
            "-c",
            f"source {load_mock_config['paths']['profile_sh_path']} && echo ${CREDS_VARIABLES[1]} ${CREDS_VARIABLES[2]} ${CREDS_VARIABLES[3]}",
        ],
        stdout=subprocess.PIPE,
    )
    envs = command_output.stdout.decode("utf8")

    assert envs.strip() == ""


@pytest.mark.skipif(sys.platform.startswith("win"), reason="require Linux")
@pytest.mark.asyncio
async def test_set_credential_half_linux(
    open_keepass: PyKeePass, load_mock_config: dict[str, Any]
):
    kp = open_keepass
    app = DbCredsApp(load_mock_config, kp)
    add_credential_keybind = load_mock_config["keybindings"]["add_credential"]

    async with app.run_test() as pilot:
        await pilot.press(add_credential_keybind)
        await select_input_and_enter_text(
            pilot, f"#{ID_USERNAME_INPUT}", USERNAME_TEST_VALUE
        )
        await select_input_and_enter_text(
            pilot, f"#{ID_PASSWORD_INPUT}", PASSWORD_TEST_VALUE
        )
        await pilot.click(f"#{ID_CONFIRM_BUTTON}")
        await pilot.press(Keys.Enter)

        write_credential_in_profile(
            Credential(*pilot.app.return_value), load_mock_config
        )

    command_output = subprocess.run(
        [
            "bash",
            "-c",
            f"source {load_mock_config['paths']['profile_sh_path']} && echo ${CREDS_VARIABLES[0]} ${CREDS_VARIABLES[1]}",
        ],
        stdout=subprocess.PIPE,
    )
    envs = command_output.stdout.decode("utf8")

    assert USERNAME_TEST_VALUE in envs
    assert PASSWORD_TEST_VALUE in envs

    command_output = subprocess.run(
        [
            "bash",
            "-c",
            f"source {load_mock_config['paths']['profile_sh_path']} && echo ${CREDS_VARIABLES[2]} ${CREDS_VARIABLES[3]}",
        ],
        stdout=subprocess.PIPE,
    )
    envs = command_output.stdout.decode("utf8")

    assert envs.strip() == ""


@pytest.mark.skipif(sys.platform.startswith("win"), reason="require Linux")
@pytest.mark.asyncio
async def test_set_credential_full_linux(
    open_keepass: PyKeePass, load_mock_config: dict[str, Any]
):
    kp = open_keepass
    app = DbCredsApp(load_mock_config, kp)
    add_credential_keybind = load_mock_config["keybindings"]["add_credential"]

    async with app.run_test() as pilot:
        await pilot.press(add_credential_keybind)
        await select_input_and_enter_text(
            pilot, f"#{ID_USERNAME_INPUT}", USERNAME_TEST_VALUE
        )
        await select_input_and_enter_text(
            pilot, f"#{ID_PASSWORD_INPUT}", PASSWORD_TEST_VALUE
        )
        await select_input_and_enter_text(pilot, f"#{ID_HASH_INPUT}", HASH_TEST_VALUE)
        await select_input_and_enter_text(
            pilot, f"#{ID_DOMAIN_INPUT}", DOMAIN_TEST_VALUE
        )
        await pilot.click(f"#{ID_CONFIRM_BUTTON}")
        await pilot.press(Keys.Enter)

        write_credential_in_profile(
            Credential(*pilot.app.return_value), load_mock_config
        )

    command_output = subprocess.run(
        [
            "bash",
            "-c",
            f"source {load_mock_config['paths']['profile_sh_path']} && echo ${CREDS_VARIABLES[0]} ${CREDS_VARIABLES[1]} ${CREDS_VARIABLES[2]} ${CREDS_VARIABLES[3]}",
        ],
        stdout=subprocess.PIPE,
    )
    envs = command_output.stdout.decode("utf8")

    assert USERNAME_TEST_VALUE in envs
    assert PASSWORD_TEST_VALUE in envs
    assert HASH_TEST_VALUE in envs
    assert DOMAIN_TEST_VALUE in envs


@pytest.mark.skipif(sys.platform.startswith("lin"), reason="require Windows")
@pytest.mark.asyncio
async def test_set_credential_only_username_windows(
    open_keepass: PyKeePass, load_mock_config: dict[str, Any]
):
    kp = open_keepass
    app = DbCredsApp(load_mock_config, kp)
    add_credential_keybind = load_mock_config["keybindings"]["add_credential"]

    async with app.run_test() as pilot:
        await pilot.press(add_credential_keybind)
        await select_input_and_enter_text(
            pilot, f"#{ID_USERNAME_INPUT}", USERNAME_TEST_VALUE
        )
        await pilot.click(f"#{ID_CONFIRM_BUTTON}")
        await pilot.press(Keys.Enter)

        write_credential_in_profile(
            Credential(*pilot.app.return_value), load_mock_config
        )

    command_output = subprocess.run(
        [
            "powershell",
            "-Command",
            f". {load_mock_config['paths']['profile_sh_path']}; if ($?) {{ echo ${CREDS_VARIABLES[0]} }}",
        ],
        stdout=subprocess.PIPE,
    )
    envs = command_output.stdout.decode("utf8")

    assert USERNAME_TEST_VALUE in envs

    command_output = subprocess.run(
        [
            "powershell",
            "-Command",
            f". {load_mock_config['paths']['profile_sh_path']}; if ($?) {{ echo ${CREDS_VARIABLES[1]} ${CREDS_VARIABLES[2]} ${CREDS_VARIABLES[3]} }}",
        ],
        stdout=subprocess.PIPE,
    )
    envs = command_output.stdout.decode("utf8")

    assert envs.strip() == ""


@pytest.mark.skipif(sys.platform.startswith("lin"), reason="require Windows")
@pytest.mark.asyncio
async def test_set_credential_half_windows(
    open_keepass: PyKeePass, load_mock_config: dict[str, Any]
):
    kp = open_keepass
    app = DbCredsApp(load_mock_config, kp)
    add_credential_keybind = load_mock_config["keybindings"]["add_credential"]

    async with app.run_test() as pilot:
        await pilot.press(add_credential_keybind)
        await select_input_and_enter_text(
            pilot, f"#{ID_USERNAME_INPUT}", USERNAME_TEST_VALUE
        )
        await pilot.click(f"#{ID_CONFIRM_BUTTON}")
        await pilot.press(Keys.Enter)

        write_credential_in_profile(
            Credential(*pilot.app.return_value), load_mock_config
        )

    command_output = subprocess.run(
        [
            "powershell",
            "-Command",
            f". {load_mock_config['paths']['profile_sh_path']}; if ($?) {{ echo ${CREDS_VARIABLES[0]} ${CREDS_VARIABLES[1]} }}",
        ],
        stdout=subprocess.PIPE,
    )
    envs = command_output.stdout.decode("utf8")

    assert USERNAME_TEST_VALUE in envs
    assert PASSWORD_TEST_VALUE in envs

    command_output = subprocess.run(
        [
            "powershell",
            "-Command",
            f". {load_mock_config['paths']['profile_sh_path']}; if ($?) {{ echo ${CREDS_VARIABLES[2]} ${CREDS_VARIABLES[3]} }}",
        ],
        stdout=subprocess.PIPE,
    )
    envs = command_output.stdout.decode("utf8")

    assert envs.strip() == ""


@pytest.mark.skipif(sys.platform.startswith("lin"), reason="require Windows")
@pytest.mark.asyncio
async def test_set_credential_full_windows(
    open_keepass: PyKeePass, load_mock_config: dict[str, Any]
):
    kp = open_keepass
    app = DbCredsApp(load_mock_config, kp)
    add_credential_keybind = load_mock_config["keybindings"]["add_credential"]

    async with app.run_test() as pilot:
        await pilot.press(add_credential_keybind)
        await select_input_and_enter_text(
            pilot, f"#{ID_USERNAME_INPUT}", USERNAME_TEST_VALUE
        )
        await pilot.click(f"#{ID_CONFIRM_BUTTON}")
        await pilot.press(Keys.Enter)

        write_credential_in_profile(
            Credential(*pilot.app.return_value), load_mock_config
        )

    command_output = subprocess.run(
        [
            "powershell",
            "-Command",
            f". {load_mock_config['paths']['profile_sh_path']}; if ($?) {{ echo ${CREDS_VARIABLES[0]} ${CREDS_VARIABLES[1]} ${CREDS_VARIABLES[2]} ${CREDS_VARIABLES[3]} }}",
        ],
        stdout=subprocess.PIPE,
    )
    envs = command_output.stdout.decode("utf8")

    assert USERNAME_TEST_VALUE in envs
    assert PASSWORD_TEST_VALUE in envs
    assert HASH_TEST_VALUE in envs
    assert DOMAIN_TEST_VALUE in envs
