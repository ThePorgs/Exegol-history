from textual.keys import Keys
import pytest
from exegol_history.db_api.importing import CredsImportFileType
from exegol_history.tui.db_creds import DbCredsApp
from exegol_history.db_api.creds import Credential, get_credentials
from common import (
    CREDENTIALS_TEST_VALUE,
    CREDENTIALS_TEST_VALUE,
    CREDENTIALS_TEST_VALUE_GOAD_PYPYKATZ,
    CREDENTIALS_TEST_VALUE_KDBX,
    TEST_CREDS_CSV_COMMA,
    TEST_CREDS_JSON,
    TEST_CREDS_KDBX,
    TEST_CREDS_KDBX_KEYFILE,
    TEST_CREDS_PYPYKATZ_JSON,
    USERNAME_TEST_VALUE,
    PASSWORD_TEST_VALUE,
    HASH_TEST_VALUE,
    DOMAIN_TEST_VALUE,
    select_input_and_enter_text,
    select_select_index,
)
from pykeepass import PyKeePass
from typing import Any
from exegol_history.tui.widgets.credential_form import ID_CONFIRM_BUTTON
from exegol_history.tui.widgets.import_file import (
    ID_CONFIRM_IMPORT_BUTTON,
    ID_FILE_TEXTAREA,
    ID_FILE_TYPE_SELECT,
    ID_IMPORT_BUTTON,
    ID_KDBX_KEYFILE_BUTTON,
    ID_KDBX_PASSWORD_INPUT,
)
from exegol_history.tui.screens.open_file import ID_PATH_INPUT


@pytest.mark.asyncio
async def test_import_credential_csv_textarea(
    open_keepass: PyKeePass, load_mock_config: dict[str, Any]
):
    kp = open_keepass
    app = DbCredsApp(load_mock_config, kp)
    add_credential_keybind = load_mock_config["keybindings"]["add_credential"]

    async with app.run_test(size=(400, 400)) as pilot:
        await pilot.press(add_credential_keybind)

        # Switch tab
        await pilot.press(Keys.Right)

        await select_input_and_enter_text(
            pilot,
            f"#{ID_FILE_TEXTAREA}",
            f"username,password,hash,domain\n{USERNAME_TEST_VALUE},{PASSWORD_TEST_VALUE},{HASH_TEST_VALUE},{DOMAIN_TEST_VALUE}",
        )

        await select_select_index(
            pilot, f"#{ID_FILE_TYPE_SELECT}", CredsImportFileType.CSV.value
        )

        await pilot.click(f"#{ID_CONFIRM_IMPORT_BUTTON}")

    assert get_credentials(kp) == [
        Credential(
            "1",
            USERNAME_TEST_VALUE,
            PASSWORD_TEST_VALUE,
            HASH_TEST_VALUE,
            DOMAIN_TEST_VALUE,
        )
    ]


@pytest.mark.asyncio
async def test_import_credential_import_csv_file(
    open_keepass: PyKeePass, load_mock_config: dict[str, Any]
):
    kp = open_keepass
    app = DbCredsApp(load_mock_config, kp)
    add_credential_keybind = load_mock_config["keybindings"]["add_credential"]

    async with app.run_test(size=(400, 400)) as pilot:
        # Comma
        await pilot.press(add_credential_keybind)

        # Switch tab
        await pilot.press(Keys.Right)

        await pilot.click(f"#{ID_IMPORT_BUTTON}")
        pilot.app.screen.query_one(f"#{ID_PATH_INPUT}").value = str(
            TEST_CREDS_CSV_COMMA
        )
        await pilot.pause()
        await pilot.click(f"#{ID_CONFIRM_BUTTON}")

        await select_select_index(
            pilot, f"#{ID_FILE_TYPE_SELECT}", CredsImportFileType.CSV.value
        )

        await pilot.click(f"#{ID_CONFIRM_IMPORT_BUTTON}")

        assert get_credentials(kp) == CREDENTIALS_TEST_VALUE


