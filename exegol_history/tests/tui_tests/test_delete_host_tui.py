import pytest
from exegol_history.tui.db_hosts.db_hosts import DbHostsApp
from exegol_history.db_api.hosts import Host, add_host, add_hosts, get_hosts
from common import (
    HOSTS_TEST_VALUE,
    IP_TEST_VALUE,
    HOSTNAME_TEST_VALUE,
    ROLE_TEST_VALUE,
    select_input_and_enter_text,
)
from pykeepass import PyKeePass
from typing import Any

from exegol_history.tui.widgets.credential_form import ID_CONFIRM_BUTTON
from exegol_history.tui.widgets.delete_objects import (
    ID_CONFIRM_RANGE_BUTTON,
    ID_IDS_INPUT,
)
from exegol_history.tui.widgets.host_form import (
    ID_HOSTNAME_INPUT,
    ID_IP_INPUT,
    ID_ROLE_INPUT,
)
from textual.keys import Keys


@pytest.mark.asyncio
async def test_delete_host(open_keepass: PyKeePass, load_mock_config: dict[str, Any]):
    kp = open_keepass
    app = DbHostsApp(load_mock_config, kp)
    add_host_keybind = load_mock_config["keybindings"]["add_host"]
    delete_host_keybind = load_mock_config["keybindings"]["delete_host"]

    async with app.run_test() as pilot:
        await pilot.press(add_host_keybind)
        await select_input_and_enter_text(pilot, f"#{ID_IP_INPUT}", IP_TEST_VALUE)
        await pilot.click(f"#{ID_CONFIRM_BUTTON}")

        assert get_hosts(kp) == [Host(id="1", ip=IP_TEST_VALUE)]

        await pilot.press(delete_host_keybind)
        await pilot.click(f"#{ID_CONFIRM_BUTTON}")

        assert len(get_hosts(kp)) == 0


@pytest.mark.asyncio
async def test_delete_host_full(
    open_keepass: PyKeePass, load_mock_config: dict[str, Any]
):
    kp = open_keepass
    app = DbHostsApp(load_mock_config, kp)
    add_host_keybind = load_mock_config["keybindings"]["add_host"]
    delete_host_keybind = load_mock_config["keybindings"]["delete_host"]

    async with app.run_test() as pilot:
        await pilot.press(add_host_keybind)
        await select_input_and_enter_text(pilot, f"#{ID_IP_INPUT}", IP_TEST_VALUE)
        await select_input_and_enter_text(
            pilot, f"#{ID_HOSTNAME_INPUT}", HOSTNAME_TEST_VALUE
        )
        await select_input_and_enter_text(pilot, f"#{ID_ROLE_INPUT}", ROLE_TEST_VALUE)
        await pilot.click(f"#{ID_CONFIRM_BUTTON}")

        assert get_hosts(kp) == [
            Host(
                id="1",
                ip=IP_TEST_VALUE,
                hostname=HOSTNAME_TEST_VALUE,
                role=ROLE_TEST_VALUE,
            )
        ]

        await pilot.press(delete_host_keybind)
        await pilot.click(f"#{ID_CONFIRM_BUTTON}")

        assert len(get_hosts(kp)) == 0


@pytest.mark.asyncio
async def test_delete_host_range(
    open_keepass: PyKeePass, load_mock_config: dict[str, Any]
):
    kp = open_keepass
    app = DbHostsApp(load_mock_config, kp)
    delete_host_keybind = load_mock_config["keybindings"]["delete_host"]

    add_hosts(kp, HOSTS_TEST_VALUE)
    assert get_hosts(kp) == HOSTS_TEST_VALUE

    async with app.run_test() as pilot:
        await pilot.press(delete_host_keybind)
        await pilot.press(Keys.Right)
        await select_input_and_enter_text(
            pilot,
            f"#{ID_IDS_INPUT}",
            "1-2,4",
        )
        await pilot.click(f"#{ID_CONFIRM_RANGE_BUTTON}")

        assert get_hosts(kp) == HOSTS_TEST_VALUE[2:3]


@pytest.mark.asyncio
async def test_delete_host_range_with_invalid_id(
    open_keepass: PyKeePass, load_mock_config: dict[str, Any]
):
    kp = open_keepass
    app = DbHostsApp(load_mock_config, kp)
    delete_host_keybind = load_mock_config["keybindings"]["delete_host"]

    add_hosts(kp, HOSTS_TEST_VALUE)
    assert get_hosts(kp) == HOSTS_TEST_VALUE

    async with app.run_test() as pilot:
        await pilot.press(delete_host_keybind)
        await pilot.press(Keys.Right)
        await select_input_and_enter_text(
            pilot,
            f"#{ID_IDS_INPUT}",
            "1-2,999,4",
        )
        await pilot.click(f"#{ID_CONFIRM_RANGE_BUTTON}")

        assert get_hosts(kp) == HOSTS_TEST_VALUE[2:3]


# Trying to delete an object when no object are present should not raise an exception
@pytest.mark.asyncio
async def test_delete_host_empty(
    open_keepass: PyKeePass, load_mock_config: dict[str, Any]
):
    kp = open_keepass
    app = DbHostsApp(load_mock_config, kp)
    delete_host_keybind = load_mock_config["keybindings"]["delete_host"]

    async with app.run_test() as pilot:
        await pilot.press(delete_host_keybind)


@pytest.mark.asyncio
async def test_delete_host_issue_3(
    open_keepass: PyKeePass, load_mock_config: dict[str, Any]
):
    kp = open_keepass
    app = DbHostsApp(load_mock_config, kp)
    delete_host_keybind = load_mock_config["keybindings"]["delete_host"]

    add_host(kp, Host())

    async with app.run_test() as pilot:
        await pilot.press(delete_host_keybind)
        await pilot.press(delete_host_keybind)
        await pilot.click(f"#{ID_CONFIRM_BUTTON}")
