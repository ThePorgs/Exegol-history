import sqlite3
from exegol_history.db_api.creds import Credential, add_credentials, edit_credentials, get_existing_credential

class NXC_Users_Extractor:
    def __init__(self, db_file_path, kp, service_name):
        self.db_file_path = db_file_path
        self.kp = kp
        self.service_name = service_name

    def extract_and_add_credentials(self):
        try:
            conn = sqlite3.connect(self.db_file_path)
            cursor = conn.cursor()

            query = "SELECT domain, username, password, credtype FROM users"
            cursor.execute(query)
            rows = cursor.fetchall()
            counter = 0
            credentials_to_add = []
            credentials_to_edit = []

            for row in rows:
                domain, username, password, credtype = row
                credential = Credential(username=username, domain=domain)
                existing_credential = get_existing_credential(self.kp, credential)

                if credtype == 'plaintext':
                    credential.password = password
                elif credtype == 'hash':
                    if ':' in password:
                        password = password.split(':')[1]
                    credential.hash = password

                if not existing_credential:
                    credentials_to_add.append(credential)
                    counter = counter + 1
                else:
                    counter = counter + 1
                    credential.id = existing_credential.title
                    credentials_to_edit.append(credential)

                add_credentials(self.kp, credentials_to_add)
                edit_credentials(self.kp, credentials_to_edit)

            print(f"Synced {counter} {self.service_name} credentials")

            conn.close()
        except Exception as e:
            print(f"Error extracting from {self.db_file_path}: {e}")
