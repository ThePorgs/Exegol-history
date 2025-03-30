import pytest
import os
import subprocess
import sys

from exegol_history.tui.db_hosts.db_hosts import DbHostsApp
from exegol_history.db_api.hosts import get_hosts
from common_tui import (
    IP_TEST_VALUE,
    HOSTNAME_TEST_VALUE,
    ROLE_TEST_VALUE,
    TEST_PROFILE_SH,
    select_input_and_enter_text,
)
from exegol_history.db_api.utils import write_host_in_profile
from pykeepass import PyKeePass
from typing import Any


@pytest.mark.asyncio
async def test_add_host_import_csv_tui(
    open_keepass: PyKeePass, load_mock_config: dict[str, Any]
):
    config = load_mock_config
    kp = open_keepass
    app = DbHostsApp(config, kp)

    async with app.run_test() as pilot:
        await pilot.press("f3")

        # Switch tab
        await pilot.press("right")

        await select_input_and_enter_text(
            pilot,
            "#file_textarea",
            f"{IP_TEST_VALUE},{HOSTNAME_TEST_VALUE},{ROLE_TEST_VALUE}",
        )

        await pilot.click("#file_type_select")
        await pilot.press("down")
        await pilot.press("down")
        await pilot.press("enter")

        await pilot.click("#confirm_import")

    hosts = get_hosts(kp)

    assert hosts == [(IP_TEST_VALUE, HOSTNAME_TEST_VALUE, ROLE_TEST_VALUE)]


@pytest.mark.asyncio
async def test_add_host_import_csv_file_tui(
    open_keepass: PyKeePass, load_mock_config: dict[str, Any]
):
    config = load_mock_config
    kp = open_keepass
    app = DbHostsApp(config, kp)

    async with app.run_test() as pilot:
        await pilot.press("f3")

        # Switch tab
        await pilot.press("right")

        await pilot.click("#import_file")
        pilot.app.query_one("#label_selected_path").update(
            os.path.dirname(os.path.abspath(__file__)) + "/../artifacts/hosts.txt"
        )
        await pilot.click("#select_button")

        # Choose CSV file type
        await pilot.click("#file_type_select")
        await pilot.press("down")
        await pilot.press("down")
        await pilot.press("enter")

        await pilot.click("#confirm_import")

    hosts = get_hosts(kp)

    assert hosts == [(IP_TEST_VALUE, HOSTNAME_TEST_VALUE, ROLE_TEST_VALUE)]


