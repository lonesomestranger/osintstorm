import os
import platform
import time

from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from webdriver_manager.chrome import ChromeDriverManager

from src.config import VK_APP_URL


class VkParser:
    def __init__(self, url=VK_APP_URL):
        self.url = url
        self.chrome_options = self._get_chrome_options()

    def _get_chrome_options(self):
        chrome_options = Options()
        chrome_options.add_argument("--headless")
        chrome_options.add_argument("--incognito")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--start-maximized")
        chrome_options.add_argument("--disable-popup-blocking")
        chrome_options.add_argument("--disable-crash-reporter")
        chrome_options.add_argument("--disable-in-process-stack-traces")
        chrome_options.add_argument("--disable-logging")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--disable-blink-features=AutomationControlled")
        chrome_options.add_argument("--log-level=3")
        chrome_options.add_argument("--output=/dev/null")

        prefs = {"profile.managed_default_content_settings.images": 2}
        chrome_options.add_experimental_option("prefs", prefs)
        chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
        chrome_options.add_experimental_option("useAutomationExtension", False)
        return chrome_options

    def _get_driver(self):
        system = platform.system()
        if system == "Windows":
            return webdriver.Chrome(options=self.chrome_options)
        else:
            service = Service(ChromeDriverManager().install())
            return webdriver.Chrome(service=service, options=self.chrome_options)

    def parse_user_data(self, username):
        if not self.url:
            print("VK_APP_URL is not configured. VK parsing is disabled.")
            return None
        with self._get_driver() as driver:
            return self._parse_data_with_driver(driver, self.url, username)

    def _parse_data_with_driver(self, driver, url, input_value):
        try:
            driver.get(url)

            # поле ввода юзернейма
            input_element = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located(
                    (
                        By.XPATH,
                        "//*[@id='input']/div/section/div[1]/form/div/div[1]/div/input",
                    )
                )
            )
            input_element.send_keys(input_value)

            # нажатие на кнопку Найти
            submit_button = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable(
                    (
                        By.XPATH,
                        '//*[@id="input"]/div/section/div[1]/form/div/div[2]/button/span[1]',
                    )
                )
            )
            submit_button.click()
            user_data = {}

            try:
                if WebDriverWait(driver, 3).until(
                        EC.presence_of_element_located(
                            (
                                    By.XPATH,
                                    '//*[@id="root"]/div/div/div/div/section/div[2]/div/div/div[2]/div/div[2]',
                            )
                        )
                ):
                    print("Такого пользователя не существует.")
                    return "user_not_found"
            except Exception:
                pass

            # имя фамилия
            user_data["name"] = (
                WebDriverWait(driver, 10)
                .until(
                    EC.presence_of_element_located(
                        (
                            By.XPATH,
                            '//*[@id="input"]/div/section/div[1]/a/div[2]/div/span',
                        )
                    )
                )
                .text
            )

            # дата регистрации
            user_data["registration_date"] = (
                WebDriverWait(driver, 10)
                .until(
                    EC.presence_of_element_located(
                        (By.XPATH, '//*[@id="input"]/div/section/div[1]/a/div[2]/span')
                    )
                )
                .text.replace("Дата регистрации: ", "")
            )

            # вк айди (может пригодиться)
            user_data["vk_id"] = driver.find_element(
                By.XPATH, '//*[@id="input"]/div/section/div[1]/div[6]/div[2]/span'
            ).text

            # интересовались за месяц
            was_searched = driver.find_element(
                By.XPATH, '//*[@id="input"]/div/section/div[1]/div[3]/div[2]/div/span'
            ).text

            # кнопка Сообщества
            if was_searched != "Интересовались за последний месяц":
                driver.find_element(
                    By.XPATH,
                    '//*[@id="input"]/div/section/div[1]/div[8]/div[2]/div/span',
                ).click()
            else:
                driver.find_element(
                    By.XPATH,
                    '//*[@id="input"]/div/section/div[1]/div[10]/div[2]/div/span',
                ).click()

            try:
                WebDriverWait(driver, 10).until(
                    EC.presence_of_element_located(
                        (By.XPATH, '//*[@id="groups"]/div/section/div[1]/header')
                    )
                )
            except Exception as e:
                print(
                    f"Timeout waiting for community data or 'no communities' message: {e}"
                )
                return None

            html = driver.page_source
            soup = BeautifulSoup(html, "html.parser")

            no_communities_header = soup.find(
                "span", class_="vkuiPanelHeader__content-in PanelHeader__content-in"
            )
            if (
                    no_communities_header
                    and "Сообществ не найдено" in no_communities_header.get_text(strip=True)
            ):
                print("Сообществ не найдено.")
                driver.find_element(
                    By.XPATH,
                    '//*[@id="groups"]/div/div[2]/div[1]/div/div/div[1]/button',
                ).click()
                user_data["communities"] = []

            else:
                communities = []
                for community_link in soup.find_all(
                        "a",
                        class_="vkuiSimpleCell vkuiSimpleCell--android SimpleCell SimpleCell--android vkuiSimpleCell--sizeY-compact SimpleCell--sizeY-compact vkuiTappable vkuiTappable--android Tappable Tappable--android vkuiTappable--sizeX-regular Tappable--sizeX-regular vkuiTappable--mouse Tappable--mouse",
                ):
                    name_span = community_link.find(
                        "span",
                        class_="vkuiSimpleCell__children SimpleCell__children vkuiText vkuiText--android Text Text--android vkuiText--w-regular Text--w-regular",
                    )
                    name = name_span.get_text(strip=True) if name_span else None

                    link = community_link.get("href")

                    participants_span = community_link.find(
                        "span",
                        class_="vkuiSimpleCell__description SimpleCell__description vkuiSubhead vkuiSubhead--android Subhead Subhead--android vkuiSubhead--w-regular Subhead--w-regular",
                    )
                    participants = (
                        participants_span.get_text(strip=True)
                        if participants_span
                        else None
                    )

                    if name and link and participants:
                        communities.append(
                            {"name": name, "link": link, "participants": participants}
                        )

                user_data["communities"] = communities

                try:
                    back_button = driver.find_element(
                        By.XPATH,
                        '//*[@id="groups"]/div/div[2]/div[1]/div/div/div[1]/button',
                    )
                    time.sleep(1)
                    back_button.click()
                except Exception as e:
                    print(f"Error navigating to next tab: {e}")
                    return None

            # кнопка Приложения
            if was_searched != "Интересовались за последний месяц":
                WebDriverWait(driver, 10).until(
                    EC.element_to_be_clickable(
                        (
                            By.XPATH,
                            '//*[@id="input"]/div/section/div[1]/div[9]/div[2]/div/span',
                        )
                    )
                ).click()
                time.sleep(1)
            else:
                try:
                    WebDriverWait(driver, 10).until(
                        EC.element_to_be_clickable(
                            (
                                By.XPATH,
                                '//*[@id="input"]/div/section/div[1]/div[11]/div[2]/div/span',
                            )
                        )
                    ).click()
                    time.sleep(1)
                except Exception as e:
                    print(f"Timeout waiting for app data or 'no apps' message: {e}")
                    return None

            html = driver.page_source
            soup = BeautifulSoup(html, "html.parser")

            no_apps_header = soup.find(
                "span", class_="vkuiPanelHeader__content-in PanelHeader__content-in"
            )
            if no_apps_header and "Приложений не найдено" in no_apps_header.get_text(
                    strip=True
            ):
                print("Приложений не найдено.")
                driver.find_element(
                    By.XPATH, '//*[@id="apps"]/div/div[2]/div[1]/div/div/div[1]/button'
                ).click()
                user_data["apps"] = []
            else:
                apps = []
                for app_link in soup.find_all(
                        "a",
                        class_="vkuiSimpleCell vkuiSimpleCell--android SimpleCell SimpleCell--android vkuiSimpleCell--sizeY-compact SimpleCell--sizeY-compact vkuiTappable vkuiTappable--android Tappable Tappable--android vkuiTappable--sizeX-regular Tappable--sizeX-regular vkuiTappable--mouse Tappable--mouse",
                ):
                    name_span = app_link.find(
                        "span",
                        class_="vkuiSimpleCell__children SimpleCell__children vkuiText vkuiText--android Text Text--android vkuiText--w-regular Text--w-regular",
                    )
                    name = name_span.get_text(strip=True) if name_span else None
                    link = app_link.get("href")
                    participants_span = app_link.find(
                        "span",
                        class_="vkuiSimpleCell__description SimpleCell__description vkuiSubhead vkuiSubhead--android Subhead Subhead--android vkuiSubhead--w-regular Subhead--w-regular",
                    )
                    participants = (
                        participants_span.get_text(strip=True)
                        if participants_span
                        else None
                    )

                    if name and link and participants:
                        apps.append(
                            {"name": name, "link": link, "participants": participants}
                        )
                user_data["apps"] = apps

                try:
                    back_button = driver.find_element(
                        By.XPATH,
                        '//*[@id="apps"]/div/div[2]/div[1]/div/div/div[1]/button',
                    )
                    time.sleep(1)
                    back_button.click()
                except Exception as e:
                    print(f"Error navigating to the next tab after Apps: {e}")

            # кнопка Прочее (остальные не работают не в приложении)
            if was_searched != "Интересовались за последний месяц":
                WebDriverWait(driver, 10).until(
                    EC.element_to_be_clickable(
                        (
                            By.XPATH,
                            '//*[@id="input"]/div/section/div[1]/div[13]/div[2]/div',
                        )
                    )
                ).click()
                time.sleep(1)
            else:
                try:
                    WebDriverWait(driver, 10).until(
                        EC.element_to_be_clickable(
                            (
                                By.XPATH,
                                '//*[@id="input"]/div/section/div[1]/div[15]/div[2]/div',
                            )
                        )
                    ).click()
                    time.sleep(1)
                except Exception as e:
                    print(f"Timeout waiting for app data or 'no apps' message: {e}")
                    return None

            try:
                user_data["last_visit"] = (
                    WebDriverWait(driver, 10)
                    .until(
                        EC.presence_of_element_located(
                            (
                                By.XPATH,
                                '//*[@id="other"]/div/section/div[1]/div[2]/div/div/span/h3',
                            )
                        )
                    )
                    .text.strip()
                    .rstrip()
                )
            except Exception:
                user_data["last_visit"] = None

            driver.quit()
            return user_data
        except Exception as e:
            print(f"Произошла ошибка: {e}")
            return None


def main():
    if not VK_APP_URL:
        print("Please set VK_APP_URL in your .env file to run this test.")
        return

    parser = VkParser()
    user_data = parser.parse_user_data("durov")

    if user_data:
        print(f"Registration Date: {user_data['registration_date']}")
        print(f"VK ID: {user_data['vk_id']}")
        print(f"Last Visit: {user_data['last_visit']}")

        if user_data["communities"]:
            print("\nCommunities:")
            for community in user_data["communities"]:
                print(f"  Name: {community['name']}")
                print(f"  Link: {community['link']}")
                print(f"  Participants: {community['participants']}")
                print("-" * 20)
        else:
            print("\nNo communities found.")

        if user_data["apps"]:
            print("\nApps:")
            for app in user_data["apps"]:
                print(f"  Name: {app['name']}")
                print(f"  Link: {app['link']}")
                print(f"  Participants: {app['participants']}")
                print("-" * 20)
        else:
            print("\nNo apps found.")
    else:
        print("Failed to retrieve user data.")


if __name__ == "__main__":
    main()