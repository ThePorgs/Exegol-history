import os
from exegol_history.connectors.nxc.extractors.credentials import (
    NXC_Credentials_Extractor,
)
from exegol_history.connectors.nxc.extractors.users import NXC_Users_Extractor


class NXCWorkspaceSyncer:
    SYNCER_NAME = "nxc"

    def __init__(self, kp, workspaces_dir="~/.nxc/workspaces/"):
        self.workspaces_dir = os.path.expanduser(workspaces_dir)
        self.kp = kp
        self.db_files = {
            "smb.db": NXC_Users_Extractor,
            "ftp.db": NXC_Credentials_Extractor,
            "mssql.db": NXC_Users_Extractor,
            "ssh.db": NXC_Credentials_Extractor,
            "winrm.db": NXC_Users_Extractor,
            "ldap.db": NXC_Users_Extractor,
            "rdp.db": NXC_Credentials_Extractor,
            "nfs.db": NXC_Credentials_Extractor,
            "vnc.db": NXC_Credentials_Extractor,
            "wmi.db": NXC_Credentials_Extractor,
        }

    def sync(self):
        if os.path.exists(self.workspaces_dir):
            for workspace in os.listdir(self.workspaces_dir):
                workspace_path = os.path.join(self.workspaces_dir, workspace)
                if os.path.isdir(workspace_path):
                    self.process_workspace(workspace_path)
        else:
            print("No workspaces directory found at ~/.nxc/workspaces/")

    def process_workspace(self, workspace_path):
        for db_file, extractor_class in self.db_files.items():
            db_file_path = os.path.join(workspace_path, db_file)
            service_name = db_file.split(".")[0]
            if os.path.isfile(db_file_path):
                extractor = extractor_class(db_file_path, self.kp, service_name)
                extractor.extract_and_add_credentials()
            else:
                print(f"Missing: {db_file}")
