import os
import datetime
from dotenv import load_dotenv
from discord.ext import commands
from siglfinder import Cours
import discord
import traceback

load_dotenv()
token = os.getenv('DISCORD_TOKEN')
nothing_found_msg = 'Sigle absent de la banque de cours'
sessions = ['hiver', 'été', 'automne']

bot = commands.Bot(command_prefix=';')

@bot.event
async def on_ready():
    print(f'{bot.user} has connected to Discord!')

@bot.command(name='sigle', help='[sigle] | Donne la description du cours.')
async def get_sigle(ctx, sigle: str):
    cours = Cours(sigle)
    success = cours.fetch_description()
    if not success:
        await ctx.send(nothing_found_msg)
    else:
        embed=discord.Embed(
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

@bot.command(name='horaire', help='[session] [année]')
async def get_horaire(ctx, sigle: str, session: str, annee=None):
    if not annee:
        annee = str(datetime.datetime.now().year)
    try:
        index_session = sessions.index(session) + 1
    except ValueError:
        await ctx.send(f'`{session}` n\'est pas une session valide.\n Essayez plutôt `hiver`, `été`, ou `automne`.')

    cours = Cours(sigle)
    try:
        success = cours.fetch_horaire(index_session, annee)
    except Exception:
        err_tace = traceback.format_exc()
        await ctx.send(f':skull: Bon t\'as cassé le bot, voici le message d\'erreur ```{err_tace}```')

    if not success:
        print(cours.url)
        await ctx.send(f'L\'horaire de la session {session} {annee} pour le cours {sigle} n\'est pas encore publié.')
    else:
        embed=discord.Embed(
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

@bot.command(name='img_horaire', help='[sigle] [session]')
async def get_img_horaire(ctx, sigle: str, session: str):
    annee = str(datetime.datetime.now().year)
    try:
        index_session = sessions.index(session) + 1
    except ValueError:
        await ctx.send(f'`{session}` n\'est pas une session valide.\n Essayez plutôt `hiver`, `été`, ou `automne`.')

    cours = Cours(sigle)
    try:
        success = cours.fetch_horaire(index_session, annee)
    except Exception:
        err_tace = traceback.format_exc()
        await ctx.send(f':skull: Bon t\'as cassé le bot, voici le message d\'erreur ```{err_tace}```')

    if not success:
        print(cours.url)
        await ctx.send(f'L\'horaire de la session {session} {annee} pour le cours {sigle} n\'est pas encore publié.')
    else:
        if cours.horaire():
            await ctx.send(file=discord.File('horaire_img.png'))
        else:
            await ctx.send(f'Il y a eu un problème dans la génération d\'image')

bot.run(token)
