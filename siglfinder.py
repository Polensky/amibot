import re
import sys
import urllib.request
import requests
from bs4 import BeautifulSoup


class Cours:

    def __init__(self, sigle):
        self.sigle = sigle
        self.url = f'https://oraprdnt.uqtr.uquebec.ca/pls/public/couw001?owa_type=P&owa_sigle={sigle}'

    def fetch_data(self):
        res = requests.get(self.url)
        soup = BeautifulSoup(res.text, "html.parser")

        if soup.find('center'):
            # Le sigle n'existe pas
            return False

        self.titre = soup.find('h1', {'class': 'titrepagecours'}).contents[0]
        # Removing a weird character (\xa0)
        self.titre = self.titre[:-1] 

        self.description = soup.find('div', {'class': 'textedescription'}).contents[1].text
        self.description = re.sub('\\r ', '\\n', self.description)

        m = re.search('Préalable', self.description)
        if m:
            self.description = self.description[:m.start()]

            desc = soup.find('div', {'class': 'textedescription'})
            all_prea = desc.find_all('strong')
            self.prealables = [[] for _ in all_prea]
            for i, prea in enumerate(all_prea):
                for sigl in prea.find_next().find_all('a'):
                    self.prealables[i].append(sigl.text)

        self.niveau = soup.find_all('table')[1].find_all('td')[1].text
        self.departement = soup.find_all('table')[1].find_all('td')[3].text
        return True
