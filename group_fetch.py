from bs4 import BeautifulSoup
import requests
import re

class Horaire:
    """
    Objet représentant l'horaire d'un groupe
    """
    def __init__(self, jour: str, heure: str, lieu: str):
        self.jour = jour
        self.heure = heure
        self.lieu = lieu


class Groupe:
    """
    Objet représentant un groupe dans un cours
    """
    def __init__(self, no: int, horaires: list):
        self.no = no
        self.horaires = horaires


def fetch_horaire():
    """Fetches the course schedule.
    session -- a Session enum
    annee   -- which year to fetch the schedule
    """
    #url = f'https://oraprdnt.uqtr.uquebec.ca/pls/public/actw001f?owa_sigle=INF1010&owa_anses=20203&owa_type=C&owa_apercu=N&owa_type_rech=D&owa_valeur_rech=1800'
    #url = f'https://oraprdnt.uqtr.uquebec.ca/pls/public/actw001f?owa_sigle=ADM1016&owa_anses=20201&owa_type=C&owa_apercu=N'
    url = f'https://oraprdnt.uqtr.uquebec.ca/pls/public/actw001f?owa_sigle=sif1040&owa_anses=20201'
    res = requests.get(url)

    soup = BeautifulSoup(res.text, "html.parser")

    soup_groupe = soup.find_all('table', {'class': 'dateshoraire'})

    g_list = []

    for i, s_group in enumerate(soup_groupe):
        horaire_tuple = []

        soup_horaire = s_group.find_all('tr')[1:]
        for s_horaire in soup_horaire:
            jour = s_horaire.find('td').text.split()[0]

            heure = s_horaire.find('td', {'class': 'heure'})
            heure = re.sub('\xa0', '', heure.text)
            heure = re.sub('\\n', '', heure)

            lieu = s_horaire.find('td', {'class': 'heure'}).find_next().text
            lieu = lieu.strip()

            horaire_tuple.append((jour, heure, lieu))

        print(horaire_tuple)
        horaire_court = []
        horaire = []
        for h in horaire_tuple:
            if h not in horaire_court:
                horaire_court.append(h)
                horaire.append(Horaire(h[0], h[1], h[2]))

        #horaire = [Horaire(h[0], h[1], h[2]) for h in horaire_court]

        g_list.append(Groupe(i, horaire))

    return g_list

try:
    groupes = fetch_horaire()

    for groupe in groupes:
        print(f'Groupe {groupe.no}:')
        [print(f'Jour: {h.jour}, Heure: {h.heure}, Lieu: {h.lieu}') for h in groupe.horaires]
finally:
    input('the end')
