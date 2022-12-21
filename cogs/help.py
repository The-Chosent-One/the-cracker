from discord.ext import commands
import discord
import random


class help(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    def getRandomColour(self):
        hex_values = ["a", "b", "c", "d", "e", "f", "1", "2", "3", "4", "5", "6", "7", "8", "9"]
        colour = ""
        for number in range(6):
            colour += random.choice(hex_values)
        return eval(f"0x{colour}")

    async def send_command_help(self, ctx, command):
        if not command in [c.name for c in ctx.bot.commands]:
            await ctx.send("That command doesn't exist")
            return
    
        specific_command_embed = discord.Embed(
            title = f"Help for {command}",
            colour = 0x3f51b5
        )

        specific_command_embed.add_field(
            name = "Usage for command and options",
            value = [c.help for c in ctx.bot.commands if c.name == command][0],
            inline = False
        )

        await ctx.send(embed = specific_command_embed)



    @commands.command(help = "Shows you the commands that can be used.\n(Pretty self-explanitory, I mean you used the help command to get here)", hidden = True)
    async def help(self, ctx, *command):
    
        async with ctx.typing():
            pass
        
        if command != ():
            return await self.send_command_help(ctx, command[0])

        p = self.bot.get_cog("prefixes")

        embed_help = discord.Embed(
            title = "The Cracker's help",
            description = 
            f"List of commands that can be used. The current prefix is `{await p.determine_prefixes(ctx)}`",
            colour = self.getRandomColour())

        embed_help.add_field(
            name = "Blackjack statistics",
            value = "Provides blackjack statistics on your blackjack games. This is not a command and can only be invoked by playing blackjack",
            inline = False
        )
        
        for command in ctx.bot.walk_commands():
            if not command.hidden:
                embed_help.add_field(
                    name = command,
                    value = command.brief, 
                    inline = True
                )


        embed_help.set_footer(text = "Email [REDACTED] for any issues with the bot")
        await ctx.send(embed = embed_help)


def setup(bot):
    bot.add_cog(help(bot))