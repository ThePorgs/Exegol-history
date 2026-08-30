from sqlalchemy import Engine
from exegol_history.config.config import AppConfig
from exegol_history.tui.db_hosts import DbHostsApp
from exegol_history.db_api.hosts import Host, add_hosts, get_hosts
from common import (
    IP_TEST_VALUE,
    HOSTNAME_TEST_VALUE,
    ROLE_TEST_VALUE,
    select_input_and_enter_text,
)

from exegol_history.tui.widgets.credential_form import ID_CONFIRM_BUTTON
from exegol_history.tui.screens.delete_object import (
    ID_CONFIRM_RANGE_BUTTON,
    ID_IDS_INPUT,
)
from exegol_history.tui.widgets.host_form import (
    ID_HOSTNAME_INPUT,
    ID_IP_INPUT,
    ID_ROLE_INPUT,
)
from textual.keys import Keys


async def test_delete_host(engine: Engine, load_mock_config: AppConfig):
    app = DbHostsApp(load_mock_config, engine)
    add_host_keybind = load_mock_config.keybindings["add_host"]
    delete_host_keybind = load_mock_config.keybindings["delete_host"]

    async with app.run_test() as pilot:
        await pilot.press(add_host_keybind)
        await select_input_and_enter_text(pilot, f"#{ID_IP_INPUT}", IP_TEST_VALUE)
        await pilot.click(f"#{ID_CONFIRM_BUTTON}")

        assert get_hosts(engine) == [Host(1, ip=IP_TEST_VALUE)]

        await pilot.press(delete_host_keybind)
        await pilot.click(f"#{ID_CONFIRM_BUTTON}")

        assert len(get_hosts(engine)) == 0


async def test_delete_host_full(engine: Engine, load_mock_config: AppConfig):
    app = DbHostsApp(load_mock_config, engine)
    add_host_keybind = load_mock_config.keybindings["add_host"]
    delete_host_keybind = load_mock_config.keybindings["delete_host"]

    async with app.run_test() as pilot:
        await pilot.press(add_host_keybind)
        await select_input_and_enter_text(pilot, f"#{ID_IP_INPUT}", IP_TEST_VALUE)
        await select_input_and_enter_text(
            pilot, f"#{ID_HOSTNAME_INPUT}", HOSTNAME_TEST_VALUE
        )
        await select_input_and_enter_text(pilot, f"#{ID_ROLE_INPUT}", ROLE_TEST_VALUE)
        await pilot.click(f"#{ID_CONFIRM_BUTTON}")

        assert get_hosts(engine) == [
            Host(
                1,
                ip=IP_TEST_VALUE,
                hostname=HOSTNAME_TEST_VALUE,
                role=ROLE_TEST_VALUE,
            )
        ]

        await pilot.press(delete_host_keybind)
        await pilot.click(f"#{ID_CONFIRM_BUTTON}")

        assert len(get_hosts(engine)) == 0


async def test_delete_host_range(
    engine: Engine, load_mock_config: AppConfig, HOSTS_TEST_VALUE: list[Host]
):
    app = DbHostsApp(load_mock_config, engine)
    delete_host_keybind = load_mock_config.keybindings["delete_host"]

    add_hosts(engine, [host.as_dict() for host in HOSTS_TEST_VALUE])
    assert get_hosts(engine) == HOSTS_TEST_VALUE

    async with app.run_test() as pilot:
        await pilot.press(delete_host_keybind)
        await pilot.press(Keys.Right)
        await select_input_and_enter_text(
            pilot,
            f"#{ID_IDS_INPUT}",
            "1-2,4",
        )
        await pilot.click(f"#{ID_CONFIRM_RANGE_BUTTON}")

        assert get_hosts(engine) == HOSTS_TEST_VALUE[2:3]


async def test_delete_host_range_with_invalid_id(
    engine: Engine, load_mock_config: AppConfig, HOSTS_TEST_VALUE: list[Host]
):
    app = DbHostsApp(load_mock_config, engine)
    delete_host_keybind = load_mock_config.keybindings["delete_host"]

    add_hosts(engine, [host.as_dict() for host in HOSTS_TEST_VALUE])
    assert get_hosts(engine) == HOSTS_TEST_VALUE

    async with app.run_test() as pilot:
        await pilot.press(delete_host_keybind)
        await pilot.press(Keys.Right)
        await select_input_and_enter_text(
            pilot,
            f"#{ID_IDS_INPUT}",
            "1-2,999,4",
        )
        await pilot.click(f"#{ID_CONFIRM_RANGE_BUTTON}")

        assert get_hosts(engine) == HOSTS_TEST_VALUE[2:3]


# Trying to delete an object when no object are present should not raise an exception


async def test_delete_host_empty(engine: Engine, load_mock_config: AppConfig):
    app = DbHostsApp(load_mock_config, engine)
    delete_host_keybind = load_mock_config.keybindings["delete_host"]

    async with app.run_test() as pilot:
        await pilot.press(delete_host_keybind)


async def test_delete_host_issue_3(engine: Engine, load_mock_config: AppConfig):
    app = DbHostsApp(load_mock_config, engine)
    delete_host_keybind = load_mock_config.keybindings["delete_host"]

    add_hosts(engine, [Host(ip=IP_TEST_VALUE).as_dict()])

    async with app.run_test() as pilot:
        await pilot.press(delete_host_keybind)
        await pilot.press(delete_host_keybind)
        await pilot.click(f"#{ID_CONFIRM_BUTTON}")
