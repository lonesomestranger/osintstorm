> ### Важное замечание от автора
>
> Maigret — отвратительный продукт, который тянет за собой поток deprecated репозиториев. Это не позволяет проекту (особенно в связке с отдельной утилитой на Go) иметь актуальные зависимости, что мешает развитию и удобству поддержки.
>
> Активная разработка этого бота прекращена. OSINT-инструменты в открытом доступе умирают день за днем, и сейчас на рынке живы только монетизированные продукты, которые наглым образом собирают наши личные данные путем манипуляций и социальной инженерии. Telegram является площадкой, которая предоставляет крупным игрокам, таким как Антипов, нагло наживаться на глупости неопытных пользователей.
>
> **Будьте внимательны.**
>
> По желанию вы можете связаться со мной через контакты, указанные в моем профиле GitHub, для доработки функционала бота по вашим советам или для совместной работы.

> ### An Important Note from the Author
>
> Maigret is a terrible product that relies on a chain of deprecated dependencies. This prevents the project (especially when used alongside a separate Go-based tool) from maintaining up-to-date dependencies, which hinders flexibility and ease of maintenance.
>
> Active development of this bot has been discontinued. Open-source OSINT tools are dying out day by day, leaving only monetized products that brazenly collect our personal data through manipulation and social engineering. Telegram has become a platform that allows major players, such as Antipov, to shamelessly profit from the naivety of inexperienced users.
>
> **Please be careful.**
>
> If you wish, you can contact me via the methods listed on my GitHub profile to improve the bot's functionality based on your suggestions or to collaborate on its development.

---

# ⛰ Codeberg
Actual link is [here](https://codeberg.org/lonesomestranger/osintstorm).

---

# OSINT-Storm Telegram Bot

OSINT-Storm is a powerful Telegram bot designed for Open Source Intelligence (OSINT) investigations. It integrates various services and tools to help you gather information on usernames, emails, IP addresses, VK profiles, and more, directly from your Telegram client.

## Features

-   **Username Search**: Perform normal or deep searches for a username across hundreds of websites using Maigret and GoSearch.
-   **Email Analysis**: Check which services an email address is registered on with Holehe.
-   **IP Address Info**: Get detailed information about an IP address (country, city, coordinates).
-   **VK Profile Parsing**: Extract public information from a VK user profile, including registration date, communities, and applications (requires configuration).
-   **Full Name Search (Dorks)**: Generate Google Dorks to search for information based on a full name and date of birth.
-   **Useful Links**: A curated list of external OSINT tools and resources.
-   **Helper Commands**: Quick access to information about domains, phone numbers, Steam profiles, and crypto wallets via external service links.

## Prerequisites

Before you begin, ensure you have the following installed on your system:

-   **Python 3.10+**
-   **Go Language (1.18+)**

## Installation

1.  **Clone the repository:**
    ```bash
    git clone https://github.com/lonesomestranger/osintstorm.git
    cd osintstorm
    ```

2.  **Install Go dependencies:**
    The bot uses `gosearch` for deep username searches. Install it and make sure it's available in your system's PATH.
    ```bash
    go install github.com/ibnaleem/gosearch@latest
    ```
    *Note: Ensure that your Go binary path (e.g., `~/go/bin` or `C:\Users\YourUser\go\bin`) is included in your system's `PATH` environment variable.*

3.  **Set up a Python virtual environment:**
    ```bash
    python -m venv venv
    source venv/bin/activate  # On Windows, use `venv\Scripts\activate`
    ```

4.  **Install Python dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

## Configuration

1.  **Create a `.env` file:**
    Copy the example file to create your own configuration file.
    ```bash
    cp .env.example .env
    ```

2.  **Edit the `.env` file:**
    Open the `.env` file and fill in the required values.

    -   `BOT_TOKEN`: Your Telegram bot token, which you can get from [@BotFather](https://t.me/BotFather).

    -   `VK_APP_URL` (Optional): This is required for the VK profile search feature. If you leave this empty, the feature will be disabled.
        -   **How to get the URL:**
            1.  Log in to your VK.com account in a web browser.
            2.  Go to the [VK InfoApp application](https://vk.com/app7183114_353722110).
            3.  Open your browser's developer tools (usually F12) and go to the "Network" tab.
            4.  In the app's search bar, search for any user (e.g., `durov`).
            5.  In the Network tab, you will see requests being made. The URL you need is the one for the main document or frame of the app. It will look something like `https://prod-app7183114-*.pages-ac.vk-apps.com/index.html?...`.
            6.  Copy the **full URL** and paste it as the value for `VK_APP_URL`.

## Running the Bot

Once you have completed the installation and configuration, you can start the bot with the following command:

```bash
python -m src.bot.bot
```

## TODO

- Automated analysis of a crypto wallet with any coin
- Enumeration of osint sources once again
- Study of the applicability of phomber
