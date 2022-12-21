import discord
import time
import asyncio
import sqlite3
import sys
import traceback
from discord.ext import commands

async def determine_prefixes(self,message):
    dbase = sqlite3.connect("config.db")
    cursor = dbase.cursor()
    cursor.execute("SELECT prefix FROM prefix WHERE guild_id == ?", [str(message.guild.id)])
    if (custom_prefix := cursor.fetchone()) is not None:
        return custom_prefix[0]
    else:
        return "-"


bot = discord.AutoShardedClient()
bot = commands.Bot(command_prefix = determine_prefixes)
bot.remove_command('help')

cogs = ["cogs.help","cogs.prefixes","cogs.suggestions", "cogs.partnerBots", "cogs.serverConfigurations", "cogs.betLogger"]

async def changeStatus():
    await bot.wait_until_ready()
    while True:
        guildCount = len(bot.guilds)
        memberCount = sum((guild.member_count for guild in bot.guilds))
        await bot.change_presence(activity = discord.Activity(type = discord.ActivityType.watching, name = f"{'{:,}'.format(memberCount)} members in {guildCount} servers"))

        await asyncio.sleep(300)

@bot.event
async def on_ready():
    print("I'm alive")
  
    for cog in cogs:
        bot.load_extension(cog)

@bot.check
def valid_channels(ctx):
    if ctx.command.name in ("help", "serverconfig"):
        return True
    
    dbase = sqlite3.connect("config.db")
    cursor = dbase.cursor()
    cursor.execute("SELECT enabled, disabled FROM config WHERE guild_id == ?", [str(ctx.guild.id)])
    channels = cursor.fetchone()
    if channels is None:
        return True
    enabled, disabled = channels

    if enabled == "all":
        return not str(ctx.channel.id) in disabled
    return str(ctx.channel.id) in enabled
        
@bot.event
async def on_command_error(ctx, error):
    # This prevents any commands with local handlers being handled here in on_command_error.
    if hasattr(ctx.command, 'on_error'):
        return

    # This prevents any cogs with an overwritten cog_command_error being handled here.
    cog = ctx.cog
    if cog:
        if cog._get_overridden_method(cog.cog_command_error) is not None:
            return

    ignored = (commands.CommandNotFound, commands.errors.CheckFailure)

    # Allows us to check for original exceptions raised and sent to CommandInvokeError.
    # If nothing is found. We keep the exception passed to on_command_error.
    error = getattr(error, 'original', error)

    # Anything in ignored will return and prevent anything happening.
    if isinstance(error, ignored):
        return

    else:
        # All other Errors not returned come here. And we can just print the default TraceBack.
        print('Ignoring exception in command {}:'.format(ctx.command), file=sys.stderr)
        traceback.print_exception(type(error), error, error.__traceback__, file=sys.stderr)

@bot.command(hidden = True)
async def ping(ctx):
    await ctx.send(f"Pong! Took {round(bot.latency*1000,2)}ms")


@bot.command(brief = "Invite links for the bot and support server", help = "Invite links for the bot and support server(I mean it's pretty self-explanatory)", aliases = ("inv","i"))
async def invite(ctx):
    invite_embed = discord.Embed(
        title = "Invite links",
        description = "Thank you for using this bot!\nHere's the invite link for [the bot]([REDACTED])\nHere's the invite link for [the support server]([REDACTED]) as well",
        colour = 0x3f51b5
    )
    await ctx.author.send(embed = invite_embed)
    await ctx.send(f"{ctx.author.mention}, I've sent a DM to you!")

@bot.command(help = "Invite link for the support server", hidden = True)
async def support(ctx):
    support_embed = discord.Embed(
        title = "Invite links",
        description = "Here's the invite link for [the support server]([REDACTED])",
        colour = 0x3f51b5
    )
    await ctx.author.send(embed = support_embed)
    await ctx.send(f"{ctx.author.mention}, I've sent a DM to you!")

@bot.command(hidden = True)
async def bigGuilds(ctx):
    if ctx.author.id == 531317158530121738:
        payload = ""
        for guild in bot.guilds:
            if guild.member_count > 10000:
                payload += f"{guild.name} {guild.member_count}\n"
        await ctx.send(payload)

@bot.command(hidden = True)
async def reload_cog(ctx, *, cog_name):
    if ctx.author.id != 531317158530121738:
        return
    bot.reload_extension(cog_name)
    await ctx.send("Reloaded")
    
bot.loop.create_task(changeStatus())
bot.run("REDACTED")