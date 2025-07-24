import pytest
from exegol_history.tui.db_creds import DbCredsApp
from exegol_history.db_api.creds import (
    Credential,
    add_credential,
    add_credentials,
    get_credentials,
)
from common import (
    CREDENTIALS_TEST_VALUE_GOAD_SECRETSDUMP,
    USERNAME_TEST_VALUE,
    PASSWORD_TEST_VALUE,
    HASH_TEST_VALUE,
    DOMAIN_TEST_VALUE,
    select_input_and_enter_text,
)
from pykeepass import PyKeePass
from exegol_history.tui.widgets.credential_form import (
    ID_CONFIRM_BUTTON,
    ID_DOMAIN_INPUT,
    ID_HASH_INPUT,
    ID_PASSWORD_INPUT,
    ID_USERNAME_INPUT,
)
from textual.keys import Keys
from exegol_history.tui.screens.delete_object import (
    ID_CONFIRM_RANGE_BUTTON,
    ID_IDS_INPUT,
)


@pytest.mark.asyncio
async def test_delete_credential(open_keepass: PyKeePass, load_mock_config):
    kp = open_keepass
    app = DbCredsApp(load_mock_config, kp)
    add_credential_keybind = load_mock_config["keybindings"]["add_credential"]
    delete_credential_keybind = load_mock_config["keybindings"]["delete_credential"]

    async with app.run_test() as pilot:
        await pilot.press(add_credential_keybind)
        await select_input_and_enter_text(
            pilot, f"#{ID_USERNAME_INPUT}", USERNAME_TEST_VALUE
        )
        await pilot.click(f"#{ID_CONFIRM_BUTTON}")

        assert get_credentials(kp) == [Credential(id="1", username=USERNAME_TEST_VALUE)]

        await pilot.press(delete_credential_keybind)
        await pilot.click(f"#{ID_CONFIRM_BUTTON}")

        assert len(get_credentials(kp)) == 0


@pytest.mark.asyncio
async def test_delete_credential_full(open_keepass: PyKeePass, load_mock_config):
    kp = open_keepass
    app = DbCredsApp(load_mock_config, kp)
    add_credential_keybind = load_mock_config["keybindings"]["add_credential"]
    delete_credential_keybind = load_mock_config["keybindings"]["delete_credential"]

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

        await pilot.press(delete_credential_keybind)
        await pilot.click(f"#{ID_CONFIRM_BUTTON}")

        assert len(get_credentials(kp)) == 0


@pytest.mark.asyncio
async def test_delete_credential_range(open_keepass: PyKeePass, load_mock_config):
    kp = open_keepass
    app = DbCredsApp(load_mock_config, kp)
    delete_credential_keybind = load_mock_config["keybindings"]["delete_credential"]

    add_credentials(kp, CREDENTIALS_TEST_VALUE_GOAD_SECRETSDUMP)
    assert get_credentials(kp) == CREDENTIALS_TEST_VALUE_GOAD_SECRETSDUMP

    async with app.run_test() as pilot:
        await pilot.press(delete_credential_keybind)
        await pilot.press(Keys.Right)
        await select_input_and_enter_text(
            pilot,
            f"#{ID_IDS_INPUT}",
            "5-9,1,17",
        )
        await pilot.click(f"#{ID_CONFIRM_RANGE_BUTTON}")

        assert (
            get_credentials(kp)
            == CREDENTIALS_TEST_VALUE_GOAD_SECRETSDUMP[1:4]
            + CREDENTIALS_TEST_VALUE_GOAD_SECRETSDUMP[9:16]
            + CREDENTIALS_TEST_VALUE_GOAD_SECRETSDUMP[17:]
        )


@pytest.mark.asyncio
async def test_delete_credential_range_with_invalid_id(
    open_keepass: PyKeePass, load_mock_config
):
    kp = open_keepass
    app = DbCredsApp(load_mock_config, kp)
    delete_credential_keybind = load_mock_config["keybindings"]["delete_credential"]

    add_credentials(kp, CREDENTIALS_TEST_VALUE_GOAD_SECRETSDUMP)
    assert get_credentials(kp) == CREDENTIALS_TEST_VALUE_GOAD_SECRETSDUMP

    async with app.run_test() as pilot:
        await pilot.press(delete_credential_keybind)
        await pilot.press(Keys.Right)
        await select_input_and_enter_text(
            pilot,
            f"#{ID_IDS_INPUT}",
            "5-9,1,999,17",
        )
        await pilot.click(f"#{ID_CONFIRM_RANGE_BUTTON}")

        assert (
            get_credentials(kp)
            == CREDENTIALS_TEST_VALUE_GOAD_SECRETSDUMP[1:4]
            + CREDENTIALS_TEST_VALUE_GOAD_SECRETSDUMP[9:16]
            + CREDENTIALS_TEST_VALUE_GOAD_SECRETSDUMP[17:]
        )


# Trying to delete an object when no object are present should not raise an exception
@pytest.mark.asyncio
async def test_delete_credential_empty(open_keepass: PyKeePass, load_mock_config):
    kp = open_keepass
    app = DbCredsApp(load_mock_config, kp)
    delete_credential_keybind = load_mock_config["keybindings"]["delete_credential"]

    async with app.run_test() as pilot:
        await pilot.press(delete_credential_keybind)


@pytest.mark.asyncio
async def test_delete_credential_issue_3(open_keepass: PyKeePass, load_mock_config):
    kp = open_keepass
    app = DbCredsApp(load_mock_config, kp)
    delete_credential_keybind = load_mock_config["keybindings"]["delete_credential"]

    add_credential(kp, Credential())

    async with app.run_test() as pilot:
        await pilot.press(delete_credential_keybind)
        await pilot.press(delete_credential_keybind)
        await pilot.click(f"#{ID_CONFIRM_BUTTON}")
