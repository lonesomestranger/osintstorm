import asyncio
import json
import logging
import os
import re

import requests


class Maigret:
    def __init__(
            self,
            db_file="data.json",
            cookies_file="cookies.txt",
            top_sites_count=350,
            timeout=30,
            *,
            db_url="https://raw.githubusercontent.com/soxoj/maigret/main/maigret/resources/data.json",
            cookies_url="https://raw.githubusercontent.com/soxoj/maigret/main/cookies.txt",
    ):
        self.db_file = db_file
        self.cookies_file = cookies_file
        self.top_sites_count = top_sites_count
        self.timeout = timeout
        self.db_url = db_url
        self.cookies_url = cookies_url
        self.logger = logging.getLogger("maigret_cli")

    def download_files(self):
        self._download_file(self.db_file, self.db_url)
        self._download_file(self.cookies_file, self.cookies_url)

    def _download_file(self, local_path, remote_url):
        try:
            if not os.path.exists(local_path):
                print(f"Downloading {local_path}...")
                response = requests.get(remote_url, stream=True)
                response.raise_for_status()
                with open(local_path, "wb") as f:
                    for chunk in response.iter_content(chunk_size=8192):
                        f.write(chunk)
                print(f"{local_path} downloaded successfully.")
        except requests.exceptions.RequestException as e:
            self.logger.error(f"Error downloading {local_path}: {e}")
            raise

    async def search(self, username: str):
        report_filename = f"{username}_report.pdf"

        command = [
            "maigret",
            username,
            "--top-sites", str(self.top_sites_count),
            "--timeout", str(self.timeout),
            "--cookies", self.cookies_file,
            "--pdf",
            "--no-progressbar",
            "--no-color",
        ]

        try:
            process = await asyncio.create_subprocess_exec(
                *command,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
            )
            stdout, stderr = await process.communicate()

            # Handle PDF report
            pdf_report_path = os.path.join("reports", f"report_{username}.pdf")
            if os.path.exists(pdf_report_path):
                try:
                    # --- FIX: Overwrite existing report file ---
                    # If the destination file already exists, remove it first.
                    if os.path.exists(report_filename):
                        os.remove(report_filename)
                    os.rename(pdf_report_path, report_filename)
                    # --- END FIX ---
                except Exception as e:
                    self.logger.error(f"Could not move report file: {e}")
                    report_filename = None  # Signal that the report is not available
            else:
                report_filename = None

            # Parse text output directly from stdout
            found_sites = []
            if stdout:
                stdout_text = stdout.decode(errors='ignore')
                matches = re.findall(r"\[\+\]\s(.*?):\s(https?://[^\s]+)", stdout_text)
                for site_name, url in matches:
                    if "OP.GG" in site_name:
                        continue

                    found_sites.append({
                        "site": site_name.strip(),
                        "url_user": url.strip(),
                        "status": {"status": "claimed"}
                    })

            if not found_sites:
                return {
                    "status": "no_results",
                    "message": "No accounts found.",
                    "found_sites": [],
                    "report_filename": report_filename,
                }

            return {
                "status": "success",
                "message": "Search completed successfully.",
                "found_sites": found_sites,
                "report_filename": report_filename,
            }

        except FileNotFoundError:
            self.logger.error("Maigret command not found. Is it installed and in PATH?")
            return {
                "status": "error",
                "message": "Maigret is not installed or not in your system's PATH.",
                "found_sites": [],
                "report_filename": None,
            }
        except Exception as e:
            self.logger.error(f"An unexpected error occurred during Maigret search: {e}")
            return {
                "status": "error",
                "message": "An error occurred during the search.",
                "found_sites": [],
                "report_filename": None,
            }