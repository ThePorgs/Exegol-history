from textual.keys import Keys
import pytest
from exegol_history.db_api.importing import HostsImportFileType
from exegol_history.tui.db_hosts import DbHostsApp
from exegol_history.db_api.hosts import Host, get_hosts
from common import (
    HOSTS_TEST_VALUE,
    IP_TEST_VALUE,
    HOSTNAME_TEST_VALUE,
    ROLE_TEST_VALUE,
    TEST_HOSTS_CSV_COMMA,
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
)
from exegol_history.tui.screens.open_file import ID_PATH_INPUT


@pytest.mark.asyncio
async def test_import_host_csv(
    open_keepass: PyKeePass, load_mock_config: dict[str, Any]
):
    kp = open_keepass
    app = DbHostsApp(load_mock_config, kp)
    add_host_keybind = load_mock_config["keybindings"]["add_host"]

    async with app.run_test(size=(400, 400)) as pilot:
        await pilot.press(add_host_keybind)

        # Switch tab
        await pilot.press(Keys.Right)

        await select_input_and_enter_text(
            pilot,
            f"#{ID_FILE_TEXTAREA}",
            f"ip,hostname,role\n\n{IP_TEST_VALUE},{HOSTNAME_TEST_VALUE},{ROLE_TEST_VALUE}",
        )

        await select_select_index(
            pilot, f"#{ID_FILE_TYPE_SELECT}", HostsImportFileType.CSV.value
        )

        await pilot.click(f"#{ID_CONFIRM_IMPORT_BUTTON}")

    assert get_hosts(kp) == [
        Host(
            id="1", ip=IP_TEST_VALUE, hostname=HOSTNAME_TEST_VALUE, role=ROLE_TEST_VALUE
        )
    ]


@pytest.mark.asyncio
async def test_import_host_csv_file(
    open_keepass: PyKeePass, load_mock_config: dict[str, Any]
):
    kp = open_keepass
    app = DbHostsApp(load_mock_config, kp)
    add_host_keybind = load_mock_config["keybindings"]["add_host"]

    async with app.run_test(size=(400, 400)) as pilot:
        await pilot.press(add_host_keybind)

        # Switch tab
        await pilot.press(Keys.Right)

        await pilot.click(f"#{ID_IMPORT_BUTTON}")
        pilot.app.screen.query_one(f"#{ID_PATH_INPUT}").value = str(
            TEST_HOSTS_CSV_COMMA
        )
        await pilot.pause()
        await pilot.click(f"#{ID_CONFIRM_BUTTON}")

        # Choose CSV file type
        await select_select_index(
            pilot, f"#{ID_FILE_TYPE_SELECT}", HostsImportFileType.CSV.value
        )

        await pilot.click(f"#{ID_CONFIRM_IMPORT_BUTTON}")

    assert get_hosts(kp) == HOSTS_TEST_VALUE
