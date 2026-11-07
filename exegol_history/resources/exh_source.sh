#info: this file is used by the exegol-history.py utility. Exegol terminals source it to export env vars
_exh_file="~/.exegol_history/exh_data.json"
_exh_vars=("INTERFACE" "DOMAIN" "DOMAIN_SID" "USER" "PASSWORD" "NT_HASH" "KRB5CCNAME" "DC_IP" "DC_HOST" "DB_HOSTNAME" "ROLE" "TARGET" "IP" "ATTACKER_IP")

if [[ -r "$_exh_file" ]]; then
    eval "$(jq -r '
        $ARGS.positional[] as $v
        | if has($v) | not then empty
        elif .[$v] == null then "unset \($v)"
        else "export \($v)=\(.[$v] | tostring | @sh)"
        end
    ' "$_exh_file" --args "${_exh_vars[@]}")"
fi

unset _exh_file _exh_vars