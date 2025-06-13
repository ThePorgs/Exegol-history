import pytest
from exegol_history.tui.db_creds.db_creds import DbCredsApp
from exegol_history.db_api.creds import Credential, get_credentials
from common import (
    USERNAME_TEST_VALUE,
    PASSWORD_TEST_VALUE,
    HASH_TEST_VALUE,
    DOMAIN_TEST_VALUE,
    select_input_and_enter_text,
    select_input_erase_and_enter_text,
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
async def test_edit_credential_only_username(
    open_keepass: PyKeePass, load_mock_config: dict[str, Any]
):
    kp = open_keepass
    app = DbCredsApp(load_mock_config, kp)
    add_credential_keybind = load_mock_config["keybindings"]["add_credential"]
    edit_credential_keybind = load_mock_config["keybindings"]["edit_credential"]

    async with app.run_test() as pilot:
        await pilot.press(add_credential_keybind)
        await select_input_and_enter_text(
            pilot, f"#{ID_USERNAME_INPUT}", USERNAME_TEST_VALUE
        )
        await pilot.click(f"#{ID_CONFIRM_BUTTON}")

        assert get_credentials(kp) == [Credential(id="1", username=USERNAME_TEST_VALUE)]

        await pilot.press(edit_credential_keybind)
        await select_input_erase_and_enter_text(
            pilot, f"#{ID_USERNAME_INPUT}", USERNAME_TEST_VALUE + "2"
        )
        await pilot.click(f"#{ID_CONFIRM_BUTTON}")

        assert get_credentials(kp) == [
            Credential(id="1", username=USERNAME_TEST_VALUE + "2")
        ]


@pytest.mark.asyncio
async def test_edit_credential_full(
    open_keepass: PyKeePass, load_mock_config: dict[str, Any]
):
    kp = open_keepass
    app = DbCredsApp(load_mock_config, kp)
    add_credential_keybind = load_mock_config["keybindings"]["add_credential"]
    edit_credential_keybind = load_mock_config["keybindings"]["edit_credential"]

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

        assert get_credentials(kp) == [
            Credential(
                id="1",
                username=USERNAME_TEST_VALUE,
                password=PASSWORD_TEST_VALUE,
                hash=HASH_TEST_VALUE,
                domain=DOMAIN_TEST_VALUE,
            )
        ]

        await pilot.press(edit_credential_keybind)
        await select_input_erase_and_enter_text(
            pilot, f"#{ID_USERNAME_INPUT}", USERNAME_TEST_VALUE + "2"
        )
        await select_input_erase_and_enter_text(
            pilot, f"#{ID_PASSWORD_INPUT}", PASSWORD_TEST_VALUE + "2"
        )
        await select_input_erase_and_enter_text(
            pilot, f"#{ID_HASH_INPUT}", HASH_TEST_VALUE + "2"
        )
        await select_input_erase_and_enter_text(
            pilot, f"#{ID_DOMAIN_INPUT}", DOMAIN_TEST_VALUE + "2"
        )
        await pilot.click(f"#{ID_CONFIRM_BUTTON}")

        assert get_credentials(kp) == [
            Credential(
                id="1",
                username=USERNAME_TEST_VALUE + "2",
                password=PASSWORD_TEST_VALUE + "2",
                hash=HASH_TEST_VALUE + "2",
                domain=DOMAIN_TEST_VALUE + "2",
            )
        ]


@pytest.mark.asyncio
async def test_edit_credential_not_exist(
    open_keepass: PyKeePass, load_mock_config: dict[str, Any]
):
    kp = open_keepass
    app = DbCredsApp(load_mock_config, kp)
    edit_credential_keybind = load_mock_config["keybindings"]["edit_credential"]

    async with app.run_test() as pilot:
        await pilot.press(edit_credential_keybind)

    assert len(get_credentials(kp)) == 0


@pytest.mark.asyncio
async def test_edit_credential_issue_3(
    open_keepass: PyKeePass, load_mock_config: dict[str, Any]
):
    kp = open_keepass
    app = DbCredsApp(load_mock_config, kp)
    add_credential_keybind = load_mock_config["keybindings"]["add_credential"]
    edit_credential_keybind = load_mock_config["keybindings"]["edit_credential"]

    async with app.run_test() as pilot:
        await pilot.press(add_credential_keybind)
        await select_input_and_enter_text(
            pilot, f"#{ID_USERNAME_INPUT}", USERNAME_TEST_VALUE
        )
        await pilot.click(f"#{ID_CONFIRM_BUTTON}")

        assert get_credentials(kp) == [Credential(id="1", username=USERNAME_TEST_VALUE)]

        await pilot.press(edit_credential_keybind)
        await pilot.press(edit_credential_keybind)
        await select_input_erase_and_enter_text(
            pilot, f"#{ID_USERNAME_INPUT}", USERNAME_TEST_VALUE + "2"
        )
        await pilot.click(f"#{ID_CONFIRM_BUTTON}")

        assert get_credentials(kp) == [
            Credential(id="1", username=USERNAME_TEST_VALUE + "2")
        ]
