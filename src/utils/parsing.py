import re


def extract_phone_number(text):
    """Возвращает очищенный номер телефона формата +1234567890"""
    match = re.search(r"(\+?\d{1,3}[-.\s]?)?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}", text)
    if match:
        cleaned_number = re.sub(r"[^0-9]", "", match.group(0))
        return cleaned_number
    return None


def is_valid_ip(ip_address: str) -> bool:
    pattern = r"^(\d{1,3}\.){3}\d{1,3}$"
    if re.match(pattern, ip_address):
        octets = ip_address.split(".")
        return all(0 <= int(octet) <= 255 for octet in octets)
    return False


def extract_email(text):
    match = re.search(r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}", text)
    if match:
        return match.group(0)
    return None


def extract_vk_link(text):
    match = re.search(r"https?://vk\.com/([a-zA-Z0-9_.]+)", text)
    if match:
        return match.group(1)

    match = re.search(r"vk\.com/([a-zA-Z0-9_.]+)", text)
    if match:
        return match.group(1)

    if text.isdigit():
        return text

    if re.match(r"^[a-zA-Z0-9_.]+$", text):
        return text

    return None
