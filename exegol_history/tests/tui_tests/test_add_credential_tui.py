import pytest
import os

from exegol_history.tui.db_creds.db_creds import DbCredsApp
from exegol_history.db_api.creds import get_credentials
from common_tui import (
    USERNAME_TEST_VALUE,
    PASSWORD_TEST_VALUE,
    HASH_TEST_VALUE,
    DOMAIN_TEST_VALUE,
    select_input_and_enter_text,
)
from pykeepass import PyKeePass
from typing import Any


@pytest.mark.asyncio
async def test_add_credential_import_csv_tui(
    open_keepass: PyKeePass, load_mock_config: dict[str, Any]
):
    config = load_mock_config
    kp = open_keepass
    app = DbCredsApp(config, kp)

    async with app.run_test() as pilot:
        await pilot.press("f4")

        # Switch tab
        await pilot.press("right")

        await select_input_and_enter_text(
            pilot,
            "#file_textarea",
            f"{USERNAME_TEST_VALUE},{PASSWORD_TEST_VALUE},{HASH_TEST_VALUE},{DOMAIN_TEST_VALUE}",
        )

        await pilot.click("#file_type_select")
        await pilot.press("down")
        await pilot.press("down")
        await pilot.press("enter")

        await pilot.click("#confirm_import")

    credentials = get_credentials(kp)

    assert credentials == [
        (USERNAME_TEST_VALUE, PASSWORD_TEST_VALUE, HASH_TEST_VALUE, DOMAIN_TEST_VALUE)
    ]


@pytest.mark.asyncio
async def test_add_credential_import_csv_file_tui(
    open_keepass: PyKeePass, load_mock_config: dict[str, Any]
):
    config = load_mock_config
    kp = open_keepass
    app = DbCredsApp(config, kp)

    async with app.run_test() as pilot:
        await pilot.press("f4")

        # Switch tab
        await pilot.press("right")

        await pilot.click("#import_file")
        pilot.app.query_one("#label_selected_path").update(
            os.path.dirname(os.path.abspath(__file__)) + "/../artifacts/creds.txt"
        )
        await pilot.click("#select_button")

        await pilot.click("#file_type_select")
        await pilot.press("down")
        await pilot.press("down")
        await pilot.press("enter")

        await pilot.click("#confirm_import")

    credentials = get_credentials(kp)

    assert credentials == [
        (USERNAME_TEST_VALUE, PASSWORD_TEST_VALUE, HASH_TEST_VALUE, DOMAIN_TEST_VALUE)
    ]


@pytest.mark.asyncio
async def test_add_credential_only_username_tui(
    open_keepass: PyKeePass, load_mock_config: dict[str, Any]
):
    config = load_mock_config
    kp = open_keepass
    app = DbCredsApp(config, kp)

    async with app.run_test() as pilot:
        await pilot.press("f4")
        await select_input_and_enter_text(pilot, "#username", USERNAME_TEST_VALUE)
        await pilot.click("#confirm_add")

    credentials = get_credentials(kp)

    assert credentials == [(USERNAME_TEST_VALUE, "", "", "")]


@pytest.mark.asyncio
async def test_add_credential_half_tui(
    open_keepass: PyKeePass, load_mock_config: dict[str, Any]
):
    config = load_mock_config
    kp = open_keepass
    app = DbCredsApp(config, kp)

    async with app.run_test() as pilot:
        await pilot.press("f4")
        await select_input_and_enter_text(pilot, "#username", USERNAME_TEST_VALUE)
        await select_input_and_enter_text(pilot, "#hash", HASH_TEST_VALUE)
        await pilot.click("#confirm_add")

    credentials = get_credentials(kp)

    assert credentials == [(USERNAME_TEST_VALUE, "", HASH_TEST_VALUE, "")]


@pytest.mark.asyncio
async def test_add_credential_full_tui(
    open_keepass: PyKeePass, load_mock_config: dict[str, Any]
):
    config = load_mock_config
    kp = open_keepass
    app = DbCredsApp(config, kp)

    async with app.run_test() as pilot:
        await pilot.press("f4")
        await select_input_and_enter_text(pilot, "#username", USERNAME_TEST_VALUE)
        await select_input_and_enter_text(pilot, "#password", PASSWORD_TEST_VALUE)
        await select_input_and_enter_text(pilot, "#hash", HASH_TEST_VALUE)
        await select_input_and_enter_text(pilot, "#domain", DOMAIN_TEST_VALUE)
        await pilot.click("#confirm_add")

    credentials = get_credentials(kp)

    assert credentials == [
        (USERNAME_TEST_VALUE, PASSWORD_TEST_VALUE, HASH_TEST_VALUE, DOMAIN_TEST_VALUE)
    ]


@pytest.mark.asyncio
async def test_add_credential_empty_tui(
    open_keepass: PyKeePass, load_mock_config: dict[str, Any]
):
    config = load_mock_config
    kp = open_keepass
    app = DbCredsApp(config, kp)

    async with app.run_test() as pilot:
        await pilot.press("f4")
        await pilot.click("#confirm_add")

    credentials = get_credentials(kp)

    assert len(credentials) == 0


@pytest.mark.asyncio
async def test_add_credential_existing_tui(
    open_keepass: PyKeePass, load_mock_config: dict[str, Any]
):
    config = load_mock_config
    kp = open_keepass
    app = DbCredsApp(config, kp)

    async with app.run_test() as pilot:
        await pilot.press("f4")
        await select_input_and_enter_text(pilot, "#username", USERNAME_TEST_VALUE)
        await select_input_and_enter_text(pilot, "#hash", HASH_TEST_VALUE)
        await pilot.click("#confirm_add")

        credentials = get_credentials(kp)

        assert credentials == [(USERNAME_TEST_VALUE, "", HASH_TEST_VALUE, "")]

        await pilot.press("f4")
        await select_input_and_enter_text(pilot, "#username", USERNAME_TEST_VALUE)
        await select_input_and_enter_text(pilot, "#password", PASSWORD_TEST_VALUE)
        await select_input_and_enter_text(pilot, "#hash", HASH_TEST_VALUE)
        await select_input_and_enter_text(pilot, "#domain", DOMAIN_TEST_VALUE)
        await pilot.click("#confirm_add")

    credentials = get_credentials(kp)

    assert credentials == [
        (USERNAME_TEST_VALUE, PASSWORD_TEST_VALUE, HASH_TEST_VALUE, DOMAIN_TEST_VALUE)
    ]


@pytest.mark.asyncio
async def test_add_credential_issue_3(
    open_keepass: PyKeePass, load_mock_config: dict[str, Any]
):
    config = load_mock_config
    kp = open_keepass
    app = DbCredsApp(config, kp)

    async with app.run_test() as pilot:
        await pilot.press("f4")
        await pilot.press("f4")
        await select_input_and_enter_text(pilot, "#username", USERNAME_TEST_VALUE)
        await pilot.click("#confirm_add")

    credentials = get_credentials(kp)

    assert credentials == [(USERNAME_TEST_VALUE, "", "", "")]
