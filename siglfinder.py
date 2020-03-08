import re
import requests
import pandas as pd
import matplotlib.pyplot as plt
from bs4 import BeautifulSoup

#TODO eviter que sa casse pour des cours comme SIF1040, PIF1005
#TODO gerer les cours avec plusieurs groupes (ex.: ADM1016 hiv 2020)

class Cours:

    def __init__(self, sigle):
        self.sigle = sigle

    def fetch_description(self) -> bool:
        """
        Fetches the course description and sets appropriate attributes.
        """
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


    def fetch_horaire(self, session_index, annee) -> bool:
        """
        Fetches the course schedule.
        """
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
            lieu = lieu.strip()

            self.horaires = [(jour, heure, lieu)]
        return True

    def horaire_cours(self) -> bool:
        """
        Returns the schedule for the current Cours instance.
        """
        return Cours._horaire_text_table([self])

    @staticmethod
    def _horaire_text_table(cours) -> bool:
        """
        Gets the schedule as a table.
        """
        # TODO enlever la partie transparente de l'image

        fig = plt.figure(dpi=250)
        ax = fig.add_subplot(1,1,1)

        semaine = {
            '': ['08h30-11h30', '12h00-15h00', '15h30-18h30', '19h00-22h00'],
            'lundi': ['','','', ''],
            'mardi': ['','','', ''],
            'mercredi': ['','','', ''],
            'jeudi': ['','','', ''],
            'vendredi': ['','','', ''],
        }

        for c in cours:
            for h in c.horaires:
                jour, heure, lieu = h

                if heure[:2] == '08':
                    periode = 0
                elif heure[:2] == '12':
                    periode = 1
                elif heure[:2] == '15':
                    periode = 2
                elif heure[:2] == '19':
                    periode = 3

                semaine[jour][periode] += f'{c.sigle}: {lieu}\n'

        dc = pd.DataFrame(semaine)

        dc = pd.DataFrame(semaine)

        table = ax.table(
            cellText=dc.values,
            colWidths=[0.1]*len(dc.columns),
            colLabels=dc.columns,
            loc='center',
            cellLoc='center'
        )
        table.set_fontsize(14)
        table.scale(2,2)
        ax.axis('off')

        ax.patch.set_visible(False)
        fig.patch.set_visible(False)

        plt.savefig('horaire_img.png', bbox_inches='tight', pad_inches=0)

        return True
