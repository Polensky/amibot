import os
from dotenv import load_dotenv
from discord.ext import commands
from siglfinder import Cours
import discord

load_dotenv()
token = os.getenv('DISCORD_TOKEN')
nothing_found_msg = 'Sigle absent de la banque de cours'

bot = commands.Bot(command_prefix='?')

@bot.event
async def on_ready():
    print(f'{bot.user} has connected to Discord!')

@bot.command(name='sigle')
async def on_message(ctx, sigle):
    cours = Cours(sigle)
    success = cours.fetch_data()
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


bot.run(token)
