import time

import requests


class IPParser:
    def __init__(self, ip_addr):
        self.ip = ip_addr

    def parse_info(self):
        try:
            response = requests.get(
                f"http://ipwho.is/{self.ip}", timeout=10, verify=False
            )

            if response.status_code == 200:
                return response.json()
            else:
                time.sleep(5)
                self.parse_info()
        except Exception:
            return None


if __name__ == "__main__":
    ip_parser = IPParser("44.44.44.44").parse_info()
