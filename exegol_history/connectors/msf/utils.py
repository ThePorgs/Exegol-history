import yaml

from enum import Enum

MSF_DB_CONFIG_PATH = "/var/lib/postgresql/.msf4/database.yml"
MSF_DB_CREDENTIAL_QUERY = """
SELECT metasploit_credential_cores.id, username, COALESCE(data, ''), COALESCE(metasploit_credential_privates.type, ''), COALESCE(metasploit_credential_realms.value, '')
FROM metasploit_credential_cores 
LEFT JOIN metasploit_credential_publics ON metasploit_credential_cores.public_id=metasploit_credential_publics.id 
LEFT JOIN metasploit_credential_privates ON metasploit_credential_cores.private_id=metasploit_credential_privates.id
LEFT JOIN metasploit_credential_realms ON metasploit_credential_cores.realm_id=metasploit_credential_realms.id;
"""
MSF_DB_HOST_QUERY = """
SELECT id, address FROM hosts;
"""


# Ref: https://github.com/rapid7/metasploit-framework/blob/a4297329d73f2d244dd83e632864f9efc753b6c4/lib/msf/core/web_services/documentation/api/v1/credential_api_doc.rb#L42
class MetasploitCredentialType(str, Enum):
    ReplayableHash = "Metasploit::Credential::ReplayableHash"
    NonreplayableHash = "Metasploit::Credential::NonreplayableHash"
    NTLMHash = "Metasploit::Credential::NTLMHash"
    Password = "Metasploit::Credential::Password"
    PasswordHash = "Metasploit::Credential::PasswordHash"
    SSHKey = "Metasploit::Credential::SSHKey"
    PostgresMD5 = "Metasploit::Credential::PostgresMD5"


def is_private_data_hash(private_data_type: str):
    return private_data_type in [
        MetasploitCredentialType.NonreplayableHash,
        MetasploitCredentialType.NTLMHash,
        MetasploitCredentialType.PasswordHash,
        MetasploitCredentialType.PostgresMD5,
        MetasploitCredentialType.ReplayableHash,
    ]


def get_msf_postgres_db_infos(msf_db_config_path: str) -> (str, str):
    with open(msf_db_config_path, "rb") as msf_config:
        msf_config_yml = yaml.safe_load(msf_config)
        database = msf_config_yml["development"]["database"]
        port = msf_config_yml["development"]["port"]
        username = msf_config_yml["development"]["username"]
        password = msf_config_yml["development"]["password"]

    return (database, port, username, password)
