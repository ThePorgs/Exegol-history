import tempfile
from sqlalchemy import Engine
from exegol_history.config.config import AppConfig
from exegol_history.db_api.importing import HostsImportFileType
from exegol_history.tui.db_hosts import DbHostsApp
from exegol_history.db_api.hosts import Host, add_hosts
from common import (
    TEST_HOSTS_JSON,
    select_select_index,
)
from exegol_history.tui.screens.export_object import (
    ID_BROWSE_BUTTON,
    ID_EXPORT_TYPE_SELECT,
)
from exegol_history.tui.widgets.credential_form import ID_CONFIRM_BUTTON
from exegol_history.tui.screens.open_file import ID_PATH_INPUT


async def test_export_host_csv(
    engine: Engine, load_mock_config: AppConfig, HOSTS_TEST_VALUE: list[Host]
):
    app = DbHostsApp(load_mock_config, engine)
    export_host_keybind = load_mock_config.keybindings["export_host"]
    temp_export_csv = tempfile.NamedTemporaryFile(delete=False)
    add_hosts(engine, [host.as_dict() for host in HOSTS_TEST_VALUE])

    async with app.run_test(size=(400, 400)) as pilot:
        await pilot.press(export_host_keybind)

        await pilot.click(f"#{ID_BROWSE_BUTTON}")
        pilot.app.screen.query_one(f"#{ID_PATH_INPUT}").value = temp_export_csv.name
        await pilot.pause()
        await pilot.click(f"#{ID_CONFIRM_BUTTON}")
        await pilot.click(f"#{ID_CONFIRM_BUTTON}")

    with open(temp_export_csv.name, "r") as temp_export_csv_read:
        assert (
            temp_export_csv_read.read()
            == "ip,hostname,role\n127.0.0.1,DC01,DC\n127.0.0.12,,\n127.0.0.12,DC012,\n127.0.0.13,,\n"
        )


async def test_export_host_json(
    engine: Engine, load_mock_config: AppConfig, HOSTS_TEST_VALUE: list[Host]
):
    app = DbHostsApp(load_mock_config, engine)
    export_host_keybind = load_mock_config.keybindings["export_host"]
    temp_export_json = tempfile.NamedTemporaryFile(delete=False)
    add_hosts(engine, [host.as_dict() for host in HOSTS_TEST_VALUE])

    async with app.run_test(size=(400, 400)) as pilot:
        await pilot.press(export_host_keybind)

        await select_select_index(
            pilot, f"#{ID_EXPORT_TYPE_SELECT}", HostsImportFileType.JSON.value
        )
        await pilot.click(f"#{ID_BROWSE_BUTTON}")
        pilot.app.screen.query_one(f"#{ID_PATH_INPUT}").value = temp_export_json.name
        await pilot.pause()
        await pilot.click(f"#{ID_CONFIRM_BUTTON}")
        await pilot.click(f"#{ID_CONFIRM_BUTTON}")

    with open(temp_export_json.name, "r") as temp_export_json_read:
        with open(TEST_HOSTS_JSON, "r") as json_assert:
            tmp1 = json_assert.read().replace(" ", "").replace("\n", "")
            tmp2 = temp_export_json_read.read().replace(" ", "").replace("\n", "")

            assert tmp1 == tmp2
