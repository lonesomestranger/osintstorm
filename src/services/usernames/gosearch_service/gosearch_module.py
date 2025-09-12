import asyncio
import os
import re
import subprocess


class GoSearch:
    """Возвращает словарь, который выглядит примерно так:
    status: success
    username: ultrvlthz
    found_profiles: [{'site': 'Twitch', 'url': 'https://twitch.tv/ultrvlthz\x1b[0m'}, {'site': 'Tinder', 'url': 'https://tinder.com/@ultrvlthz\x1b[0m'}, {'site': 'Snapchat', 'url': 'https://www.snapchat.com/add/ultrvlthz\x1b[0m'}, {'site': 'Vero', 'url': 'https://vero.co/ultrvlthz\x1b[0m'}, {'site': 'Quizlet', 'url': 'https://quizlet.com/user/ultrvlthz/sets\x1b[0m'}, {'site': 'Roblox', 'url': 'https://www.roblox.com/user.aspx?username=ultrvlthz\x1b[0m'}, {'site': 'Reddit', 'url': 'https://www.reddit.com/user/ultrvlthz\x1b[0m'}]
    compromised_passwords: []
    hudsonrock_status: Not found in HudsonRock database
    domains_found: True
    found_domains: ['Twitch', 'Genius', 'Tinder', 'Snapchat', 'Vero', 'Quizlet', 'Roblox', 'Reddit']
    raw_output: ...
    """

    def __init__(self, username, no_false_positives=True):
        self.username = username
        self.no_false_positives = no_false_positives
        self.command = ["gosearch", "-u", self.username]
        if self.no_false_positives:
            self.command.append("--no-false-positives")
        self.results = {}

    async def run_search(self):
        try:
            # Check if gosearch is installed. If not, install it.
            try:
                subprocess.run(
                    ["gosearch", "-h"],
                    check=True,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                )
            except (FileNotFoundError, subprocess.CalledProcessError):
                install_process = await asyncio.create_subprocess_exec(
                    "go", "install", "github.com/ibnaleem/gosearch@latest"
                )
                await install_process.wait()

                if install_process.returncode != 0:
                    raise Exception("gosearch installation failed.")

            process = await asyncio.create_subprocess_exec(
                *self.command,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
            )
            stdout, stderr = await process.communicate()
            output = stdout.decode()
            error_output = stderr.decode()

            if process.returncode != 0:
                if "executable file not found in $PATH" in error_output:
                    raise FileNotFoundError

                raise subprocess.CalledProcessError(
                    process.returncode, self.command, output=stdout, stderr=stderr
                )

            self.parse_output(output)
            return self.results

        except FileNotFoundError:
            return {
                "status": "error",
                "message": "gosearch command not found or Go is not installed. Make sure Go is installed and gosearch is in your PATH.",
                "error_type": "FileNotFoundError",
            }
        except subprocess.CalledProcessError as e:
            return {
                "status": "error",
                "message": f"gosearch command failed: {e.stderr.decode()}",
                "error_type": "CalledProcessError",
            }
        except Exception as e:
            return {
                "status": "error",
                "message": str(e),
                "error_type": type(e).__name__,
            }

    def parse_output(self, output):
        lines = output.splitlines()
        found_profiles = []
        compromised_passwords = []
        found_domains = []

        for line in lines:
            match = re.search(r"\[\+\]\s+(\w+):\s+(https?://[^\s←]+)", line)
            if match:
                site_name = match.group(1)
                site_url = (
                    match.group(2).replace("←[0m", "").replace("\x1b[0m", "").strip()
                )
                found_profiles.append({"site": site_name, "url": site_url})

            password_match = re.search(
                r"::\s+Email:\s([^\n]+)\n::\s+Password:\s([^\n]+)", line
            )
            if password_match:
                email = password_match.group(1).strip()
                password = password_match.group(2).strip()
                compromised_passwords.append({"email": email, "password": password})

            domain_match = re.search(r"\[\+\]\s+([^\s:]+)", line)  #
            if domain_match and "::" not in line and "⎯" not in line:
                domain = domain_match.group(1).strip()
                if domain not in ("Email", "Password"):
                    found_domains.append(domain)

        hudsonrock_status = "Not found in HudsonRock database"
        for line in lines:
            if ":: This username" in line:
                if "is not associated with" in line:
                    hudsonrock_status = "Not found in HudsonRock database"
                elif "has been found in" in line:
                    hudsonrock_status = "Found in HudsonRock database"
                break

        domains_found = bool(found_domains)

        self.results = {
            "status": "success"
            if found_profiles or compromised_passwords or found_domains
            else "no_results",
            "username": self.username,
            "found_profiles": found_profiles,
            "compromised_passwords": compromised_passwords,
            "hudsonrock_status": hudsonrock_status,
            "domains_found": domains_found,
            "found_domains": found_domains,
            "raw_output": output,
        }
        if not (found_profiles or compromised_passwords or found_domains):
            self.results["message"] = (
                "No profiles, compromised passwords, or domains found."
            )
        else:
            self.results["message"] = (
                "Search completed.  See 'found_profiles', 'compromised_passwords', and 'found_domains'."
            )


async def search(username: str):
    searcher = GoSearch(username)
    results = await searcher.run_search()
    return results


async def main():
    username = input("Enter username to search: ")
    result = await search(username)

    if result["status"] == "error":
        print(f"Error: {result['message']}")
        if "error_type" in result:
            print(f"  Error Type: {result['error_type']}")

    elif result["status"] == "no_results":
        print(result["message"])
    else:
        print(f"Search results for {result['username']}:")
        if result["found_profiles"]:
            print("\nFound Profiles:")
            for profile in result["found_profiles"]:
                print(f"- {profile['site']}: {profile['url']}".replace("\x1b[0m", ""))

        if result["compromised_passwords"]:
            print("\nCompromised Passwords:")
            for item in result["compromised_passwords"]:
                print(f"  - Email: {item['email']}, Password: {item['password']}")

        print(f"\nHudsonRock Status: {result['hudsonrock_status']}")
        os.remove(f"{username}.txt")


if __name__ == "__main__":
    asyncio.run(main())
