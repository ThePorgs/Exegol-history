#info: this file is used by the exegol-history.py utility. Exegol terminals source it to export env vars
variables=("INTERFACE" "DOMAIN" "DOMAIN_SID" "USER" "PASSWORD" "NT_HASH" "KRB5CCNAME" "DC_IP" "DC_HOST" "DB_HOSTNAME" "ROLE" "TARGET" "IP" "ATTACKER_IP")

for var in "${variables[@]}"; do
    value=$(cat "/opt/tools/Exegol-history/exh_data.json" | jq -r ".$var")
    if [[ "$value" == "null" ]]; then
        unset "$var"
    else
        export "$var=$value"
    fi
done