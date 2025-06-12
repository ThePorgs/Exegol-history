# 📂 Exegol-history
Exegol-history is a tool to quickly store and retrieve compromised credentials and hosts; the goal is to ease the management of credentials and hosts during a penetration testing engagement or a CTF.

Once an asset is selected from the TUI, the information can be accessed through environment variables and doesn't need to be typed over and over.

## ✨ Features
- Add / edit / delete credentials and hosts informations trough a CLI or a TUI
- Import / export in various format (CSV, Pypykatz, ...)
- Keybinds customisation

## 🖼️ Screenshots
The TUI (Terminal User Interface):
![](screenshots/screenshot01.png)

![](screenshots/screenshot02.png)

![](screenshots/screenshot03.png)

A typical workflow with `Exegol-history`:
![](screenshots/screenshot04.png)

## ⚙️ Install
`Exegol-history` is already installed in an Exegol container, however you can install it manually:
```sh
# Using `pipx`
pipx install git+https://github.com/ThePorgs/exegol-history

# Using `uv`
uv tool install git+https://github.com/ThePorgs/Exegol-history
```

Then you can create a function to run `Exegol-history` and add it to your `.zshrc` file:
```sh
echo 'function exh { exegol-history "$@" && exec zsh }' >> ~/.zshrc
```

## 📝 Configuration
A small configuration file `config.toml` can be used to customise the database name and keybinds for the TUI:
```toml
[paths]
db_name = "DB.kdbx"
db_key_name = "db.key"
profile_sh_path = "/opt/tools/Exegol-history/profile.sh"

[keybindings]
copy_username_clipboard = "f1"
copy_password_clipboard = "f2"
copy_hash_clipboard = "f3"
add_credential = "f4"
delete_credential = "f5"
edit_credential = "f6"
export_credential = "f7"
copy_ip_clipboard = "f1"
copy_hostname_clipboard = "f2"
add_host = "f3"
delete_host = "f4"
edit_host = "f5"
export_host = "f6"
quit = "ctrl+c"
```

**The configuration file must be in the home folder, in a `.exegol-history` folder.**

## 💡 Tips & tricks
### 🗨️ Prompt
To see which user you are currently using, you can add the `USER` environnment variable in your prompt, for example with [Starship](https://github.com/starship/starship):
```toml
[env_var]
variable = "USER"
default = ''
style = "fg:bold red bg:#477069"
format = '[  $env_value ]($style)'
```

if you are inside an `Exegol` container, the prompt should already be configured. 

### ⌨️ Keybind
You can add a keybind that will automatically type the command to launch the **Exegol-history** TUI, for example using the [Kitty](https://github.com/kovidgoyal/kitty) terminal, you can add a keybind like this:
```
map ctrl+u 'remote_control send-text "exh set creds\\n"'
```
pushing the **ctrl+u** key combination should automatically open the TUI without having to type `exh set creds`.

## 💡 Examples
```sh
# Interactively select a credential
exh set creds

# Show the current environnment variables
exh show

# Add a credential
exh add creds -u 'Administrator' -p 'Passw0rd!'

# Add a credential with a password, a hash and a domain
exh add creds -u 'Administrator' -p 'Passw0rd!' -H 'FC525C9683E8FE067095BA2DDC971889' -d 'test.local'

# Import multiple credentials from a CSV file
exh import creds --file creds.csv --format CSV

# Delete the credential with the id 1
exh rm creds --id 1

# Add a host
exh add hosts --ip '127.0.0.1'

# Add a host with a hostname and a role
exh add hosts --ip '127.0.0.1' -n 'dc.test.local' -r 'DC'

# Import multiple hosts from a CSV file
exh import hosts --file hosts.csv --format CSV

# Export hosts in CSV format
exh export hosts --format CSV

# Delete the host with the id 1
exh rm hosts --id 1
```

## 📥 Importing credential
| Name  | Status |
| ------------- | ------------- |
| CSV | ✅  |
| JSON  | ✅  |
| Keepass KDBX  | ✅  |
| Pypykatz (JSON)  | ✅  |
| Secretsdump  | ✅  |
| Lsassy  | ❌  |
| Masky  | ❌  |
| Gosecretsdump  | ❌  |
| Certsync  | ❌  |
| Dploot  | ❌  |
| PassTheCert  | ❌  |
| Pcredz  | ❌  |

## 📥 Importing hosts
| Name  | Status |
| ------------- | ------------- |
| CSV | ✅  |
| JSON  | ✅  |

## 📤 Exporting credential
| Name  | Status |
| ------------- | ------------- |
| CSV  | ✅  |
| JSON  | ✅  |

## 📤 Exporting hosts
| Name  | Status |
| ------------- | ------------- |
| CSV  | ✅  |
| JSON  | ✅  |

## 🔄 Synchronizing
| Name  | Status |
| ------------- | ------------- |
| Metasploit Database  | 🚧  |
| NetExec  | 🚧  |
| Cobalt Strike  | ❌  |
| Havoc  | ❌  |
| Sliver  | ❌  |
| Bloodhound | ❌  |
| Crackhound  | ❌  |
| DonPAPI  | ❌  |
| Hashcat  | ❌  |

### Running tests
```sh
poetry run pytest
```