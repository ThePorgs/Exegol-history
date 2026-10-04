import subprocess
import sys
import pytest
from pathlib import Path
from unittest.mock import patch, MagicMock

from exegol_history.cli.arguments import parse_arguments
from exegol_history.cli.functions import KRB_SUBCOMMAND, SET_SUBCOMMAND
from exegol_history.cli.utils import KERBEROS_VARIABLES, write_kerberos_in_profile
from exegol_history.config.config import AppConfig
import exegol_history.db_api.kerberos as kerberos_module
from exegol_history.db_api.kerberos import (
    Ticket,
    convert_ticket,
    describe_and_enrich_tickets,
    describe_ticket,
    kirbi_output_path,
    parse_ticket_identity,
    scan_ccache_tickets,
)
from exegol_history.tests.common import (
    KRB_DESCRIBE_OUTPUT,
    KRB_DOMAIN_TEST_VALUE,
    KRB_USERNAME_TEST_VALUE,
    TEST_KERBEROS_ARTIFACTS_PATH,
    TEST_KRB_TICKET1,
    TEST_KRB_TICKET2,
)


def test_parse_set_krb_arguments():
    command_line = f"{SET_SUBCOMMAND} {KRB_SUBCOMMAND}".split()
    args = parse_arguments().parse_args(command_line)

    assert args.command == SET_SUBCOMMAND
    assert args.subcommand == KRB_SUBCOMMAND


def test_scan_ccache_tickets_finds_tickets():
    tickets = scan_ccache_tickets([str(TEST_KERBEROS_ARTIFACTS_PATH)], search_depth=3)

    found_paths = [ticket.path for ticket in tickets]

    assert str(TEST_KRB_TICKET1) in found_paths
    assert str(TEST_KRB_TICKET2) in found_paths


def test_scan_ccache_tickets_ignores_non_ccache():
    tickets = scan_ccache_tickets([str(TEST_KERBEROS_ARTIFACTS_PATH)], search_depth=3)

    found_names = [Path(ticket.path).name for ticket in tickets]

    assert "readme.txt" not in found_names


def test_scan_ccache_tickets_respects_depth(tmp_path):
    base = tmp_path
    (base / "root.ccache").write_bytes(b"x")

    deep = base / "a" / "b" / "c" / "d"
    deep.mkdir(parents=True)
    (deep / "too_deep.ccache").write_bytes(b"x")

    tickets = scan_ccache_tickets([str(base)], search_depth=3)
    names = [Path(ticket.path).name for ticket in tickets]

    assert "root.ccache" in names
    assert "too_deep.ccache" not in names


def test_scan_ccache_tickets_depth_boundary(tmp_path):
    # A ticket exactly at search_depth must be found, one level deeper must not.
    at_depth = tmp_path / "l1" / "l2" / "l3"
    at_depth.mkdir(parents=True)
    (at_depth / "at_depth.ccache").write_bytes(b"x")

    beyond = at_depth / "l4"
    beyond.mkdir()
    (beyond / "beyond.ccache").write_bytes(b"x")

    tickets = scan_ccache_tickets([str(tmp_path)], search_depth=3)
    names = [Path(ticket.path).name for ticket in tickets]

    assert "at_depth.ccache" in names
    assert "beyond.ccache" not in names


@pytest.mark.skipif(sys.platform.startswith("win"), reason="require POSIX symlinks")
def test_scan_ccache_tickets_does_not_follow_dir_symlinks(tmp_path):
    # A directory symlink pointing back up must not be followed (no loop/escape).
    real = tmp_path / "real"
    real.mkdir()
    (real / "real.ccache").write_bytes(b"x")

    target = tmp_path / "outside"
    target.mkdir()
    (target / "outside.ccache").write_bytes(b"x")

    (real / "link").symlink_to(target, target_is_directory=True)

    tickets = scan_ccache_tickets([str(real)], search_depth=3)
    names = [Path(ticket.path).name for ticket in tickets]

    assert "real.ccache" in names
    assert "outside.ccache" not in names


def test_scan_ccache_tickets_deduplicates(tmp_path):
    (tmp_path / "ticket.ccache").write_bytes(b"x")

    tickets = scan_ccache_tickets([str(tmp_path), str(tmp_path)], search_depth=3)

    assert len(tickets) == 1


def test_scan_ccache_tickets_missing_path():
    tickets = scan_ccache_tickets(["/this/path/does/not/exist"], search_depth=3)

    assert tickets == []


def test_parse_ticket_identity():
    username, domain = parse_ticket_identity(KRB_DESCRIBE_OUTPUT)

    assert username == KRB_USERNAME_TEST_VALUE
    assert domain == KRB_DOMAIN_TEST_VALUE


def test_parse_ticket_identity_empty():
    username, domain = parse_ticket_identity("no identity here")

    assert username is None
    assert domain is None


def test_kirbi_output_path():
    assert kirbi_output_path("/workspace/ticket.ccache") == "/workspace/ticket.kirbi"


