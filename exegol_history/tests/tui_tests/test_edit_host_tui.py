from sqlalchemy import Engine
from exegol_history.config.config import AppConfig
from exegol_history.tui.db_hosts import DbHostsApp
from exegol_history.db_api.hosts import Host, get_hosts
from common import (
    IP_TEST_VALUE,
    select_input_and_enter_text,
    select_input_erase_and_enter_text,
)
from exegol_history.tui.widgets.credential_form import ID_CONFIRM_BUTTON
from exegol_history.tui.widgets.host_form import ID_IP_INPUT


async def test_edit_host_only_ip(engine: Engine, load_mock_config: AppConfig):
    app = DbHostsApp(load_mock_config, engine)
    add_host_keybind = load_mock_config.keybindings["add_host"]
    edit_host_keybind = load_mock_config.keybindings["edit_host"]

    async with app.run_test() as pilot:
        await pilot.press(add_host_keybind)
        await select_input_and_enter_text(pilot, f"#{ID_IP_INPUT}", IP_TEST_VALUE)
        await pilot.click(f"#{ID_CONFIRM_BUTTON}")

        assert get_hosts(engine) == [Host(1, ip=IP_TEST_VALUE)]

        await pilot.press(edit_host_keybind)
        await select_input_erase_and_enter_text(
            pilot, f"#{ID_IP_INPUT}", IP_TEST_VALUE + "2"
        )
        await pilot.click(f"#{ID_CONFIRM_BUTTON}")

        assert get_hosts(engine) == [Host(1, ip=IP_TEST_VALUE + "2")]


async def test_edit_host_full(engine: Engine, load_mock_config: AppConfig):
    app = DbHostsApp(load_mock_config, engine)
    add_host_keybind = load_mock_config.keybindings["add_host"]
    edit_host_keybind = load_mock_config.keybindings["edit_host"]

    async with app.run_test() as pilot:
        await pilot.press(add_host_keybind)
        await select_input_and_enter_text(pilot, f"#{ID_IP_INPUT}", IP_TEST_VALUE)
        await pilot.click(f"#{ID_CONFIRM_BUTTON}")

        assert get_hosts(engine) == [Host(1, ip=IP_TEST_VALUE)]

        await pilot.press(edit_host_keybind)
        await select_input_erase_and_enter_text(
            pilot, f"#{ID_IP_INPUT}", IP_TEST_VALUE + "2"
        )
        await pilot.click(f"#{ID_CONFIRM_BUTTON}")

        assert get_hosts(engine) == [Host(1, ip=IP_TEST_VALUE + "2")]


async def test_edit_credential_not_exist(engine: Engine, load_mock_config: AppConfig):
    app = DbHostsApp(load_mock_config, engine)
    edit_host_keybind = load_mock_config.keybindings["edit_host"]

    async with app.run_test() as pilot:
        await pilot.press(edit_host_keybind)

    assert len(get_hosts(engine)) == 0


async def test_edit_host_issue_3(engine: Engine, load_mock_config: AppConfig):
    app = DbHostsApp(load_mock_config, engine)
    add_host_keybind = load_mock_config.keybindings["add_host"]
    edit_host_keybind = load_mock_config.keybindings["edit_host"]

    async with app.run_test() as pilot:
        await pilot.press(add_host_keybind)
        await select_input_and_enter_text(pilot, f"#{ID_IP_INPUT}", IP_TEST_VALUE)
        await pilot.click(f"#{ID_CONFIRM_BUTTON}")

        assert get_hosts(engine) == [Host(1, ip=IP_TEST_VALUE)]

        await pilot.press(edit_host_keybind)
        await pilot.press(edit_host_keybind)
        await select_input_erase_and_enter_text(
            pilot, f"#{ID_IP_INPUT}", IP_TEST_VALUE + "2"
        )
        await pilot.click(f"#{ID_CONFIRM_BUTTON}")

        assert get_hosts(engine) == [Host(1, ip=IP_TEST_VALUE + "2")]
