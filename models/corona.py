"""C O R O N A"""
import json
import requests
import discord


def my_embed() -> discord.Embed:
    """Generate embed for corona command"""
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

    return embed
