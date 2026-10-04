import os
import re
import shutil
import subprocess
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from typing import Optional

# Common extensions used for Kerberos CCACHE tickets.
CCACHE_EXTENSIONS = (".ccache")


class Ticket:
    """
    Represents a Kerberos CCACHE ticket found on disk.

    ``describe_output`` caches the output of describeTicket.py so it only has to
    be computed once (at scan / refresh time) rather than every time the ticket
    is highlighted in the TUI. It is intentionally kept out of __iter__ and
    __eq__ so it does not become a table column nor affect ticket identity.
    """

    def __init__(
        self,
        path: str,
        username: Optional[str] = None,
        domain: Optional[str] = None,
        describe_output: Optional[str] = None,
    ):
        self.path = str(path)
        self.username = username
        self.domain = domain
        self.describe_output = describe_output

    def __eq__(self, value) -> bool:
        return (
            isinstance(value, Ticket)
            and self.path == value.path
            and self.username == value.username
            and self.domain == value.domain
        )

    def __repr__(self) -> str:
        return (
            f"Ticket(path={self.path}, username={self.username}, domain={self.domain})"
        )

    def __iter__(self):
        return iter([self.path, self.username, self.domain])


def scan_ccache_tickets(search_paths: list[str], search_depth: int = 3) -> list[Ticket]:
    """
    Recursively scan the provided paths for Kerberos CCACHE tickets up to the
    given depth.

    The depth is relative to each scanned path: a depth of 0 only looks at files
    directly inside the path, a depth of 1 also looks one directory deeper, etc.

    The walk is pruned at ``search_depth`` so heavy out-of-scope directories
    (node_modules, .git, loot dumps, ...) are never descended into, and it relies
    on os.walk/os.scandir to avoid a stat() syscall per candidate. Directory
    symlinks are not followed, which also protects against symlink loops.
    """
    tickets: list[Ticket] = []
    seen: set[str] = set()

    for raw_path in search_paths:
        base = os.path.expanduser(raw_path)

        if not os.path.isdir(base):
            continue

        base_depth = base.rstrip(os.sep).count(os.sep)

        # onerror swallows permission errors / broken entries like the previous
        # implementation did with its OSError guard.
        for dirpath, dirnames, filenames in os.walk(base, onerror=lambda _: None):
            # Prune: stop descending once we have reached the configured depth.
            if dirpath.count(os.sep) - base_depth >= search_depth:
                dirnames[:] = []

            for name in filenames:
                # Cheap filename check first, before touching the filesystem.
                if not name.lower().endswith(CCACHE_EXTENSIONS):
                    continue

                full_path = os.path.join(dirpath, name)
                if full_path in seen:
                    continue

                seen.add(full_path)
                tickets.append(Ticket(full_path))

    # Deterministic order makes the TUI and the tests predictable.
    tickets.sort(key=lambda ticket: ticket.path)

    return tickets


def describe_ticket(
    ticket_path: str, describe_ticket_command: str = "describeTicket.py"
) -> str:
    """
    Run Impacket's describeTicket.py on the given ticket and return its output.
    """
    try:
        result = subprocess.run(
            [describe_ticket_command, ticket_path],
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            check=False,
        )
    except FileNotFoundError:
        return (
            f"'{describe_ticket_command}' was not found, is Impacket installed and "
            "available in the PATH?"
        )

    return result.stdout.decode("utf-8", errors="replace")


def parse_ticket_identity(describe_output: str) -> tuple[Optional[str], Optional[str]]:
    """
    Extract the username and domain from describeTicket.py output.

    describeTicket.py prints a line such as:
        User Name                 : john
        User Realm                : DOMAIN.LOCAL
    """
    username = None
    domain = None

    username_match = re.search(r"User Name\s*:\s*(\S+)", describe_output)
    if username_match:
        username = username_match.group(1)

    domain_match = re.search(r"User Realm\s*:\s*(\S+)", describe_output)
    if domain_match:
        domain = domain_match.group(1)

    return username, domain


def describe_and_enrich_tickets(
    tickets: list[Ticket],
    describe_ticket_command: str = "describeTicket.py",
    max_workers: int = 8,
) -> list[Ticket]:
    """
    Run describeTicket.py on every ticket once and cache the result on the ticket
    (``describe_output``), along with the username / domain parsed from it.

    This is meant to be called at scan / refresh time so the TUI never has to run
    describeTicket.py live while the user moves the cursor around. Tickets are
    described concurrently since each call spawns an independent, I/O-bound
    subprocess.
    """
    if not tickets:
        return tickets

    def _describe(ticket: Ticket) -> None:
        output = describe_ticket(ticket.path, describe_ticket_command)
        ticket.describe_output = output
        username, domain = parse_ticket_identity(output)
        ticket.username = username
        ticket.domain = domain

    workers = max(1, min(max_workers, len(tickets)))
    with ThreadPoolExecutor(max_workers=workers) as executor:
        # list() forces every future to complete (and re-raises any exception).
        list(executor.map(_describe, tickets))

    return tickets


def convert_ticket(
    input_path: str,
    output_path: str,
    ticket_converter_command: str = "ticketConverter.py",
) -> str:
    """
    Convert a ticket using Impacket's ticketConverter.py.

    The conversion direction is inferred by the tool itself based on the input
    file format (ccache <-> kirbi).
    """
    try:
        result = subprocess.run(
            [ticket_converter_command, input_path, output_path],
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            check=False,
        )
    except FileNotFoundError:
        raise RuntimeError(
            f"'{ticket_converter_command}' was not found, is Impacket installed and "
            "available in the PATH?"
        )

    if result.returncode != 0:
        raise RuntimeError(result.stdout.decode("utf-8", errors="replace"))

    return result.stdout.decode("utf-8", errors="replace")


def kirbi_output_path(ticket_path: str) -> str:
    """
    Compute a sensible .kirbi output path from a ccache ticket path.
    """
    return str(Path(ticket_path).with_suffix(".kirbi"))


def is_tool_available(command: str) -> bool:
    """
    Return True if the given command is available in the PATH.
    """
    return shutil.which(command) is not None
