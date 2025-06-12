import tempfile
import pytest
from exegol_history.db_api.importing import HostsImportFileType
from exegol_history.tui.db_hosts.db_hosts import DbHostsApp
from exegol_history.db_api.hosts import add_hosts
from common import (
    HOSTS_TEST_VALUE,
    TEST_HOSTS_JSON,
    select_select_index,
)
from pykeepass import PyKeePass
from typing import Any
from exegol_history.tui.widgets.credential_form import ID_CONFIRM_BUTTON
from exegol_history.tui.widgets.export_objects import (
    ID_BROWSE_BUTTON,
    ID_EXPORT_TYPE_SELECT,
)
from exegol_history.tui.widgets.open_file import ID_PATH_INPUT


@pytest.mark.asyncio
async def test_export_host_csv(
    open_keepass: PyKeePass, load_mock_config: dict[str, Any]
):
    kp = open_keepass
    app = DbHostsApp(load_mock_config, kp)
    export_host_keybind = load_mock_config["keybindings"]["export_host"]
    temp_export_csv = tempfile.NamedTemporaryFile()
    add_hosts(kp, HOSTS_TEST_VALUE)

    async with app.run_test(size=(400, 400)) as pilot:
        await pilot.press(export_host_keybind)

        await pilot.click(f"#{ID_BROWSE_BUTTON}")
        pilot.app.query_one(f"#{ID_PATH_INPUT}").value = temp_export_csv.name
        await pilot.click(f"#{ID_CONFIRM_BUTTON}")
        await pilot.click(f"#{ID_CONFIRM_BUTTON}")

    with open(temp_export_csv.name, "r") as temp_export_csv_read:
        assert (
            temp_export_csv_read.read()
            == "ip,hostname,role\n127.0.0.1,DC01,DC\n127.0.0.12,,\n127.0.0.12,DC012,\n127.0.0.13,,\n"
        )


@pytest.mark.asyncio
async def test_export_host_json(
    open_keepass: PyKeePass, load_mock_config: dict[str, Any]
):
    kp = open_keepass
    app = DbHostsApp(load_mock_config, kp)
    export_host_keybind = load_mock_config["keybindings"]["export_host"]
    temp_export_json = tempfile.NamedTemporaryFile()
    add_hosts(kp, HOSTS_TEST_VALUE)

    async with app.run_test(size=(400, 400)) as pilot:
        await pilot.press(export_host_keybind)

        await select_select_index(
            pilot, f"#{ID_EXPORT_TYPE_SELECT}", HostsImportFileType.JSON.value
        )
        await pilot.click(f"#{ID_BROWSE_BUTTON}")
        pilot.app.query_one(f"#{ID_PATH_INPUT}").value = temp_export_json.name
        await pilot.click(f"#{ID_CONFIRM_BUTTON}")
        await pilot.click(f"#{ID_CONFIRM_BUTTON}")

    with open(temp_export_json.name, "r") as temp_export_json_read:
        with open(TEST_HOSTS_JSON, "r") as json_assert:
            tmp1 = json_assert.read().replace(" ", "").replace("\n", "")
            tmp2 = temp_export_json_read.read().replace(" ", "").replace("\n", "")

            assert tmp1 == tmp2
