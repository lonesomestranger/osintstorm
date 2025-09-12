import hashlib
import urllib.parse


def _md5(text):
    return hashlib.md5(text.encode("utf-8")).hexdigest()


def _emtools(value):
    encoded_value = urllib.parse.quote_plus(value)
    return [
        f"https://epieos.com/?q={encoded_value}",
        f"https://predictasearch.com/?q={encoded_value}",
        f'https://www.google.com/search?q="{encoded_value}"',
        f'https://www.google.com/search?q="{encoded_value}"&tbm=isch',
        f'https://www.bing.com/search?q="{encoded_value}"',
        f'https://yandex.com/search/?text="{encoded_value}"',
    ]


def _openall(base_url, values):
    return [base_url + urllib.parse.quote_plus(v) for v in values]


class Namint:
    def __init__(
        self,
        name="",
        middle="",
        surname="",
        date_of_birth="",
        dom1="icloud.com",
        dom2="yahoo.com",
        dom3="hotmail.com",
        dom4="msn.com",
    ):
        self.name = name
        self.middle = middle
        self.surname = surname
        self.date_of_birth = date_of_birth
        self.dom1 = dom1
        self.dom2 = dom2
        self.dom3 = dom3
        self.dom4 = dom4
        self.linum = 0
        self.or_names = []

    def _addname(self, value):
        encoded_value = urllib.parse.quote_plus(value)
        links = [
            f'https://www.google.com/search?q="{encoded_value}"',
            f'https://www.google.com/search?q="{encoded_value}"&tbs=itp%3Aface&tbm=isch',
            f'https://www.google.com/search?q="{encoded_value}"+AND+(%E2%9C%86+OR+%E2%98%8E+OR+%E2%98%8F+OR+%F0%9F%93%B1+OR+%F0%9F%93%9E)',
            f'https://www.google.com/search?q="{encoded_value}"+AND+(%F0%9F%93%A7+OR+%F0%9F%93%A8+OR+%F0%9F%93%A9+OR+✉)',
            f'https://www.google.com/maps/search/"{encoded_value}"',
            f'https://www.google.com/search?q="{encoded_value}"+ext:pdf',
            f'https://www.google.com/search?q="{encoded_value}"+ext:docx',
            f'https://www.google.com/search?q="{encoded_value}"+ext:xlsx',
            f'https://www.bing.com/search?q="{encoded_value}"',
            f'https://yandex.com/search/?text="{encoded_value}"',
            f'https://yandex.com/images/search?text="{encoded_value}"&type=face',
            f"https://www.facebook.com/public/{encoded_value}",
            f"https://twitter.com/search?q={encoded_value}&src=typed_query&f=user",
            f"https://www.tiktok.com/search/user?q={encoded_value}",
            f'https://www.flickr.com/search/people/?username="{encoded_value}"',
            f"https://vk.com/search?c%5Bname%5D=1&c%5Bper_page%5D=40&c%5Bq%5D={encoded_value}&c%5Bsection%5D=people",
        ]

        if self.linum == 0:
            links.append(
                f"https://www.linkedin.com/pub/dir?firstName={urllib.parse.quote_plus(self.name)}&lastName={urllib.parse.quote_plus(self.surname)}&src=typed_query&f=user"
            )
            self.linum += 1
        return links

    def _forname(self, value):
        self.or_names.append(f'"{value}"')
        return f'"{value}"'

    def _addlogin(self, value):
        encoded_value = urllib.parse.quote_plus(value)
        links = [
            f'https://www.google.com/search?q="{encoded_value}"',
            f'https://www.bing.com/search?q="{encoded_value}"',
            f'https://yandex.com/search/?text="{encoded_value}"',
            f'https://www.google.com/search?q="{encoded_value}@gmail.com"+OR+"{encoded_value}@outlook.com"+OR+"{encoded_value}@icloud.com"+OR+"{encoded_value}@yahoo.com"+OR+"{encoded_value}@protonmail.com"',
            f"https://www.facebook.com/{encoded_value}",
            f"https://twitter.com/{encoded_value}",
            f"https://instagram.com/{encoded_value}",
            f"https://www.tiktok.com/@{encoded_value}",
            f"https://www.twitch.tv/{encoded_value}",
            f"https://seintpl.github.io/imagstodon/?u={encoded_value}",
            f"https://whatsmyname.app/?q={encoded_value}",
        ]

        f"{value}@gmail.com"
        f"{value}@outlook.com"
        f"{value}@{self.dom1}"
        f"{value}@{self.dom2}"
        f"{value}@{self.dom3}"
        f"{value}@{self.dom4}"

        return links

    def generate_links(self):
        if not self.name or not self.surname:
            return "Enter at least name and surname name."

        all_links = {}

        p = []
        q = []
        r = []
        s = []

        p.append(f"{self.name} {self.surname}")
        p.append(f"{self.name[0]}. {self.surname}")
        p.append(f"{self.surname} {self.name}")
        p.append(f"{self.surname} {self.name[0]}.")
        for name in p:
            self._forname(name)
        p.append(self.surname)

        all_links["name_patterns"] = []
        for name_pattern in p:
            all_links["name_patterns"].extend(self._addname(name_pattern))

        if self.middle:
            q.append(f"{self.name} {self.middle} {self.surname}")
            q.append(f"{self.name[0]}. {self.middle[0]}. {self.surname}")
            q.append(f"{self.name} {self.middle[0]}. {self.surname}")
            q.append(f"{self.surname} {self.name} {self.middle}")
            q.append(f"{self.surname} {self.name[0]}. {self.middle[0]}.")
            q.append(f"{self.middle} {self.surname}")

            all_links["name_patterns_with_middle"] = []
            for name_pattern in q:
                all_links["name_patterns_with_middle"].extend(
                    self._addname(name_pattern)
                )
                self._forname(name_pattern)

        or_name_query = " OR ".join(self.or_names)
        encoded_or_name = urllib.parse.quote_plus(or_name_query)
        all_links["combined_name_search"] = [
            f"https://www.google.com/search?q={encoded_or_name}",
            f'https://www.google.com/search?q={encoded_or_name}"&tbs=itp%3Aface&tbm=isch',
            f"https://www.google.com/search?q=({encoded_or_name})+AND+(%E2%9C%86+OR+%E2%98%8E+OR+%E2%98%8F+OR+%F0%9F%93%B1+OR+%F0%9F%93%9E)",
            f"https://www.google.com/search?q=({encoded_or_name})+AND+(%F0%9F%93%A7+OR+%F0%9F%93%A8+OR+%F0%9F%93%A9+OR+✉)",
            f"https://www.google.com/maps/search/{encoded_or_name}",
            f'https://www.google.com/search?q="{encoded_or_name}"+ext:pdf',
            f'https://www.google.com/search?q="{encoded_or_name}"+ext:docx',
            f'https://www.google.com/search?q="{encoded_or_name}"+ext:xlsx',
            f"https://www.bing.com/search?q={encoded_or_name}",
            f"https://yandex.com/search/?text={encoded_or_name}",
            f"https://yandex.com/images/search?text={encoded_or_name}&type=face",
            f"https://www.google.com/search?q={encoded_or_name} site:pastebin.com",
        ]

        r.append(f"{self.name.lower()}.{self.surname.lower()}")
        r.append(f"{self.surname.lower()}.{self.name.lower()}")
        r.append(f"{self.name[0].lower()}.{self.surname.lower()}")
        r.append(f"{self.surname.lower()}.{self.name[0].lower()}")
        r.append(f"{self.name.lower()}{self.surname.lower()}")
        r.append(f"{self.surname.lower()}{self.name.lower()}")
        r.append(f"{self.name[0].lower()}{self.surname.lower()}")
        r.append(f"{self.surname.lower()}{self.name[0].lower()}")
        r.append(f"{self.name.lower()}{self.surname[0].lower()}")
        r.append(f"{self.name.lower()}.{self.surname[0].lower()}")
        r.append(f"{self.name.lower()}_{self.surname.lower()}")
        r.append(f"{self.surname.lower()}_{self.name.lower()}")
        r.append(f"{self.name.lower()}-{self.surname.lower()}")
        r.append(f"{self.surname.lower()}-{self.name.lower()}")
        r.append(f"{self.name[0].lower()}_{self.surname.lower()}")
        r.append(f"{self.surname.lower()}_{self.name[0].lower()}")
        r.append(f"{self.name[0].lower()}-{self.surname.lower()}")
        r.append(f"{self.surname.lower()}-{self.name[0].lower()}")
        r.append(f"{self.name.lower()}")
        r.append(f"{self.surname.lower()}")

        if self.date_of_birth:
            r.append(f"{self.name.lower()}.{self.surname.lower()}{self.date_of_birth}")
            r.append(f"{self.surname.lower()}.{self.name.lower()}{self.date_of_birth}")
            r.append(
                f"{self.name[0].lower()}.{self.surname.lower()}{self.date_of_birth}"
            )
            r.append(
                f"{self.surname.lower()}.{self.name[0].lower()}{self.date_of_birth}"
            )
            r.append(f"{self.name.lower()}{self.surname.lower()}{self.date_of_birth}")
            r.append(f"{self.surname.lower()}{self.name.lower()}{self.date_of_birth}")
            r.append(
                f"{self.name[0].lower()}{self.surname.lower()}{self.date_of_birth}"
            )
            r.append(
                f"{self.surname.lower()}{self.name[0].lower()}{self.date_of_birth}"
            )
            r.append(
                f"{self.name.lower()}{self.surname[0].lower()}{self.date_of_birth}"
            )
            r.append(
                f"{self.name.lower()}.{self.surname[0].lower()}{self.date_of_birth}"
            )
            r.append(f"{self.name.lower()}_{self.surname.lower()}{self.date_of_birth}")
            r.append(f"{self.surname.lower()}_{self.name.lower()}{self.date_of_birth}")
            r.append(f"{self.name.lower()}-{self.surname.lower()}{self.date_of_birth}")
            r.append(f"{self.surname.lower()}-{self.name.lower()}{self.date_of_birth}")
            r.append(
                f"{self.name[0].lower()}_{self.surname.lower()}{self.date_of_birth}"
            )
            r.append(
                f"{self.surname.lower()}_{self.name[0].lower()}{self.date_of_birth}"
            )
            r.append(
                f"{self.name[0].lower()}-{self.surname.lower()}{self.date_of_birth}"
            )
            r.append(
                f"{self.surname.lower()}-{self.name[0].lower()}{self.date_of_birth}"
            )
            r.append(f"{self.name.lower()}{self.date_of_birth}")
            r.append(f"{self.surname.lower()}{self.date_of_birth}")

        all_links["login_patterns"] = []
        for login_pattern in r:
            all_links["login_patterns"].extend(self._addlogin(login_pattern))

        if self.middle:
            s.append(f"{self.name.lower()}{self.middle.lower()}{self.surname.lower()}")
            s.append(f"{self.surname.lower()}{self.name.lower()}{self.middle.lower()}")
            s.append(
                f"{self.name.lower()}{self.middle[0].lower()}{self.surname.lower()}"
            )
            s.append(
                f"{self.name[0].lower()}{self.middle[0].lower()}{self.surname.lower()}"
            )
            s.append(
                f"{self.surname.lower()}{self.name[0].lower()}{self.middle[0].lower()}"
            )
            s.append(f"{self.middle.lower()}{self.surname.lower()}")
            s.append(f"{self.surname.lower()}{self.middle.lower()}")
            s.append(f"{self.middle.lower()}")

            if self.date_of_birth:
                s.append(
                    f"{self.name.lower()}{self.middle.lower()}{self.surname.lower()}{self.date_of_birth}"
                )
                s.append(
                    f"{self.surname.lower()}{self.name.lower()}{self.middle.lower()}{self.date_of_birth}"
                )
                s.append(
                    f"{self.name.lower()}{self.middle[0].lower()}{self.surname.lower()}{self.date_of_birth}"
                )
                s.append(
                    f"{self.name[0].lower()}{self.middle[0].lower()}{self.surname.lower()}{self.date_of_birth}"
                )
                s.append(
                    f"{self.surname.lower()}{self.name[0].lower()}{self.middle[0].lower()}{self.date_of_birth}"
                )
                s.append(
                    f"{self.middle.lower()}{self.surname.lower()}{self.date_of_birth}"
                )
                s.append(
                    f"{self.surname.lower()}{self.middle.lower()}{self.date_of_birth}"
                )
                s.append(f"{self.middle.lower()}{self.date_of_birth}")

            all_links["login_patterns_with_middle"] = []
            for login_pattern in s:
                all_links["login_patterns_with_middle"].extend(
                    self._addlogin(login_pattern)
                )

        email_combos = []
        for login in r + s if self.middle else r:
            email_combos.append(f"{login}@gmail.com")
            email_combos.append(f"{login}@outlook.com")
            email_combos.append(f"{login}@{self.dom1}")
            email_combos.append(f"{login}@{self.dom2}")
            email_combos.append(f"{login}@{self.dom3}")
            email_combos.append(f"{login}@{self.dom4}")

        all_links["email_search"] = []
        for email in email_combos:
            all_links["email_search"].extend(_emtools(email))

        return all_links


