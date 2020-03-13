"""
Module containing functions that fetch data related to python
"""
import requests
from bs4 import BeautifulSoup


class Pep:
    def __init__(self, pep: str, desc: str, author: str, URL: str, fields=[]):
        self.pep = pep
        self.desc = desc
        self.author = author
        self.URL = URL
        self.fields = fields

class Requester:
    @staticmethod
    def zen() -> str:
        """
        Gets the Zen of Python
        """
        res = requests.get('https://www.python.org/dev/peps/pep-0020/')

        soup = BeautifulSoup(res.text, 'html.parser')
        zen = soup.find('pre', {'class': 'literal-block'})
        zen = zen.text.strip('\n')

        return zen

    @staticmethod
    def anypep(num: int) -> Pep:
        """
        Returns any pep desired
        """
        num = str(num)
        while len(num) < 4:
            num = '0' + num

        pep_url = f'https://www.python.org/dev/peps/pep-{num}/'

        res = requests.get(pep_url)

        if res.status_code == 404:
            return None

        soup = BeautifulSoup(res.text, 'html.parser')
        pep_table = soup.find('tbody')
        field_names = [name.text for name in pep_table.findChildren('th', {'class': 'field-name'})]
        field_bodies = [body.text for body in pep_table.findChildren('td', {'class': 'field-body'})]

        table_dict = dict(zip(field_names, field_bodies))

        pep = Pep(f'Pep{table_dict.pop("PEP:")}', table_dict.pop('Title:'), table_dict.pop('Author:'), pep_url)

        pep.fields = [{'inline': False, 'name': name, 'value': body} for name, body in table_dict.items() if body]

        return pep
