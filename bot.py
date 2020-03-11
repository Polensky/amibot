"""
Bot du discord de l'AMI
"""
import os
import json
import datetime
import re
from os import listdir
import traceback
import logging
import requests
from dotenv import load_dotenv
from discord.ext import commands
import discord
from random import randint
from sigle_logger import start_logger
from siglfinder import Cours, Requester


start_logger()
LOGGER = logging.getLogger('sigle_LOGGER')

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')
NOTHING_FOUND_MSG = 'Sigle absent de la banque de cours'
SESSIONS = ['hiver', 'été', 'automne']

bot = commands.Bot(command_prefix=';')

@bot.event
async def on_ready():
    """
    Quand le bot est pret
    """
    LOGGER.warning(f'{bot.user} has connected to Discord!')

@bot.command(name='sigle', help='[sigle] | Donne la description du cours.')
async def get_sigle(ctx, sigle: str):
    """
    Commande pour obtenir la description d'un cours
    """
    cours = Cours(sigle)
    success = cours.fetch_description()
    if not success:
        await ctx.send(NOTHING_FOUND_MSG)
        return

    embed = discord.Embed(
        title=cours.titre,
        description=cours.description,
        url=cours.url,
        color=0x006534
    )
    embed.add_field(name="Niveau", value=cours.niveau, inline=True)
    embed.add_field(name="Département", value=cours.departement, inline=True)

    if hasattr(cours, "prealables"):
        for i, prealable in enumerate(cours.prealables):
            embed.add_field(
                name=f'Préalable {i+1}',
                value=' ou '.join(prealable),
                inline=False
            )
    await ctx.send(embed=embed)

@bot.command(name='horaire', help='[sigle] [session] [année (optionel)]')
async def get_horaire(ctx, sigle: str, session: str, annee=None):
    """
    Obtenir l'horaire d'un cours pour une session et une annee donnee.
    """
    if not annee:
        annee = str(datetime.datetime.now().year)
    try:
        index_session = SESSIONS.index(session) + 1
    except ValueError:
        await ctx.send(f'`{session}` n\'est pas une session valide.\n' \
                ' Essayez plutôt `hiver`, `été`, ou `automne`.')

    cours = Cours(sigle)
    try:
        success = cours.fetch_horaire(index_session, annee)
    except Exception:
        err_tace = traceback.format_exc()
        LOGGER.exception(f'Bot broke:')
        await ctx.send(f':skull: Bon t\'as cassé le bot, ' \
                f'voici le message d\'erreur ```{err_tace}```')

    if not success:
        LOGGER.warning(f'Bad URL for {session} {annee} for course {sigle} at\n{cours.url}')
        await ctx.send(f'L\'horaire de la session {session} {annee} ' \
                f'pour le cours {sigle} n\'est pas encore publié.')
        return

    embed = discord.Embed(
        title=cours.titre,
        description=cours.professor,
        url=cours.url,
        color=0x006534
    )
    if len(cours.horaires) > 1:
        pass
    else:
        jour, heure, lieu = cours.horaires[0]
        horaire_str = jour + ' de ' + heure
        embed.add_field(name="Horaire", value=horaire_str, inline=True)
        embed.add_field(name="Lieu", value=lieu, inline=True)

    await ctx.send(embed=embed)

