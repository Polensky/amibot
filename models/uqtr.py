"""
Module containing functions that fetch data related to UQTR
"""
import re # pylint: disable=no-absolute-import
from enum import Enum
import datetime
import logging
import sys
import requests
import matplotlib.pyplot as plt
import discord
from bs4 import BeautifulSoup
import pandas as pd
from typing import List
from bot_exception import NoResult, WrongArgument
sys.path.insert(0, '..')


# TODO eviter que sa casse pour PIF1005 (chercher les journées plutôt que "du")

LOGGER = logging.getLogger('sigle_logger')
NOTHING_FOUND_MSG = 'Sigle absent de la banque de cours'
WRONG_SESSION = lambda session: f'`{session}` n\'est pas une session valide.' \
                ' Essayez plutôt `hiver`, `été`, ou `automne`.'
NOT_AVAILABLE = lambda sigle, session, annee: f'L\'horaire de la session {session} {annee} ' \
                f'pour le cours {sigle} n\'est pas encore publié.'
class Session(Enum):
    """Enumaration pour les sessions"""
    HIVER = 1
    ETE = 2
    AUTOMNE = 3

    @classmethod
    def from_session_string(cls, session: str):
        """Convert string into session enum equivalent"""
        ses_enum = None
        if session == 'hiver':
            ses_enum = cls.HIVER
        elif session == 'été':
            ses_enum = cls.ETE
        elif session == 'automne':
            ses_enum = cls.AUTOMNE
        return ses_enum

    def __str__(self):
        if self == Session.ETE:
            return "été"
        return self.name.lower() # pylint: disable=no-member


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
    def __init__(self, no: int, horaires: List[Horaire]):
        self.no = no
        self.horaires = horaires


class Cours:
    """
    Objet representant un cours de l'UQTR
    """
    def __init__(self, sigle: str):
        self.sigle = sigle
        self.url = None
        self.titre = None
        self.description = None
        self.departement = None
        self.niveau = None
        self.prealables = []
        self.session = None
        self.annee = None
        self.professor = None
        self.groupes = []

    def fetch_description(self) -> bool:
        """Fetches the course description and sets appropriate attributes.
        return false if it fails
        """
        payload = {'owa_sigle': self.sigle}
        self.url = f'https://oraprdnt.uqtr.uquebec.ca/pls/public/couw001'
        res = requests.get(self.url, params=payload)
        soup = BeautifulSoup(res.text, "html.parser")

        if soup.find('center'):
            # Le sigle n'existe pas
            return False

        self.titre = soup.find('h1', {'class': 'titrepagecours'}).contents[0]
        # Removing a weird character (\xa0)
        self.titre = self.titre[:-1]

        self.description = soup.find('div', {'class': 'textedescription'}).contents[1].text
        self.description = re.sub('\\r ', '\\n', self.description)

        if m := re.search('Préalable', self.description):
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


    def fetch_horaire(self, session: Session, annee: str) -> List[Groupe]:
        """Fetches the course schedule.
        session -- a Session enum
        annee   -- which year to fetch the schedule
        """
        payload = {'owa_sigle': self.sigle, 'owa_anses': f'{annee}{session.value}'}
        self.url = f'https://oraprdnt.uqtr.uquebec.ca/pls/public/actw001f'
        res = requests.get(self.url, params=payload)
        self.url = res.url
        soup = BeautifulSoup(res.text, "html.parser")

        soup_info = soup.find('td', {'class': 'horaireinfo'})
        if not soup_info:
            return False

        self.titre = soup.find('h1', {'class': 'titrepagehorairecours'})
        self.titre = re.sub('\\n', '', self.titre.text)
        self.titre = self.titre.strip()

        professor = soup_info.find('div', {'class': 'enseignants'})
        professor = re.sub('\xa0', '', professor.text)
        self.professor = re.sub('\\n', '', professor).strip()

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

            horaire_court = []
            horaire = []
            for h in horaire_tuple:
                if h not in horaire_court:
                    horaire_court.append(h)
                    horaire.append(Horaire(h[0], h[1], h[2]))

            g_list.append(Groupe(i, horaire))

        self.groupes = g_list

        return True

    def horaire_cours(self) -> bool:
        """Returns the schedule for the current Cours instance."""
        return Cours._horaire_text_table([self])

    @staticmethod
    def _horaire_text_table(cours) -> bool:
        """Gets the schedule as a table."""
        # TODO enlever la partie transparente de l'image

        fig = plt.figure(dpi=250)
        ax = fig.add_subplot(1, 1, 1)

        semaine = {
            '': ['08h30-11h30', '12h00-15h00', '15h30-18h30', '19h00-22h00'],
            'lundi': ['', '', '', ''],
            'mardi': ['', '', '', ''],
            'mercredi': ['', '', '', ''],
            'jeudi': ['', '', '', ''],
            'vendredi': ['', '', '', ''],
        }

        for c in cours:
            for g in c.groupes:
                for h in g.horaires:
                    if h.heure[0] == '8':
                        periode = 0
                    elif h.heure[:2] == '12':
                        periode = 1
                    elif h.heure[:2] == '15':
                        periode = 2
                    elif h.heure[:2] == '19':
                        periode = 3

                    semaine[h.jour][periode] += f'{c.sigle}(GR{g.no}): {h.lieu}\n'

        dc = pd.DataFrame(semaine)

        table = ax.table(
            cellText=dc.values,
            colWidths=[0.1]*len(dc.columns),
            colLabels=dc.columns,
            loc='center',
            cellLoc='center'
        )
        table.set_fontsize(14)
        table.scale(2, 2)
        ax.axis('off')

        ax.patch.set_visible(False)
        fig.patch.set_visible(False)

        plt.savefig('images\\horaire_img.png', bbox_inches='tight', pad_inches=0)

        return True


def my_embed_desciption(sigle: str) -> discord.Embed:
    """Return an embed description of a course"""
    cours = Cours(sigle)
    success = cours.fetch_description()
    if not success:
        raise NoResult(NOTHING_FOUND_MSG)

    embed = discord.Embed(
        title=cours.titre,
        description=cours.description,
        url=cours.url,
        color=0x006534
    )
    embed.add_field(name="Niveau", value=cours.niveau, inline=True)
    embed.add_field(name="Département", value=cours.departement, inline=True)

    if cours.prealables:
        for i, prealable in enumerate(cours.prealables):
            embed.add_field(
                name=f'Préalable {i+1}',
                value=' ou '.join(prealable),
                inline=False
            )
    return embed

def my_embed_horaire(sigle: str, session: str, annee: str) -> discord.Embed:
    """Return an embed schedule of a course"""
    if not annee:
        annee = str(datetime.datetime.now().year)

    sess_enum = Session.from_session_string(session)
    if not sess_enum:
        raise WrongArgument(WRONG_SESSION(session))

    cours = Cours(sigle)
    if cours.fetch_horaire(sess_enum, annee):
        embed = discord.Embed(
            title=cours.titre,
            description=cours.professor,
            url=cours.url,
            color=0x006534
        )
        for groupe in cours.groupes:
            embed.add_field(name="Groupe", value=groupe.no, inline=False)
            for i, horaire in enumerate(groupe.horaires):
                horaire_str = f"{horaire.jour} de {horaire.heure} au {horaire.lieu}"
                embed.add_field(name=f"Horaire {i}", value=horaire_str, inline=True)
    else:
        LOGGER.warning('Bad URL for %s %s for course %s at\n%s', session, annee, sigle, cours.url)
        raise NoResult(NOT_AVAILABLE(sigle, session, annee))

    return embed