def main():
    """
    Класс Namint: Генератор поисковых ссылок по имени, фамилии и другим данным.

    Этот класс предназначен для автоматического создания набора ссылок, которые можно использовать
    для поиска информации о человеке в различных поисковых системах и социальных сетях.  Он принимает
    имя, фамилию, отчество (необязательно), числовой суффикс (например, год рождения) и
    несколько дополнительных доменов электронной почты, а затем генерирует различные
    комбинации этих данных для формирования поисковых запросов.

    Args:
        name (str): Имя.  Обязательный параметр.
        middle (str): Отчество.  Необязательный параметр.
        surname (str): Фамилия.  Обязательный параметр.
        date_of_birth (str): Числовой суффикс (например, год рождения, номер телефона или любой другой
            числовой идентификатор).  Необязательный параметр.
        dom1 (str): Дополнительный домен электронной почты (например, "company.com").
            По умолчанию "icloud.com".
        dom2 (str): Дополнительный домен электронной почты. По умолчанию "yahoo.com".
        dom3 (str): Дополнительный домен электронной почты. По умолчанию "hotmail.com".
        dom4 (str): Дополнительный домен электронной почты. По умолчанию "msn.com".

    Returns:
        dict: Словарь, где ключи - это категории сгенерированных ссылок, а значения - списки URL
            (строки) для каждой категории.  Если имя или фамилия не указаны, возвращает строку
            с сообщением об ошибке.

    Категории ссылок (ключи словаря):

        * name_patterns: Ссылки для поиска по различным комбинациям имени и фамилии (без отчества):
            - Имя Фамилия (John Doe)
            - И. Фамилия (J. Doe)
            - Фамилия Имя (Doe John)
            - Фамилия И. (Doe J.)
            - Фамилия (Doe)

        * name_patterns_with_middle:  То же, что и `name_patterns`, но с использованием отчества
            (если оно указано). Генерируются все возможные перестановки имени, фамилии и отчества.
              Примеры (для name="John", middle="Middle", surname="Doe"):
              - John Middle Doe
              - J. M. Doe
              - John M. Doe
              - Doe John Middle
              - Doe J. M.
              - Middle Doe

        * combined_name_search: Ссылки для поиска по всем комбинациям имени, фамилии и отчества
            (если есть), объединенные оператором OR.  Это позволяет найти результаты, соответствующие
            любому из вариантов написания имени.  Используются поисковые системы Google, Bing, Yandex,
            а также поиск по лицам в Yandex Images и поиск по сайту pastebin.com.

        * login_patterns: Ссылки для поиска по возможным логинам. Логины генерируются на основе
          следующих паттернов (в нижнем регистре):
            - имя.фамилия (john.doe)
            - фамилия.имя (doe.john)
            - и.фамилия (j.doe)
            - ф.имя (d.john)
            - имяфамилия (johndoe)
            - фамилияимя (doejohn)
            - ифамилия (jdoe)
            - фимя (djohn)
            - имяф (johnd)
            - имя.ф (john.d)
            - имя_фамилия (john_doe)
            - фамилия_имя (doe_john)
            - имя-фамилия (john-doe)
            - фамилия-имя (doe-john)
            - и_фамилия (j_doe)
            - ф_имя (d_john)
            - и-фамилия (j-doe)
            - ф-имя (d-john)
            - имя (john)
            - фамилия (doe)
            - ... а также все перечисленные варианты с добавлением `date_of_birth` (если `date_of_birth` указан)
              (например, john.doe1980).
          Используются поисковики Google, Bing, Yandex, поиск по email, Facebook, Twitter,
          Instagram, TikTok, Twitch, Imagstodon, WhatsMyName.

        * login_patterns_with_middle: То же, что и `login_patterns`, но с добавлением комбинаций,
          включающих отчество (если оно указано).  Например:
            - johnmiddledoe
            - doejohnmiddle
            - johnmdoe
            - jmdoe
            - doejmd
            - middledoe
            - doemiddle
            - middle
            - ... и те же комбинации с добавлением `date_of_birth`.

        * email_search: Ссылки на поисковые системы для поиска по email адресам, составленным по
          принципу `login@domain`, где `login` берется из `login_patterns` и
          `login_patterns_with_middle` (если применимо), а `domain` - это gmail.com, outlook.com,
          а также dom1, dom2, dom3, dom4, указанные при создании объекта Namint.
          Используются Epieos, Predicta Search, Google, Bing, Yandex.

    Примеры использования:
        # Простой поиск по имени и фамилии:
        namint = Namint(name="Анна", surname="Иванова")
        links = namint.generate_links()
        print(links['name_patterns'])

        # Поиск с отчеством и годом рождения:
        namint = Namint(name="Сергей", middle="Васильевич", surname="Петров", date_of_birth="1985")
        links = namint.generate_links()
        print(links['login_patterns_with_middle'])

        # Поиск с указанием дополнительных доменов:
        namint = Namint(name="Елена", surname="Смирнова", dom1="company.com", dom2="mail.ru")
        links = namint.generate_links()
        print(links['email_search'])

        # Полный вывод всех сгенерированных ссылок:
        namint = Namint(name="John", middle="Middle", surname="Doe", date_of_birth="123", dom1="example.net")
        for category, urls in namint.generate_links().items():
            print(f"--- {category} ---")
            for url in urls:
                print(url)
            print()

    Важно:
        - Имя (`name`) и фамилия (`surname`) обязательны.
        - Параметры `dom1`, `dom2`, `dom3`, `dom4` позволяют добавить дополнительные домены для
          поиска по email.
        - Метод `generate_links()` возвращает словарь. Для доступа к спискам ссылок используйте
          ключи словаря (например, `links['name_patterns']`).
    """

    name = "Никита"
    middle_name = ""
    surname = "Устинов"
    namint = Namint(
        name=name,
        middle=middle_name,
        surname=surname,
        date_of_birth="2004",
        dom1="gmail.com",
    )
    links = namint.generate_links()

    with open(f"namint_links_{name}_{surname}.txt", "w", encoding="utf-8") as f:
        f.write(
            "Категории: name_patterns, name_patterns_with_middle, combined_name_search\n"
        )
        f.write("           login_patterns, login_patterns_with_middle, email_search")
        for category, link_list in links.items():
            f.write(f"\n\n--- {category} ---\n\n")
            for link in link_list:
                f.write(f"{link}\n")


if __name__ == "__main__":
    main()
