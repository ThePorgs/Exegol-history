import pytest

from exegol_history.tui.db_hosts.db_hosts import DbHostsApp
from exegol_history.db_api.hosts import get_hosts
from common_tui import (
    IP_TEST_VALUE,
    select_input_and_enter_text,
    select_input_erase_and_enter_text,
)
from pykeepass import PyKeePass
from typing import Any


@pytest.mark.asyncio
async def test_edit_host_only_ip_tui(
    open_keepass: PyKeePass, load_mock_config: dict[str, Any]
):
    config = load_mock_config
    kp = open_keepass
    app = DbHostsApp(config, kp)

    async with app.run_test() as pilot:
        await pilot.press("f3")
        await select_input_and_enter_text(pilot, "#ip", IP_TEST_VALUE)
        await pilot.click("#confirm_add")

        hosts = get_hosts(kp)

        assert hosts == [(IP_TEST_VALUE, "", "")]

        await pilot.press("f5")
        await select_input_erase_and_enter_text(pilot, "#ip", IP_TEST_VALUE + "2")
        await pilot.click("#confirm")

        hosts = get_hosts(kp)

        assert hosts == [(IP_TEST_VALUE + "2", "", "")]


@pytest.mark.asyncio
async def test_edit_host_full_tui(
    open_keepass: PyKeePass, load_mock_config: dict[str, Any]
):
    config = load_mock_config
    kp = open_keepass
    app = DbHostsApp(config, kp)

    async with app.run_test() as pilot:
        await pilot.press("f3")
        await select_input_and_enter_text(pilot, "#ip", IP_TEST_VALUE)
        await pilot.click("#confirm_add")

        hosts = get_hosts(kp)

        assert hosts == [(IP_TEST_VALUE, "", "")]

        await pilot.press("f5")
        await select_input_erase_and_enter_text(pilot, "#ip", IP_TEST_VALUE + "2")
        await pilot.click("#confirm")

        hosts = get_hosts(kp)

        assert hosts == [(IP_TEST_VALUE + "2", "", "")]


@pytest.mark.asyncio
async def test_edit_credential_not_exist_tui(
    open_keepass: PyKeePass, load_mock_config: dict[str, Any]
):
    config = load_mock_config
    kp = open_keepass
    app = DbHostsApp(config, kp)

    async with app.run_test() as pilot:
        await pilot.press("f5")

    hosts = get_hosts(kp)
    assert len(hosts) == 0


@pytest.mark.asyncio
async def test_edit_host_issue_3(
    open_keepass: PyKeePass, load_mock_config: dict[str, Any]
):
    config = load_mock_config
    kp = open_keepass
    app = DbHostsApp(config, kp)

    async with app.run_test() as pilot:
        await pilot.press("f3")
        await select_input_and_enter_text(pilot, "#ip", IP_TEST_VALUE)
        await pilot.click("#confirm_add")

        hosts = get_hosts(kp)

        assert hosts == [(IP_TEST_VALUE, "", "")]

        await pilot.press("f5")
        await pilot.press("f5")
        await select_input_erase_and_enter_text(pilot, "#ip", IP_TEST_VALUE + "2")
        await pilot.click("#confirm")

        hosts = get_hosts(kp)

        assert hosts == [(IP_TEST_VALUE + "2", "", "")]
