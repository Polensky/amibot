import re
import sys
import urllib.request
import requests
import texttable as tt
from bs4 import BeautifulSoup

#TODO eviter que sa casse pour des cours comme SIF1040, PIF1005
#TODO gerer les cours avec plusieurs groupes (ex.: ADM1016 hiv 2020)

class Cours:

    def __init__(self, sigle):
        self.sigle = sigle

    def fetch_description(self):
        self.url = f'https://oraprdnt.uqtr.uquebec.ca/pls/public/couw001?owa_type=P&owa_sigle={self.sigle}'
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


    def fetch_horaire(self, session_index, annee):
        self.url= f'https://oraprdnt.uqtr.uquebec.ca/pls/public/actw001f?owa_sigle={self.sigle}&owa_anses={annee}{session_index}&owa_apercu=N'
        res = requests.get(self.url)
        soup = BeautifulSoup(res.text, "html.parser")

        soup_info = soup.find('td', {'class': 'horaireinfo'})
        soup_horaire = soup.find('td', {'class': 'horairedates'})
        if not soup_info:
            return False

        self.titre = soup.find('h1', {'class': 'titrepagehorairecours'})
        self.titre = re.sub('\\n', '', self.titre.text)
        self.titre = self.titre.strip()

        professor = soup_info.find('div', {'class': 'enseignants'})
        professor = re.sub('\xa0', '', professor.text)
        self.professor = re.sub('\\n', '', professor).strip()

        horaires = soup_horaire.find_all('tr')
        if len(horaires) > 2:
            pass # treat all row
        else:
            jour = soup_horaire.find('strong').text

            heure = soup_horaire.find('td', {'class': 'heure'})
            heure = re.sub('\xa0', '', heure.text)
            heure = re.sub('\\n', '', heure)

            lieu = soup_horaire.find('td', {'class': 'heure'}).find_next().text
            lieu = self.lieu.strip() 

            self.horaires = [(jours, heure, lieu)]
        return True

    def horaire(self):
        return Cours._horaire_text_table(self.jour, self.heure, self.lieu)

    @staticmethod
    def _horaire_text_table(jour, heure, lieu):
        if heure[:2] == '08':
            periode = 1
        elif heure[:2] == '12':
            periode = 2
        elif heure[:2] == '15':
            periode = 3
        elif heure[:2] == '19':
            periode = 4

        if jour == 'lundi':
            le_jour = 1
        elif jour == 'mardi':
            le_jour = 2
        elif jour == 'mercredi':
            le_jour = 3
        elif jour == 'jeudi':
            le_jour = 4
        elif jour == 'vendredi':
            le_jour = 5

        horaire_template = [['           ','Lundi','Mardi','Mercredi', 'Jeudi', 'Vendredi'],
                            ['08h30-11h30','     ','     ','        ', '     ', '        '],
                            ['12h00-15h00','     ','     ','        ', '     ', '        '],
                            ['15h30-18h30','     ','     ','        ', '     ', '        '],
                            ['19h00-22h00','     ','     ','        ', '     ', '        '],]

        horaire_template[periode][le_jour] = lieu
        table = tt.Texttable()
        table.set_chars(['⋯','|','⊕','⋯'])
        table.add_rows(horaire_template)
        return table.draw()
