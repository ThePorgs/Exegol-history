# 📂 Exegol-history
Exegol-history is a tool to quickly store and retrieve compromised credentials and hosts; the goal is to ease the management of credentials and hosts during a penetration testing engagement or a CTF.

Once an asset is selected from the TUI, the information can be accessed through environment variables and doesn't need to be typed over and over.

There is a shell wrapper provided to manipulate environment variables. You can find it in the `exegol-history.sh` file.

## ✨ Features
- Add / edit / delete credentials and hosts informations trough a CLI or a TUI
- Import file in various format (CSV, Pypykatz, ...)
- Keybinds customisation


## 🖼️ Screenshots
The TUI (Terminal User Interface):
![](screenshots/screenshot01.png)

![](screenshots/screenshot02.png)

![](screenshots/screenshot03.png)

A typical workflow with `Exegol-history`:
![](screenshots/screenshot04.png)

## ⚙️ Install
```
# without the wrapper
pipx install git+https://github.com/ThePorgs/exegol-history

# with the wrapper
git clone https://github.com/ThePorgs/exegol-history
alias exegol-history='source /PATH/TO/Exegol-history/exegol-history.sh'
```

## 📝 Configuration
A small configuration file can be used to customise the database name and keybinds for the TUI:
```toml
[paths]
db_name = "DB.kdbx"
db_key_name = "db.key"

[keybindings]
copy_username_clipboard = "f1"
copy_password_clipboard = "f2"
copy_hash_clipboard = "f3"
add_credential = "f4"
delete_credential = "f5"
edit_credential = "f6"
copy_ip_clipboard = "f1"
copy_hostname_clipboard = "f2"
add_host = "f3"
delete_host = "f4"
edit_host = "f5"
quit = "ctrl+c"
```

**The configuration file must be in the home folder, in a `.exegol-history` folder.**


## Tips & tricks

To see which user you are currently using, you can add the `USER` environnment variable in your prompt, for example with [Starship](https://github.com/starship/starship):
```toml
[env_var]
variable = "USER"
default = ''
style = "fg:bold red bg:#477069"
format = '[  $env_value ]($style)'
```

## Using the wrapper

```sh
# Interactively select creds and export them
exegol-history export creds

# Show the current env vars
exegol-history env
```

## Using the CLI

```sh
# Add a credential:
exegol-history.py add creds -u 'Administrator' -p 'Passw0rd!'

# Add a credential with a hash and a domain:
exegol-history.py add creds -u 'Administrator' -p 'Passw0rd!' -H 'FC525C9683E8FE067095BA2DDC971889' -d 'test.local'

# Add multiple credentials from a CSV file:
exegol-history.py add creds --file creds.csv --file-type CSV

# Get a specific credential in JSON format:
exegol-history.py get creds -u 'Administrator' --json

# Get all credentials in TXT format:
exegol-history.py get creds --txt

# Delete a credential:
exegol-history.py del creds -u 'Administrator'

# Add a host:
exegol-history.py add hosts --ip '127.0.0.1'

# Add a host with a hostname and a role:
exegol-history.py add hosts --ip '127.0.0.1' -n 'dc.test.local' -r 'DC'

# Add multiple hosts from a CSV file:
exegol-history.py add hosts --file hosts.csv --file-type CSV

# Get a specific host in JSON format:
exegol-history.py get hosts --ip '127.0.0.1'

# Get all hosts in CSV format:
exegol-history.py get hosts --csv

# Delete a credential:
exegol-history.py del hosts --ip '127.0.0.1'
```

## 🛠️ Development

### Running tests
```
poetry run pytest
```