def test_describe_and_enrich_tickets_fills_cache_and_identity():
    tickets = [Ticket("/tmp/a.ccache"), Ticket("/tmp/b.ccache")]

    with patch.object(
        kerberos_module, "describe_ticket", return_value=KRB_DESCRIBE_OUTPUT
    ) as mock_describe:
        describe_and_enrich_tickets(tickets, "describeTicket.py")

    # describeTicket.py is run exactly once per ticket.
    assert mock_describe.call_count == 2

    for ticket in tickets:
        assert ticket.describe_output == KRB_DESCRIBE_OUTPUT
        assert ticket.username == KRB_USERNAME_TEST_VALUE
        assert ticket.domain == KRB_DOMAIN_TEST_VALUE


def test_describe_and_enrich_tickets_empty():
    with patch.object(kerberos_module, "describe_ticket") as mock_describe:
        result = describe_and_enrich_tickets([], "describeTicket.py")

    assert result == []
    mock_describe.assert_not_called()


def test_describe_and_enrich_tickets_preserves_order():
    tickets = [Ticket(f"/tmp/{i}.ccache") for i in range(20)]

    def fake_describe(path, _command):
        # Return the path so we can check each ticket got its own output.
        return f"User Name : user\nUser Realm : REALM\n# {path}"

    with patch.object(kerberos_module, "describe_ticket", side_effect=fake_describe):
        describe_and_enrich_tickets(tickets, "describeTicket.py")

    for ticket in tickets:
        assert ticket.path in ticket.describe_output


def test_describe_ticket_runs_command():
    mock_result = MagicMock()
    mock_result.stdout = KRB_DESCRIBE_OUTPUT.encode("utf-8")

    with patch(
        "exegol_history.db_api.kerberos.subprocess.run", return_value=mock_result
    ) as mock_run:
        output = describe_ticket(str(TEST_KRB_TICKET1), "describeTicket.py")

    mock_run.assert_called_once()
    called_args = mock_run.call_args[0][0]
    assert called_args == ["describeTicket.py", str(TEST_KRB_TICKET1)]
    assert "User Name" in output


def test_describe_ticket_missing_tool():
    with patch(
        "exegol_history.db_api.kerberos.subprocess.run",
        side_effect=FileNotFoundError(),
    ):
        output = describe_ticket(str(TEST_KRB_TICKET1), "describeTicket.py")

    assert "not be found" in output.lower() or "not found" in output.lower()


def test_convert_ticket_success(tmp_path):
    output_path = str(tmp_path / "ticket.kirbi")
    mock_result = MagicMock()
    mock_result.returncode = 0
    mock_result.stdout = b"[*] converting ccache to kirbi...\n"

    with patch(
        "exegol_history.db_api.kerberos.subprocess.run", return_value=mock_result
    ) as mock_run:
        convert_ticket(str(TEST_KRB_TICKET1), output_path, "ticketConverter.py")

    called_args = mock_run.call_args[0][0]
    assert called_args == ["ticketConverter.py", str(TEST_KRB_TICKET1), output_path]


def test_convert_ticket_failure(tmp_path):
    output_path = str(tmp_path / "ticket.kirbi")
    mock_result = MagicMock()
    mock_result.returncode = 1
    mock_result.stdout = b"error while converting"

    with patch(
        "exegol_history.db_api.kerberos.subprocess.run", return_value=mock_result
    ):
        with pytest.raises(RuntimeError):
            convert_ticket(str(TEST_KRB_TICKET1), output_path, "ticketConverter.py")


def test_convert_ticket_missing_tool(tmp_path):
    output_path = str(tmp_path / "ticket.kirbi")

    with patch(
        "exegol_history.db_api.kerberos.subprocess.run",
        side_effect=FileNotFoundError(),
    ):
        with pytest.raises(RuntimeError):
            convert_ticket(str(TEST_KRB_TICKET1), output_path, "ticketConverter.py")


@pytest.mark.skipif(sys.platform.startswith("win"), reason="require Linux")
def test_write_kerberos_in_profile_linux(load_mock_config: AppConfig):
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
    assert str(TEST_KRB_TICKET1) in envs


@pytest.mark.skipif(sys.platform.startswith("win"), reason="require Linux")
def test_write_kerberos_in_profile_unsets_password_hash_linux(
    load_mock_config: AppConfig,
):
    # First set a password and hash in the profile.
    from exegol_history.cli.utils import write_credential_in_profile
    from exegol_history.db_api.creds import Credential

    write_credential_in_profile(
        Credential(username="old", password="secret", hash="abcd", domain="old.local"),
        load_mock_config,
    )

    # Now set a Kerberos ticket, which should unset PASSWORD and NT_HASH.
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
            f"echo ${KERBEROS_VARIABLES[3]} ${KERBEROS_VARIABLES[4]}",
        ],
        stdout=subprocess.PIPE,
    )
    envs = command_output.stdout.decode("utf8")

    assert envs.strip() == ""
