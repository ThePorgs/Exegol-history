import pytest
import subprocess
import sys

from sqlalchemy import Engine
from exegol_history.cli.utils import write_host_in_profile
from exegol_history.config.config import AppConfig
from exegol_history.tui.db_hosts import DbHostsApp
from exegol_history.db_api.hosts import Host, get_hosts
from common import (
    IP_TEST_VALUE,
    HOSTNAME_TEST_VALUE,
    ROLE_TEST_VALUE,
    select_input_and_enter_text,
)
from exegol_history.tui.widgets.credential_form import ID_CONFIRM_BUTTON
from exegol_history.tui.widgets.host_form import (
    ID_HOSTNAME_INPUT,
    ID_IP_INPUT,
    ID_ROLE_INPUT,
)


@pytest.mark.asyncio
async def test_add_host_only_ip(engine: Engine, load_mock_config: AppConfig):
    app = DbHostsApp(load_mock_config, engine)
    add_host_keybind = load_mock_config.keybindings["add_host"]

    async with app.run_test() as pilot:
        await pilot.press(add_host_keybind)
        await select_input_and_enter_text(pilot, f"#{ID_IP_INPUT}", IP_TEST_VALUE)
        await pilot.click(f"#{ID_CONFIRM_BUTTON}")

    assert get_hosts(engine) == [Host(1, ip=IP_TEST_VALUE)]


@pytest.mark.asyncio
async def test_add_host_only_half(engine: Engine, load_mock_config: AppConfig):
    app = DbHostsApp(load_mock_config, engine)
    add_host_keybind = load_mock_config.keybindings["add_host"]

    async with app.run_test() as pilot:
        await pilot.press(add_host_keybind)
        await select_input_and_enter_text(pilot, f"#{ID_IP_INPUT}", IP_TEST_VALUE)
        await select_input_and_enter_text(
            pilot, f"#{ID_HOSTNAME_INPUT}", HOSTNAME_TEST_VALUE
        )
        await pilot.click(f"#{ID_CONFIRM_BUTTON}")

    assert get_hosts(engine) == [
        Host(1, ip=IP_TEST_VALUE, hostname=HOSTNAME_TEST_VALUE)
    ]


@pytest.mark.asyncio
async def test_add_host_full(engine: Engine, load_mock_config: AppConfig):
    app = DbHostsApp(load_mock_config, engine)
    add_host_keybind = load_mock_config.keybindings["add_host"]

    async with app.run_test() as pilot:
        await pilot.press(add_host_keybind)
        await select_input_and_enter_text(pilot, f"#{ID_IP_INPUT}", IP_TEST_VALUE)
        await select_input_and_enter_text(
            pilot, f"#{ID_HOSTNAME_INPUT}", HOSTNAME_TEST_VALUE
        )
        await select_input_and_enter_text(pilot, f"#{ID_ROLE_INPUT}", ROLE_TEST_VALUE)
        await pilot.click(f"#{ID_CONFIRM_BUTTON}")

    assert get_hosts(engine) == [
        Host(1, ip=IP_TEST_VALUE, hostname=HOSTNAME_TEST_VALUE, role=ROLE_TEST_VALUE)
    ]


@pytest.mark.skipif(sys.platform.startswith("win"), reason="require Linux")
@pytest.mark.asyncio
async def test_add_and_set_host_full(engine: Engine, load_mock_config: AppConfig):
    app = DbHostsApp(load_mock_config, engine)
    add_host_keybind = load_mock_config.keybindings["add_host"]

    async with app.run_test() as pilot:
        await pilot.press(add_host_keybind)
        await select_input_and_enter_text(pilot, f"#{ID_IP_INPUT}", IP_TEST_VALUE)
        await select_input_and_enter_text(
            pilot, f"#{ID_HOSTNAME_INPUT}", HOSTNAME_TEST_VALUE
        )
        await select_input_and_enter_text(pilot, f"#{ID_ROLE_INPUT}", ROLE_TEST_VALUE)
        await pilot.click(f"#{ID_CONFIRM_BUTTON}")

    host = Host(1, ip=IP_TEST_VALUE, hostname=HOSTNAME_TEST_VALUE, role=ROLE_TEST_VALUE)

    assert get_hosts(engine) == [host]

    write_host_in_profile(host, load_mock_config)
    command_output = subprocess.run(
        [
            "bash",
            "-c",
            f"source {load_mock_config.paths.profile_sh_path} && echo $IP $TARGET $DC_HOST",
        ],
        stdout=subprocess.PIPE,
    )
    envs = command_output.stdout.decode("utf8")

    assert IP_TEST_VALUE in envs
    assert HOSTNAME_TEST_VALUE in envs
    assert ROLE_TEST_VALUE in envs


@pytest.mark.asyncio
async def test_add_host_empty(engine: Engine, load_mock_config: AppConfig):
    app = DbHostsApp(load_mock_config, engine)
    add_host_keybind = load_mock_config.keybindings["add_host"]
    async with app.run_test() as pilot:
        await pilot.press(add_host_keybind)
        await pilot.click(f"#{ID_CONFIRM_BUTTON}")
    assert get_hosts(engine) == [Host(1)]


@pytest.mark.asyncio
async def test_add_host_existing(engine: Engine, load_mock_config: AppConfig):
    app = DbHostsApp(load_mock_config, engine)
    add_host_keybind = load_mock_config.keybindings["add_host"]
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
        await pilot.press(add_host_keybind)
        await select_input_and_enter_text(pilot, f"#{ID_IP_INPUT}", IP_TEST_VALUE)
        await select_input_and_enter_text(
            pilot, f"#{ID_HOSTNAME_INPUT}", HOSTNAME_TEST_VALUE
        )
        await select_input_and_enter_text(
            pilot, f"#{ID_ROLE_INPUT}", ROLE_TEST_VALUE + "2"
        )
        await pilot.click(f"#{ID_CONFIRM_BUTTON}")
        assert get_hosts(engine) == [
            Host(
                1,
                ip=IP_TEST_VALUE,
                hostname=HOSTNAME_TEST_VALUE,
                role=ROLE_TEST_VALUE + "2",
            )
        ]


@pytest.mark.asyncio
async def test_add_host_issue_3(engine: Engine, load_mock_config: AppConfig):
    app = DbHostsApp(load_mock_config, engine)
    add_host_keybind = load_mock_config.keybindings["add_host"]

    async with app.run_test() as pilot:
        await pilot.press(add_host_keybind)
        await pilot.press(add_host_keybind)
        await select_input_and_enter_text(pilot, f"#{ID_IP_INPUT}", IP_TEST_VALUE)
        await pilot.click(f"#{ID_CONFIRM_BUTTON}")

    assert get_hosts(engine) == [Host(1, ip=IP_TEST_VALUE)]

@pytest.mark.asyncio
async def test_add_host_existing_no_role_keeps_role(
    engine: Engine, load_mock_config: AppConfig
):
    app = DbHostsApp(load_mock_config, engine)
    add_host_keybind = load_mock_config.keybindings["add_host"]

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

        await pilot.press(add_host_keybind)
        await select_input_and_enter_text(pilot, f"#{ID_IP_INPUT}", IP_TEST_VALUE)
        await select_input_and_enter_text(
            pilot, f"#{ID_HOSTNAME_INPUT}", HOSTNAME_TEST_VALUE
        )
        await pilot.click(f"#{ID_CONFIRM_BUTTON}")

    assert get_hosts(engine) == [
        Host(
            1,
            ip=IP_TEST_VALUE,
            hostname=HOSTNAME_TEST_VALUE,
            role=ROLE_TEST_VALUE,
        )
    ]