import sqlite3
from exegol_history.db_api.creds import Credential, add_credential

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

            for row in rows:
                domain, username, password, credtype = row
                credential = Credential(username=username, password=password, domain=domain)
                if credtype == 'plaintext':
                    add_credential(self.kp, credential)
                    counter = counter + 1
                elif credtype == 'hash':
                    if ':' in password:
                        password = password.split(':')[1]
                    add_credential(self.kp, credential)
                    counter = counter + 1
            
            print(f"Synced {counter} {self.service_name} credentials")

            conn.close()
        except Exception as e:
            print(f"Error extracting from {self.db_file_path}: {e}")
