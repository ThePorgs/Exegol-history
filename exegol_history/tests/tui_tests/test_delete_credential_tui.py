import pytest

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


@pytest.mark.asyncio
async def test_delete_credential_tui(open_keepass: PyKeePass, load_mock_config):
    config = load_mock_config
    kp = open_keepass
    app = DbCredsApp(config, kp)

    async with app.run_test() as pilot:
        await pilot.press("f4")
        await select_input_and_enter_text(pilot, "#username", USERNAME_TEST_VALUE)
        await pilot.click("#confirm_add")

        credentials = get_credentials(kp)

        assert credentials == [("1", USERNAME_TEST_VALUE, "", "", "")]

        await pilot.press("f5")
        await pilot.click("#confirm")

        credentials = get_credentials(kp)

        assert len(credentials) == 0


@pytest.mark.asyncio
async def test_delete_credential_full_tui(open_keepass: PyKeePass, load_mock_config):
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
            (
                "1",
                USERNAME_TEST_VALUE,
                PASSWORD_TEST_VALUE,
                HASH_TEST_VALUE,
                DOMAIN_TEST_VALUE,
            )
        ]

        await pilot.press("f5")
        await pilot.click("#confirm")

        credentials = get_credentials(kp)

        assert len(credentials) == 0


@pytest.mark.asyncio
async def test_delete_credential_not_exist_tui(
    open_keepass: PyKeePass, load_mock_config
):
    config = load_mock_config
    kp = open_keepass
    app = DbCredsApp(config, kp)

    async with app.run_test() as pilot:
        await pilot.press("f5")
        await pilot.click("#confirm")

    credentials = get_credentials(kp)

    assert len(credentials) == 0


@pytest.mark.asyncio
async def test_delete_credential_tui_issue_3(open_keepass: PyKeePass, load_mock_config):
    config = load_mock_config
    kp = open_keepass
    app = DbCredsApp(config, kp)

    async with app.run_test() as pilot:
        await pilot.press("f5")
        await pilot.press("f5")
        await pilot.click("#confirm")