@pytest.mark.asyncio
async def test_add_host_only_ip_tui(
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


@pytest.mark.asyncio
async def test_add_host_only_half_tui(
    open_keepass: PyKeePass, load_mock_config: dict[str, Any]
):
    config = load_mock_config
    kp = open_keepass
    app = DbHostsApp(config, kp)

    async with app.run_test() as pilot:
        await pilot.press("f3")
        await select_input_and_enter_text(pilot, "#ip", IP_TEST_VALUE)
        await select_input_and_enter_text(pilot, "#hostname", HOSTNAME_TEST_VALUE)
        await pilot.click("#confirm_add")

    hosts = get_hosts(kp)

    assert hosts == [(IP_TEST_VALUE, HOSTNAME_TEST_VALUE, "")]


@pytest.mark.asyncio
async def test_add_host_full_tui(
    open_keepass: PyKeePass, load_mock_config: dict[str, Any]
):
    config = load_mock_config
    kp = open_keepass
    app = DbHostsApp(config, kp)

    async with app.run_test() as pilot:
        await pilot.press("f3")
        await select_input_and_enter_text(pilot, "#ip", IP_TEST_VALUE)
        await select_input_and_enter_text(pilot, "#hostname", HOSTNAME_TEST_VALUE)
        await select_input_and_enter_text(pilot, "#role", ROLE_TEST_VALUE)
        await pilot.click("#confirm_add")

    hosts = get_hosts(kp)

    assert hosts == [(IP_TEST_VALUE, HOSTNAME_TEST_VALUE, ROLE_TEST_VALUE)]


@pytest.mark.skipif(sys.platform.startswith("win"), reason="require Linux")
@pytest.mark.asyncio
async def test_add_and_set_host_full_tui(
    open_keepass: PyKeePass, load_mock_config: dict[str, Any]
):
    config = load_mock_config
    kp = open_keepass
    app = DbHostsApp(config, kp)

    async with app.run_test() as pilot:
        await pilot.press("f3")
        await select_input_and_enter_text(pilot, "#ip", IP_TEST_VALUE)
        await select_input_and_enter_text(pilot, "#hostname", HOSTNAME_TEST_VALUE)
        await select_input_and_enter_text(pilot, "#role", ROLE_TEST_VALUE)
        await pilot.click("#confirm_add")

    hosts = get_hosts(kp)

    assert hosts == [(IP_TEST_VALUE, HOSTNAME_TEST_VALUE, ROLE_TEST_VALUE)]

    write_host_in_profile(
        TEST_PROFILE_SH, IP_TEST_VALUE, HOSTNAME_TEST_VALUE, ROLE_TEST_VALUE
    )
    command_output = subprocess.run(
        [
            "bash",
            "-c",
            f"source {TEST_PROFILE_SH} && echo $IP $TARGET $DC_HOST",
        ],
        stdout=subprocess.PIPE,
    )
    envs = command_output.stdout.decode("utf8")

    assert IP_TEST_VALUE in envs
    assert HOSTNAME_TEST_VALUE in envs
    assert ROLE_TEST_VALUE in envs


@pytest.mark.asyncio
async def test_add_host_empty_tui(
    open_keepass: PyKeePass, load_mock_config: dict[str, Any]
):
    config = load_mock_config
    kp = open_keepass
    app = DbHostsApp(config, kp)

    async with app.run_test() as pilot:
        await pilot.press("f3")
        await pilot.click("#confirm_add")

    hosts = get_hosts(kp)

    assert len(hosts) == 0


@pytest.mark.asyncio
async def test_add_host_existing_tui(
    open_keepass: PyKeePass, load_mock_config: dict[str, Any]
):
    config = load_mock_config
    kp = open_keepass
    app = DbHostsApp(config, kp)

    async with app.run_test() as pilot:
        await pilot.press("f3")

        await select_input_and_enter_text(pilot, "#ip", IP_TEST_VALUE)
        await select_input_and_enter_text(pilot, "#hostname", HOSTNAME_TEST_VALUE)
        await select_input_and_enter_text(pilot, "#role", ROLE_TEST_VALUE)
        await pilot.click("#confirm_add")

        hosts = get_hosts(kp)

        assert hosts == [(IP_TEST_VALUE, HOSTNAME_TEST_VALUE, ROLE_TEST_VALUE)]

        await pilot.press("f3")
        await select_input_and_enter_text(pilot, "#ip", IP_TEST_VALUE)
        await select_input_and_enter_text(pilot, "#hostname", HOSTNAME_TEST_VALUE + "2")
        await select_input_and_enter_text(pilot, "#role", ROLE_TEST_VALUE + "2")
        await pilot.click("#confirm_add")

        hosts = get_hosts(kp)

        assert hosts == [
            (IP_TEST_VALUE, HOSTNAME_TEST_VALUE + "2", ROLE_TEST_VALUE + "2")
        ]


@pytest.mark.asyncio
async def test_add_host_issue_3(
    open_keepass: PyKeePass, load_mock_config: dict[str, Any]
):
    config = load_mock_config
    kp = open_keepass
    app = DbHostsApp(config, kp)

    async with app.run_test() as pilot:
        await pilot.press("f3")
        await pilot.press("f3")
        await select_input_and_enter_text(pilot, "#ip", IP_TEST_VALUE)
        await pilot.click("#confirm_add")

    hosts = get_hosts(kp)

    assert hosts == [(IP_TEST_VALUE, "", "")]
