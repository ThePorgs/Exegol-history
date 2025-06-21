import pytest
import subprocess
import sys
from exegol_history.cli.utils import write_host_in_profile
from exegol_history.tui.db_hosts import DbHostsApp
from exegol_history.db_api.hosts import Host, get_hosts
from common import (
    IP_TEST_VALUE,
    HOSTNAME_TEST_VALUE,
    ROLE_TEST_VALUE,
    select_input_and_enter_text,
)
from pykeepass import PyKeePass
from typing import Any
from exegol_history.tui.widgets.credential_form import ID_CONFIRM_BUTTON
from exegol_history.tui.widgets.host_form import (
    ID_HOSTNAME_INPUT,
    ID_IP_INPUT,
    ID_ROLE_INPUT,
)


@pytest.mark.asyncio
async def test_add_host_only_ip(
    open_keepass: PyKeePass, load_mock_config: dict[str, Any]
):
    kp = open_keepass
    app = DbHostsApp(load_mock_config, kp)
    add_host_keybind = load_mock_config["keybindings"]["add_host"]

    async with app.run_test() as pilot:
        await pilot.press(add_host_keybind)
        await select_input_and_enter_text(pilot, f"#{ID_IP_INPUT}", IP_TEST_VALUE)
        await pilot.click(f"#{ID_CONFIRM_BUTTON}")

    assert get_hosts(kp) == [Host(id="1", ip=IP_TEST_VALUE)]


@pytest.mark.asyncio
async def test_add_host_only_half(
    open_keepass: PyKeePass, load_mock_config: dict[str, Any]
):
    kp = open_keepass
    app = DbHostsApp(load_mock_config, kp)
    add_host_keybind = load_mock_config["keybindings"]["add_host"]

    async with app.run_test() as pilot:
        await pilot.press(add_host_keybind)
        await select_input_and_enter_text(pilot, f"#{ID_IP_INPUT}", IP_TEST_VALUE)
        await select_input_and_enter_text(
            pilot, f"#{ID_HOSTNAME_INPUT}", HOSTNAME_TEST_VALUE
        )
        await pilot.click(f"#{ID_CONFIRM_BUTTON}")

    assert get_hosts(kp) == [
        Host(id="1", ip=IP_TEST_VALUE, hostname=HOSTNAME_TEST_VALUE)
    ]


@pytest.mark.asyncio
async def test_add_host_full(open_keepass: PyKeePass, load_mock_config: dict[str, Any]):
    kp = open_keepass
    app = DbHostsApp(load_mock_config, kp)
    add_host_keybind = load_mock_config["keybindings"]["add_host"]

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
            id="1", ip=IP_TEST_VALUE, hostname=HOSTNAME_TEST_VALUE, role=ROLE_TEST_VALUE
        )
    ]


@pytest.mark.skipif(sys.platform.startswith("win"), reason="require Linux")
@pytest.mark.asyncio
async def test_add_and_set_host_full(
    open_keepass: PyKeePass, load_mock_config: dict[str, Any]
):
    kp = open_keepass
    app = DbHostsApp(load_mock_config, kp)
    add_host_keybind = load_mock_config["keybindings"]["add_host"]

    async with app.run_test() as pilot:
        await pilot.press(add_host_keybind)
        await select_input_and_enter_text(pilot, f"#{ID_IP_INPUT}", IP_TEST_VALUE)
        await select_input_and_enter_text(
            pilot, f"#{ID_HOSTNAME_INPUT}", HOSTNAME_TEST_VALUE
        )
        await select_input_and_enter_text(pilot, f"#{ID_ROLE_INPUT}", ROLE_TEST_VALUE)
        await pilot.click(f"#{ID_CONFIRM_BUTTON}")

    host = Host(
        id="1", ip=IP_TEST_VALUE, hostname=HOSTNAME_TEST_VALUE, role=ROLE_TEST_VALUE
    )

    assert get_hosts(kp) == [host]

    write_host_in_profile(host, load_mock_config)
    command_output = subprocess.run(
        [
            "bash",
            "-c",
            f"source {load_mock_config['paths']['profile_sh_path']} && echo $IP $TARGET $DC_HOST",
        ],
        stdout=subprocess.PIPE,
    )
    envs = command_output.stdout.decode("utf8")

    assert IP_TEST_VALUE in envs
    assert HOSTNAME_TEST_VALUE in envs
    assert ROLE_TEST_VALUE in envs


@pytest.mark.asyncio
async def test_add_host_empty(
    open_keepass: PyKeePass, load_mock_config: dict[str, Any]
):
    kp = open_keepass
    app = DbHostsApp(load_mock_config, kp)
    add_host_keybind = load_mock_config["keybindings"]["add_host"]

    async with app.run_test() as pilot:
        await pilot.press(add_host_keybind)
        await pilot.click(f"#{ID_CONFIRM_BUTTON}")

    assert get_hosts(kp) == [Host("1")]


@pytest.mark.asyncio
async def test_add_host_existing(
    open_keepass: PyKeePass, load_mock_config: dict[str, Any]
):
    kp = open_keepass
    app = DbHostsApp(load_mock_config, kp)
    add_host_keybind = load_mock_config["keybindings"]["add_host"]

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

        await pilot.press(add_host_keybind)
        await select_input_and_enter_text(pilot, f"#{ID_IP_INPUT}", IP_TEST_VALUE)
        await select_input_and_enter_text(
            pilot, f"#{ID_HOSTNAME_INPUT}", HOSTNAME_TEST_VALUE + "2"
        )
        await select_input_and_enter_text(
            pilot, f"#{ID_ROLE_INPUT}", ROLE_TEST_VALUE + "2"
        )
        await pilot.click(f"#{ID_CONFIRM_BUTTON}")

        assert get_hosts(kp) == [
            Host(
                id="1",
                ip=IP_TEST_VALUE,
                hostname=HOSTNAME_TEST_VALUE,
                role=ROLE_TEST_VALUE,
            ),
            Host(
                id="2",
                ip=IP_TEST_VALUE,
                hostname=HOSTNAME_TEST_VALUE + "2",
                role=ROLE_TEST_VALUE + "2",
            ),
        ]


@pytest.mark.asyncio
async def test_add_host_issue_3(
    open_keepass: PyKeePass, load_mock_config: dict[str, Any]
):
    kp = open_keepass
    app = DbHostsApp(load_mock_config, kp)
    add_host_keybind = load_mock_config["keybindings"]["add_host"]

    async with app.run_test() as pilot:
        await pilot.press(add_host_keybind)
        await pilot.press(add_host_keybind)
        await select_input_and_enter_text(pilot, f"#{ID_IP_INPUT}", IP_TEST_VALUE)
        await pilot.click(f"#{ID_CONFIRM_BUTTON}")

    assert get_hosts(kp) == [Host(id="1", ip=IP_TEST_VALUE)]
