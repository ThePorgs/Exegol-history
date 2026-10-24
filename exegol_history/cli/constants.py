# Lightweight module: must only import the standard library.
# It is imported on every invocation (including shell tab-completion),
# so keeping it free of textual / sqlalchemy / pykeepass keeps startup fast.

CREDS_SUBCOMMAND = "creds"
HOSTS_SUBCOMMAND = "hosts"
KRB_SUBCOMMAND = "krb"
ALL_SUBCOMMAND = "all"
VERSION_SUBCOMMAND = "version"
ADD_SUBCOMMAND = "add"
IMPORT_SUBCOMMAND = "import"
EDIT_SUBCOMMAND = "edit"
EXPORT_SUBCOMMAND = "export"
SET_SUBCOMMAND = "set"
UNSET_SUBCOMMAND = "unset"
SHOW_SUBCOMMAND = "show"
DELETE_SUBCOMMAND = "rm"
SYNC_SUBCOMMAND = "sync"
