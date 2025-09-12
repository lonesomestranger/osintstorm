import asyncio
import asyncio.subprocess
import re


class Holehe:
    def __init__(self, email, only_used=False):
        if not re.match(r"[^@]+@[^@]+\.[^@]+", email):
            raise ValueError("Invalid email format.")
        self.email = email
        self.only_used = only_used

    async def run_holehe(self):
        command = ["holehe", self.email]
        if self.only_used:
            command.append("--only-used")

        try:
            proc = await asyncio.subprocess.create_subprocess_exec(
                *command,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
            )

            stdout, stderr = await proc.communicate()
            output = stdout.decode()

            if proc.returncode != 0:
                print(f"Error running holehe: {proc.returncode}")
                print(f"  Error output:\n{stderr.decode()}")
                return []

            regex = r"\[\+\]\s*([A-Za-z0-9.-]+)(.*)"

            used_services = []
            for line in output.splitlines():
                match = re.search(regex, line)
                if match:
                    service_name = match.group(1)
                    used_services.append(service_name)

            return used_services

        except FileNotFoundError:
            print("Error: holehe is not installed or not in your PATH.")
            print("Please make sure holehe is installed correctly:  pip install holehe")
            return []
        except Exception as e:
            print(f"An unexpected error occurred: {e}")
            return []


async def main():
    email = "testmail@gmail.com"
    parser = Holehe(email=email, only_used=True)
    used_services = await parser.run_holehe()
    print(f"Used services [{email}]: {used_services}")


if __name__ == "__main__":
    asyncio.run(main())
