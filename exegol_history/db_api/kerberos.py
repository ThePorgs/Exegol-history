import os
import re
import subprocess
from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass, field
from pathlib import Path

CCACHE_PREFIX = "krb5cc_"
CCACHE_EXTENSIONS = ".ccache"


@dataclass
class Ticket:
    """A Kerberos CCACHE ticket found on disk.

    describe_output caches describeTicket.py's output, computed once at scan /
    refresh time. It is neither a table column nor part of the ticket identity.
    """

    path: str
    username: str | None = None
    domain: str | None = None
    describe_output: str | None = field(default=None, compare=False, repr=False)

    def __post_init__(self):
        self.path = str(self.path)

    def __iter__(self):
        return iter((self.path, self.username, self.domain))


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
                lower_name = name.lower()
                # Cheap filename check first, before touching the filesystem.
                if not lower_name.startswith(CCACHE_PREFIX) and not lower_name.endswith(
                    CCACHE_EXTENSIONS
                ):
                    continue

                full_path = os.path.join(dirpath, name)
                if full_path in seen:
                    continue

                seen.add(full_path)
                tickets.append(Ticket(full_path))

    # Deterministic order makes the TUI and the tests predictable.
    tickets.sort(key=lambda ticket: ticket.path)

    return tickets


def run_impacket_tool(command: str, *args: str) -> tuple[int, str]:
    try:
        result = subprocess.run(
            [command, *args],
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            check=False,
        )
    except FileNotFoundError:
        raise RuntimeError(
            f"'{command}' was not found, is Impacket installed and available in the PATH?"
        )

    return result.returncode, result.stdout.decode("utf-8", errors="replace")


def describe_ticket(
    ticket_path: str, describe_ticket_command: str = "describeTicket.py"
) -> str:
    """Run Impacket's describeTicket.py on the given ticket and return its output."""
    try:
        return run_impacket_tool(describe_ticket_command, ticket_path)[1]
    except RuntimeError as e:
        return str(e)


def parse_ticket_identity(describe_output: str) -> tuple[str | None, str | None]:
    def value_of(label: str) -> str | None:
        match = re.search(rf"{label}\s*:\s*(\S+)", describe_output)
        return match.group(1) if match else None

    return value_of("User Name"), value_of("User Realm")


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
        ticket.describe_output = describe_ticket(ticket.path, describe_ticket_command)
        ticket.username, ticket.domain = parse_ticket_identity(ticket.describe_output)

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
    returncode, output = run_impacket_tool(
        ticket_converter_command, input_path, output_path
    )

    if returncode != 0:
        raise RuntimeError(output)

    return output


def kirbi_output_path(ticket_path: str) -> str:
    """
    Compute a sensible .kirbi output path from a ccache ticket path.
    """
    return str(Path(ticket_path).with_suffix(".kirbi"))
