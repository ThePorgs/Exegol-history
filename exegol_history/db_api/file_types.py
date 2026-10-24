# Lightweight module: only the standard library, so argparse can build its
# choices without importing sqlalchemy / pykeepass.
from enum import Enum


class CredsImportFileType(Enum):
    CSV = 1
    JSON = 2
    KDBX = 3
    PYPYKATZ_JSON = 4
    SECRETSDUMP = 5


class HostsImportFileType(Enum):
    CSV = 1
    JSON = 2


class CredsExportFileType(Enum):
    CSV = 1
    JSON = 2


class HostsExportFileType(Enum):
    CSV = 1
    JSON = 2
