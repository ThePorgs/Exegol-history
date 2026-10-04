import subprocess
import sys
import pytest
from pathlib import Path
from unittest.mock import patch
from textual.keys import Keys
from textual.widgets import Static, Input

import exegol_history.db_api.kerberos as kerberos_module
from exegol_history.cli.utils import KERBEROS_VARIABLES, write_kerberos_in_profile
from exegol_history.config.config import AppConfig
from exegol_history.db_api.kerberos import Ticket
from exegol_history.tui.db_kerberos import (
    DbKerberosApp,
    ID_DESCRIBE_STATIC,
)
from exegol_history.tui.widgets.object_datatable import ObjectsDataTable
from common import (
    KRB_DESCRIBE_OUTPUT,
    KRB_DOMAIN_TEST_VALUE,
    KRB_USERNAME_TEST_VALUE,
    TEST_KRB_TICKET1,
)


def patch_describe(**kwargs):
    """
    Patch describeTicket.py invocation at its source module. describe_and_enrich_
    tickets() runs it in worker threads, so patching the db_api symbol with
    patch.object is the reliable target.
    """
    kwargs.setdefault("return_value", KRB_DESCRIBE_OUTPUT)
    return patch.object(kerberos_module, "describe_ticket", **kwargs)


async def test_kerberos_tui_lists_tickets(load_mock_config: AppConfig):
    with patch_describe():
        app = DbKerberosApp(load_mock_config, None)

        async with app.run_test():
            table = app.screen.query_one(ObjectsDataTable)
            # Two .ccache tickets exist in the test artifacts (one nested).
            assert table.row_count == 2


async def test_kerberos_tui_identity_enriched_at_mount(load_mock_config: AppConfig):
    # username / domain are computed eagerly at table creation, so they are
    # present WITHOUT the user having to highlight a row first.
    with patch_describe():
        app = DbKerberosApp(load_mock_config, None)

        async with app.run_test():
            table = app.screen.query_one(ObjectsDataTable)
            usernames = list(table.get_column_at(1))
            domains = list(table.get_column_at(2))
            assert KRB_USERNAME_TEST_VALUE in usernames
            assert KRB_DOMAIN_TEST_VALUE in domains


async def test_kerberos_tui_describe_runs_at_mount_not_on_highlight(
    load_mock_config: AppConfig,
):
    with patch_describe() as mock_describe:
        app = DbKerberosApp(load_mock_config, None)

        async with app.run_test() as pilot:
            # describeTicket.py was run once per ticket at creation time.
            calls_after_mount = mock_describe.call_count
            assert calls_after_mount == 2

            # Moving the cursor around must NOT run describeTicket.py again.
            table = app.screen.query_one(ObjectsDataTable)
            table.focus()
            await pilot.pause()
            await pilot.press(Keys.Down)
            await pilot.pause()
            await pilot.press(Keys.Down)
            await pilot.pause()

            assert mock_describe.call_count == calls_after_mount


async def test_kerberos_tui_describe_panel_shows_cached_output(
    load_mock_config: AppConfig,
):
    with patch_describe():
        app = DbKerberosApp(load_mock_config, None)

        async with app.run_test() as pilot:
            table = app.screen.query_one(ObjectsDataTable)
            table.focus()
            await pilot.pause()
            await pilot.press(Keys.Down)
            await pilot.pause()

            describe_static = app.screen.query_one(f"#{ID_DESCRIBE_STATIC}", Static)
            assert KRB_USERNAME_TEST_VALUE in str(describe_static.render())


async def test_kerberos_tui_refresh_reruns_describe(load_mock_config: AppConfig):
    with patch_describe() as mock_describe:
        app = DbKerberosApp(load_mock_config, None)

        async with app.run_test() as pilot:
            calls_after_mount = mock_describe.call_count
            assert calls_after_mount == 2

            refresh_keybind = load_mock_config.keybindings.get("refresh_tickets", "f3")
            await pilot.press(refresh_keybind)
            await pilot.pause()

            # Refresh rescans and re-describes every ticket.
            assert mock_describe.call_count == calls_after_mount + 2


async def test_kerberos_tui_convert_ticket(load_mock_config: AppConfig):
    with (
        patch_describe(),
        patch(
            "exegol_history.tui.db_kerberos.convert_ticket", return_value="ok"
        ) as mock_convert,
    ):
        app = DbKerberosApp(load_mock_config, None)

        async with app.run_test() as pilot:
            table = app.screen.query_one(ObjectsDataTable)
            table.focus()
            await pilot.pause()
            await pilot.press(Keys.Down)
            await pilot.pause()

            convert_keybind = load_mock_config.keybindings.get("convert_ticket", "f2")
            await pilot.press(convert_keybind)
            await pilot.pause()

            mock_convert.assert_called_once()
            # The output path should be a .kirbi file derived from the ticket.
            output_path = mock_convert.call_args[0][1]
            assert output_path.endswith(".kirbi")


async def test_kerberos_tui_search_filters(load_mock_config: AppConfig):
    with patch_describe():
        app = DbKerberosApp(load_mock_config, None)

        async with app.run_test() as pilot:
            search = app.screen.query_one(Input)
            search.focus()
            await pilot.pause()
            for char in "ticket2":
                await pilot.press(char)
            await pilot.pause()

            table = app.screen.query_one(ObjectsDataTable)
            assert table.row_count == 1


async def test_kerberos_tui_select_ticket_returns_ticket(load_mock_config: AppConfig):
    with patch_describe():
        app = DbKerberosApp(load_mock_config, None)

        async with app.run_test() as pilot:
            table = app.screen.query_one(ObjectsDataTable)
            table.focus()
            await pilot.pause()
            await pilot.press(Keys.Down)
            await pilot.pause()
            await pilot.press(Keys.Enter)

        result = app.return_value
        assert result is not None


@pytest.mark.skipif(sys.platform.startswith("win"), reason="require Linux")
async def test_kerberos_tui_set_in_profile_linux(load_mock_config: AppConfig):
    ticket = Ticket(
        str(TEST_KRB_TICKET1),
        username=KRB_USERNAME_TEST_VALUE,
        domain=KRB_DOMAIN_TEST_VALUE,
    )

    write_kerberos_in_profile(ticket, load_mock_config)

    command_output = subprocess.run(
        [
            "bash",
            "-c",
            f"source {load_mock_config.paths.profile_sh_path} && "
            f"echo ${KERBEROS_VARIABLES[0]} ${KERBEROS_VARIABLES[1]} ${KERBEROS_VARIABLES[2]}",
        ],
        stdout=subprocess.PIPE,
    )
    envs = command_output.stdout.decode("utf8")

    assert KRB_USERNAME_TEST_VALUE in envs
    assert KRB_DOMAIN_TEST_VALUE in envs
    assert Path(str(TEST_KRB_TICKET1)).name in envs
