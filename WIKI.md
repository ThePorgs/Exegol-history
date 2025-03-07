## 📖 Usage

### Credentials
Add a credential:
```
exegol-history add creds -u 'Administrator' -p 'Passw0rd!'
```

Add a credential with a hash and a domain:
```
exegol-history add creds -u 'Administrator' -p 'Passw0rd!' -H 'FC525C9683E8FE067095BA2DDC971889' -d 'test.local'
```

Add multiple credentials from a CSV file:
```
exegol-history add creds --file creds.csv --file-type CSV
```

Get a specific credential in JSON format:
```
exegol-history get creds -u 'Administrator' --json
```

Get all credentials in TXT format:
```
exegol-history get creds --txt
```

Delete a credential:
```
exegol-history del creds -u 'Administrator'
```

### Hosts
Add a host:
```
exegol-history add hosts --ip '127.0.0.1'
```

Add a host with a hostname and a role:
```
exegol-history add hosts --ip '127.0.0.1' -n 'dc.test.local' -r 'DC'
```

Add multiple hosts from a CSV file:
```
exegol-history add hosts --file hosts.csv --file-type CSV
```

Get a specific host in JSON format:
```
exegol-history get hosts --ip '127.0.0.1'
```

Get all hosts in CSV format:
```
exegol-history get hosts --csv
```

Delete a credential:
```
exegol-history del hosts --ip '127.0.0.1'
```