"""
Bot du discord de l'AMI
"""
import os # pylint: disable=no-absolute-import
import datetime
import re
import json
from random import randint
import logging
from os import listdir
import traceback
from dotenv import load_dotenv
from discord.ext import commands
import discord
import setproctitle
from sigle_logger import start_logger
from models.uqtr import Cours, Session
from models.pep import Requester
from bot_exception import WrongArgument, NoResult
import models.corona as coro
import models.uqtr as uqtr


setproctitle.setproctitle('amibot') # pylint: disable=c-extension-no-member
start_logger()
LOGGER = logging.getLogger('sigle_logger')

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')

bot = commands.Bot(command_prefix=';')

@bot.event
async def on_ready():
    """Quand le bot est pret"""
    LOGGER.warning('%s has connected to Discord!', bot.user)

@bot.command(name='sigle', help='[sigle] | Donne la description du cours.')
async def get_sigle(ctx, sigle: str):
    """Commande pour obtenir la description d'un cours"""
    try:
        embed = uqtr.my_embed_desciption(sigle)
    except (WrongArgument, NoResult) as error:
        await ctx.send(error)
        return
    await ctx.send(embed=embed)

@bot.command(name='horaire', help='[sigle] [session] [année (optionel)]')
async def get_horaire(ctx, sigle: str, session: str, annee=None):
    """Obtenir l'horaire d'un cours pour une session et une annee donnee."""
    try:
        embed = uqtr.my_embed_horaire(sigle, session, annee)
    except (WrongArgument, NoResult) as error:
        await ctx.send(error)
        return
    await ctx.send(embed=embed)

@bot.command(name='img_horaire', help='[session] [sigles séparés par des espaces]')
async def get_img_horaire(ctx, session: str, *sigles: str):
    """Commande pour obtenir une image de l'horaire de plusieurs cours."""
    annee = str(datetime.datetime.now().year)
    sess_enum = Session.from_session_string(session)
    if not sess_enum:
        await ctx.send(f'`{session}` n\'est pas une session valide.\n' \
                ' Essayez plutôt `hiver`, `été`, ou `automne`.')

    fail_lst = []
    cours_lst = []
    for sigle in sigles:
        cours = Cours(sigle)
        try:
            if cours.fetch_horaire(sess_enum, annee):
                cours_lst.append(cours)
            else:
                fail_lst.append(cours)
        except Exception: # pylint: disable=broad-except
            err_tace = traceback.format_exc()
            LOGGER.exception('Bot broke:')
            await ctx.send(f':skull: Bon t\'as cassé le bot, ' \
                    f'voici le message d\'erreur ```{err_tace}```')

    if fail_lst:
        for fail in fail_lst:
            LOGGER.warning(
                'Bad URL for %s %s for course %s at\n%s', session, annee, fail.sigle, fail.url
                )
            await ctx.send(f'L\'horaire de la session {session} {annee} ' \
                    f'pour le cours {fail.sigle} n\'est pas encore publié.')

    if Cours._horaire_text_table(cours_lst): # pylint: disable=protected-access
        await ctx.send(file=discord.File('horaire_img.png'))
    else:
        LOGGER.error('Image generation failed.')
        await ctx.send(f'Il y a eu un problème dans la génération d\'image')

@bot.command(name='zen', help='Zen')
async def zen(ctx, color='006534'):
    """ZEN"""
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
    """Fetch les informations d'un pep."""
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

    if req_pep := Requester.anypep(num):
        embed = discord.Embed(
            title=req_pep.pep,
            description=req_pep.desc,
            url=req_pep.URL,
            color=color
        )
        embed.set_author(name=req_pep.author)
        embed._fields = req_pep.fields
        await ctx.send(embed=embed)
    else:
        await ctx.send(f'Pep{num} does not exist!')

@bot.command(name='todo', help='Lists bot TODOs')
async def todo(ctx):
    """
    Affiche tous les TODO dans le code.
    """
    py_dirs = ['./', './models/']
    py_files = []
    for d in py_dirs:
        py_files += [f'{d}{f}' for f in listdir(d) if '.py' in f]

    for py in py_files:
        with open(py, 'r') as f:
            todos = [
                f'line {i}: {t[0]}'
                for i, line in enumerate(f.readlines())
                if (t := re.findall(r'^(?:\s+)?#(?:\s+)?TODO\s+(.*)$', line))
            ]

            if todos:
                embed = discord.Embed(
                    title=f'{py[2:]}',
                    description='DO:\n\n' + '\n\n'.join(todos),
                    url=f'https://dmigit.uqtr.ca/siroisc/sigle_finder/blob/master/{py}',
                    color=randint(0, 16777216)
                )
                await ctx.send(embed=embed)

@bot.command(name='corona', help='COVID-19')
async def corona(ctx):
    """ C O R O N A """
    await ctx.send(embed=coro.my_embed())

# @bot.command(name='ccr')
# async def ccr(ctx):
#     if ctx.message.author.guild_permissions.administrator:
#         info_sigle = ['INF', 'SMI', 'PIF', 'SDD', 'SIF']
#         math_sigle = ['ALG', 'MAP', 'MPU', 'STT', 'PMA', 'ROP', 'EMA', 'GEM']
#         courses = json.load(open('out.json'))
#         category_info = discord.utils.get(ctx.guild.categories, name="Cours d'informatique")
#         category_math = discord.utils.get(ctx.guild.categories, name="Cours de mathématiques")
#         for cour in courses:
#             channel_name = f'{cour["sigle"]} {cour["name"]}'
#             channel_topic = f'Niveau: {cour["annee"]}'
#             if 'prealables' in cour:
#                 channel_topic += f' Préalables: {" ".join(cour["prealables"][0])}'
#             if cour['sigle'][:3] in info_sigle:
#                 if category_info:
#                     channel = await ctx.guild.create_text_channel(
#                         channel_name,
#                         topic=channel_topic,
#                         category=category_info
#                     )
#                     embed = discord.Embed(title=cour['name'], description=cour['description'])
#                     msg = await channel.send(embed=embed)
#                     await msg.pin()
#             if cour['sigle'][:3] in math_sigle:
#                 if category_info:
#                     channel = await ctx.guild.create_text_channel(
#                         channel_name,
#                         topic=channel_topic,
#                         category=category_math
#                     )
#                     embed = discord.Embed(title=cour['name'], description=cour['description'])
#                     msg = await channel.send(embed=embed)
#                     await msg.pin()
# 
# @bot.command(name='ccrd')
# async def ccrd(ctx):
#     if ctx.message.author.guild_permissions.administrator:
#         category_info = discord.utils.get(ctx.guild.categories, name="Cours d'informatique")
#         category_math = discord.utils.get(ctx.guild.categories, name="Cours de mathématiques")
#         for chan in ctx.guild.text_channels:
#             if chan.category in (category_info, category_math):
#                 await chan.delete()


try:
    bot.run(TOKEN)
finally:
    LOGGER.warning('Bot shut down')
