import os

IP_TEST_VALUE = "127.0.0.1"
HOSTNAME_TEST_VALUE = "DC01"
ROLE_TEST_VALUE = "DC"

USERNAME_TEST_VALUE = "username"
PASSWORD_TEST_VALUE = "password"
HASH_TEST_VALUE = "hash"
DOMAIN_TEST_VALUE = "test.local"

TEST_ARTIFACTS_PATH = os.path.dirname(os.path.abspath(__file__)) + "/../artifacts/"
TEST_HOSTS_CSV = TEST_ARTIFACTS_PATH + "hosts.txt"
TEST_CREDS_CSV = TEST_ARTIFACTS_PATH + "creds.txt"
