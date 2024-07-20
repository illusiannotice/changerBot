from xml.etree import ElementTree as et
import redis
import requests


class Updater:
    @staticmethod
    def update() -> None:
        print("updating...")
        _redis_cli = redis.Redis(host="redis", port=6379)
        _redis_cli.flushall()
        _redis_cli.set("RUB", 1)
        _char_codes = []
        _values = []
        _response = requests.get("https://cbr.ru/scripts/XML_daily.asp")
        with open("data.xml", "wb") as data:
            data.write(_response.content)
        _tree = et.parse("data.xml")
        _root = _tree.getroot()

        for name in _root.findall("./Valute/CharCode"):
            _char_codes.append(name.text.lower())

        for rate in _root.findall("./Valute/VunitRate"):
            _values.append(rate.text.lower())

        for i in range(len(list(_char_codes))):
            _redis_cli.set(name=str(_char_codes[i]), value=str(_values[i]))
        _redis_cli.close()