@bot.command(name='img_horaire', help='[session] [sigles séparés par des espaces]')
async def get_img_horaire(ctx, session: str, *sigles: str):
    """
    Commande pour obtenir une image de l'horaire de plusieurs cours.
    """
    annee = str(datetime.datetime.now().year)
    try:
        index_session = SESSIONS.index(session) + 1
    except ValueError:
        await ctx.send(f'`{session}` n\'est pas une session valide.\n' \
                ' Essayez plutôt `hiver`, `été`, ou `automne`.')

    fail_lst = []
    cours_lst = []
    for sigle in sigles:
        cours = Cours(sigle)
        try:
            if cours.fetch_horaire(index_session, annee):
                cours_lst.append(cours)
            else:
                fail_lst.append(cours)
        except Exception:
            err_tace = traceback.format_exc()
            LOGGER.exception(f'Bot broke:')
            await ctx.send(f':skull: Bon t\'as cassé le bot, ' \
                    f'voici le message d\'erreur ```{err_tace}```')

    if fail_lst:
        for fail in fail_lst:
            LOGGER.warning(f'Bad URL for {session} {annee} for course {fail.sigle} at\n{fail.url}')
            await ctx.send(f'L\'horaire de la session {session} {annee} ' \
                    f'pour le cours {fail.sigle} n\'est pas encore publié.')

    if Cours._horaire_text_table(cours_lst):
        await ctx.send(file=discord.File('horaire_img.png'))
    else:
        LOGGER.error('Image generation failed.')
        await ctx.send(f'Il y a eu un problème dans la génération d\'image')

@bot.command(name='zen', help='Zen')
async def zen(ctx, color='006534'):
    """
    ZEN
    """
    if len(color) == 6:
        color = f'0x{color}'
        try:
            color = int(color, 16)
        except ValueError:
            await ctx.send('Use valid hex strings you animal!')
            color = 0x006534
    else:
        await ctx.send('Use valid hex strings you animal!')
        color = 0x006534

    embed = discord.Embed(
        title='Zen of Python',
        description=Requester.zen(),
        url='https://www.python.org/dev/peps/pep-0020/',
        color=color
    )
    await ctx.send(embed=embed)

@bot.command(name='pep', help='[pep number]')
async def pep(ctx, num: int, color='006534'):
    """
    Fetch les informations d'un pep.
    """
    if num > 9999:
        await ctx.send('There aren\'t that many peps!')
        return

    if len(color) <= 6:
        try:
            color = int(color, 16)
        except ValueError:
            await ctx.send('Use valid hex strings you animal!')
            color = 0x006534
    else:
        await ctx.send('Use valid hex strings you animal!')
        color = 0x006534

    if pep := Requester.anypep(num):
        embed = discord.Embed(
            title=pep.pep,
            description=pep.desc,
            url=pep.URL,
            color=color
        )
        embed.set_author(name=pep.author)
        embed._fields = pep.fields
        await ctx.send(embed=embed)
    else:
        await ctx.send(f'Pep{num} does not exist!')

@bot.command(name='todo', help='Lists bot TODOs')
async def todo(ctx):
    """
    Affiche tous les TODO dans le code.
    """
    py_files = [f for f in listdir('./') if '.py' in f]

    for py in py_files:
        with open(py, 'r') as f:
            todos = [f'line {i}: {t[0]}' for i, line in enumerate(f.readlines()) if (t := re.findall(r'^(?:\s+)?#(?:\s+)?TODO\s+(.*)$', line))]

            if todos:
                embed = discord.Embed(
                    title=f'{py}',
                    description='DO:\n\n' + '\n\n'.join(todos),
                    url=f'https://dmigit.uqtr.ca/siroisc/sigle_finder/blob/master/{py}',
                    color=randint(0, 16777216)
                )
                await ctx.send(embed=embed)

@bot.command(name='corona', help='COVID-19')
async def corona(ctx):
    """
    C O R O N A
    """
    res = requests.get('https://coronavirus-tracker-api.herokuapp.com/all')
    j = json.loads(res.content)
    confirmed = j['latest']['confirmed']
    deaths = j['latest']['deaths']
    recovered = j['latest']['recovered']
    embed = discord.Embed(
        title=f':beer: Corona update :skull:',
        url='https://www.arcgis.com/apps/opsdashboard/index.html#/bda7594740fd40299423467b48e9ecf6',
        color=0x006534
    )
    embed.add_field(name="Confirmés", value=confirmed)
    embed.add_field(name="Morts", value=deaths)
    embed.add_field(name="Rétablis", value=recovered)
    await ctx.send(embed=embed)


bot.run(TOKEN)

# TODO make this line work with keyboardinterrupt. Catching seems to cause bot problems.
LOGGER.info('Bot shut down')