@pytest.mark.asyncio
async def test_import_credential_json_textarea(
    open_keepass: PyKeePass, load_mock_config: dict[str, Any]
):
    kp = open_keepass
    app = DbCredsApp(load_mock_config, kp)
    add_credential_keybind = load_mock_config["keybindings"]["add_credential"]

    async with app.run_test(size=(400, 400)) as pilot:
        await pilot.press(add_credential_keybind)

        # Switch tab
        await pilot.press(Keys.Right)

        await select_input_and_enter_text(
            pilot,
            f"#{ID_FILE_TEXTAREA}",
            f'[{{ "username":"{USERNAME_TEST_VALUE}","password":"{PASSWORD_TEST_VALUE}","hash":"{HASH_TEST_VALUE}","domain":"{DOMAIN_TEST_VALUE}" }}]',
        )

        await select_select_index(
            pilot, f"#{ID_FILE_TYPE_SELECT}", CredsImportFileType.JSON.value
        )

        await pilot.click(f"#{ID_CONFIRM_IMPORT_BUTTON}")

    assert get_credentials(kp) == [
        Credential(
            "1",
            USERNAME_TEST_VALUE,
            PASSWORD_TEST_VALUE,
            HASH_TEST_VALUE,
            DOMAIN_TEST_VALUE,
        )
    ]


@pytest.mark.asyncio
async def test_import_credential_import_json_file(
    open_keepass: PyKeePass, load_mock_config: dict[str, Any]
):
    kp = open_keepass
    app = DbCredsApp(load_mock_config, kp)
    add_credential_keybind = load_mock_config["keybindings"]["add_credential"]

    async with app.run_test(size=(400, 400)) as pilot:
        await pilot.press(add_credential_keybind)

        # Switch tab
        await pilot.press(Keys.Right)

        await pilot.click(f"#{ID_IMPORT_BUTTON}")
        pilot.app.screen.query_one(f"#{ID_PATH_INPUT}").value = str(TEST_CREDS_JSON)
        await pilot.click(f"#{ID_CONFIRM_BUTTON}")

        await select_select_index(
            pilot, f"#{ID_FILE_TYPE_SELECT}", CredsImportFileType.JSON.value
        )

        await pilot.click(f"#{ID_CONFIRM_IMPORT_BUTTON}")

        assert get_credentials(kp) == CREDENTIALS_TEST_VALUE


@pytest.mark.asyncio
async def test_import_credential_pypykatz_json(
    open_keepass: PyKeePass, load_mock_config: dict[str, Any]
):
    kp = open_keepass
    app = DbCredsApp(load_mock_config, kp)
    add_credential_keybind = load_mock_config["keybindings"]["add_credential"]

    async with app.run_test(size=(400, 400)) as pilot:
        await pilot.press(add_credential_keybind)

        # Switch tab
        await pilot.press(Keys.Right)

        await pilot.click(f"#{ID_IMPORT_BUTTON}")
        pilot.app.screen.query_one(f"#{ID_PATH_INPUT}").value = str(
            TEST_CREDS_PYPYKATZ_JSON
        )
        await pilot.pause()
        await pilot.click(f"#{ID_CONFIRM_BUTTON}")

        await select_select_index(
            pilot, f"#{ID_FILE_TYPE_SELECT}", CredsImportFileType.PYPYKATZ_JSON.value
        )

        await pilot.click(f"#{ID_CONFIRM_IMPORT_BUTTON}")

    assert get_credentials(kp) == CREDENTIALS_TEST_VALUE_GOAD_PYPYKATZ


@pytest.mark.asyncio
async def test_import_credential_kdbx(
    open_keepass: PyKeePass, load_mock_config: dict[str, Any]
):
    kp = open_keepass
    app = DbCredsApp(load_mock_config, kp)
    add_credential_keybind = load_mock_config["keybindings"]["add_credential"]

    async with app.run_test(size=(400, 400)) as pilot:
        await pilot.press(add_credential_keybind)

        # Switch tab
        await pilot.press(Keys.Right)
        await select_select_index(
            pilot, f"#{ID_FILE_TYPE_SELECT}", CredsImportFileType.KDBX.value
        )

        await pilot.click(f"#{ID_IMPORT_BUTTON}")
        pilot.app.screen.query_one(f"#{ID_PATH_INPUT}").value = str(TEST_CREDS_KDBX)
        await pilot.click(f"#{ID_CONFIRM_BUTTON}")

        await select_input_and_enter_text(
            pilot, f"#{ID_KDBX_PASSWORD_INPUT}", PASSWORD_TEST_VALUE
        )

        await pilot.click(f"#{ID_KDBX_KEYFILE_BUTTON}")
        pilot.app.screen.query_one(f"#{ID_PATH_INPUT}").value = str(
            TEST_CREDS_KDBX_KEYFILE
        )
        await pilot.click(f"#{ID_CONFIRM_BUTTON}")

        await pilot.click(f"#{ID_CONFIRM_IMPORT_BUTTON}")

    assert get_credentials(kp) == CREDENTIALS_TEST_VALUE_KDBX
