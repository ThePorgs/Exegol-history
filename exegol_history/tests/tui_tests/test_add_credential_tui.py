import pytest
import subprocess
import sys
from exegol_history.cli.utils import write_credential_in_profile
from exegol_history.tui.db_creds.db_creds import DbCredsApp
from exegol_history.db_api.creds import Credential, get_credentials
from common import (
    USERNAME_TEST_VALUE,
    PASSWORD_TEST_VALUE,
    HASH_TEST_VALUE,
    DOMAIN_TEST_VALUE,
    select_input_and_enter_text,
)
from pykeepass import PyKeePass
from typing import Any
from exegol_history.tui.widgets.credential_form import (
    ID_CONFIRM_BUTTON,
    ID_DOMAIN_INPUT,
    ID_HASH_INPUT,
    ID_PASSWORD_INPUT,
    ID_USERNAME_INPUT,
)


@pytest.mark.asyncio
async def test_add_credential_only_username(
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

    credentials = get_credentials(kp)

    assert credentials == [Credential("1", USERNAME_TEST_VALUE)]


@pytest.mark.asyncio
async def test_add_credential_half(
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
        await select_input_and_enter_text(pilot, f"#{ID_HASH_INPUT}", HASH_TEST_VALUE)
        await pilot.click(f"#{ID_CONFIRM_BUTTON}")

    credentials = get_credentials(kp)

    assert credentials == [Credential("1", USERNAME_TEST_VALUE, hash=HASH_TEST_VALUE)]


@pytest.mark.asyncio
async def test_add_credential_full(
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

    credentials = get_credentials(kp)

    assert credentials == [
        Credential(
            "1",
            USERNAME_TEST_VALUE,
            PASSWORD_TEST_VALUE,
            HASH_TEST_VALUE,
            DOMAIN_TEST_VALUE,
        )
    ]


@pytest.mark.skipif(sys.platform.startswith("win"), reason="require Linux")
@pytest.mark.asyncio
async def test_add_and_set_credential_full(
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

    credential = Credential(
        "1",
        USERNAME_TEST_VALUE,
        PASSWORD_TEST_VALUE,
        HASH_TEST_VALUE,
        DOMAIN_TEST_VALUE,
    )

    assert get_credentials(kp) == [credential]

    write_credential_in_profile(credential, load_mock_config)
    command_output = subprocess.run(
        [
            "bash",
            "-c",
            f"source {load_mock_config['paths']['profile_sh_path']} && echo $PASSWORD $USER $NT_HASH $DOMAIN",
        ],
        stdout=subprocess.PIPE,
    )
    envs = command_output.stdout.decode("utf8")

    assert PASSWORD_TEST_VALUE in envs
    assert USERNAME_TEST_VALUE in envs
    assert HASH_TEST_VALUE in envs
    assert DOMAIN_TEST_VALUE in envs


@pytest.mark.asyncio
async def test_add_credential_empty(
    open_keepass: PyKeePass, load_mock_config: dict[str, Any]
):
    kp = open_keepass
    app = DbCredsApp(load_mock_config, kp)
    add_credential_keybind = load_mock_config["keybindings"]["add_credential"]

    async with app.run_test() as pilot:
        await pilot.press(add_credential_keybind)
        await pilot.click(f"#{ID_CONFIRM_BUTTON}")

    assert get_credentials(kp) == [Credential("1")]


@pytest.mark.asyncio
async def test_add_credential_existing(
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
            pilot, f"#{ID_DOMAIN_INPUT}", DOMAIN_TEST_VALUE
        )
        await pilot.click(f"#{ID_CONFIRM_BUTTON}")

        assert get_credentials(kp) == [
            Credential(id="1", username=USERNAME_TEST_VALUE, domain=DOMAIN_TEST_VALUE)
        ]

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

        assert get_credentials(kp) == [
            Credential(
                id="1",
                username=USERNAME_TEST_VALUE,
                domain=DOMAIN_TEST_VALUE,
            ),
            Credential(
                id="2",
                username=USERNAME_TEST_VALUE,
                password=PASSWORD_TEST_VALUE,
                hash=HASH_TEST_VALUE,
                domain=DOMAIN_TEST_VALUE,
            ),
        ]


@pytest.mark.asyncio
async def test_add_credential_issue_3(  # https://github.com/ThePorgs/Exegol-history/issues/3
    open_keepass: PyKeePass, load_mock_config: dict[str, Any]
):
    kp = open_keepass
    app = DbCredsApp(load_mock_config, kp)
    add_credential_keybind = load_mock_config["keybindings"]["add_credential"]

    async with app.run_test() as pilot:
        await pilot.press(add_credential_keybind)
        await pilot.press(add_credential_keybind)
        await select_input_and_enter_text(
            pilot, f"#{ID_USERNAME_INPUT}", USERNAME_TEST_VALUE
        )
        await pilot.click(f"#{ID_CONFIRM_BUTTON}")

    assert get_credentials(kp) == [Credential(id="1", username=USERNAME_TEST_VALUE)]


@pytest.mark.asyncio
async def test_add_credential_multiple_local_account(
    # This test was made in order to test the case
    # were multiple local account were given, with only the domain being different
    open_keepass: PyKeePass,
    load_mock_config: dict[str, Any],
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
        await select_input_and_enter_text(
            pilot, f"#{ID_DOMAIN_INPUT}", DOMAIN_TEST_VALUE
        )
        await pilot.click(f"#{ID_CONFIRM_BUTTON}")

        assert get_credentials(kp) == [
            Credential(
                id="1",
                username=USERNAME_TEST_VALUE,
                password=PASSWORD_TEST_VALUE,
                domain=DOMAIN_TEST_VALUE,
            )
        ]

        await pilot.press(add_credential_keybind)
        await select_input_and_enter_text(
            pilot, f"#{ID_USERNAME_INPUT}", USERNAME_TEST_VALUE
        )
        await select_input_and_enter_text(
            pilot, f"#{ID_PASSWORD_INPUT}", PASSWORD_TEST_VALUE
        )
        await select_input_and_enter_text(
            pilot, f"#{ID_DOMAIN_INPUT}", DOMAIN_TEST_VALUE + "2"
        )
        await pilot.click(f"#{ID_CONFIRM_BUTTON}")

        assert get_credentials(kp) == [
            Credential(
                id="1",
                username=USERNAME_TEST_VALUE,
                password=PASSWORD_TEST_VALUE,
                domain=DOMAIN_TEST_VALUE,
            ),
            Credential(
                id="2",
                username=USERNAME_TEST_VALUE,
                password=PASSWORD_TEST_VALUE,
                domain=DOMAIN_TEST_VALUE + "2",
            ),
        ]
