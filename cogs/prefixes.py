from discord.ext import commands
import discord
import random
import sqlite3

class prefixes(commands.Cog):
    def __init__(self,bot):
        self.bot = bot
  
    def getRandomColour(self):
        hex_values = ["a","b","c","d","e","f","1","2","3","4","5","6","7","8","9"]
        colour = ""
        for number in range(6):
            colour += random.choice(hex_values)
        return eval(f"0x{colour}")
    
    async def determine_prefixes(self,message):
        dbase = sqlite3.connect("config.db")
        cursor = dbase.cursor()
        cursor.execute("SELECT prefix FROM prefix WHERE guild_id == ?", [str(message.guild.id)])
        if (custom_prefix := cursor.fetchone()) is not None:
            return custom_prefix[0]
        else:
            return "-"
  
  
    @commands.command(brief = "Changes the prefix of the bot. Requires `Manage Server` permission.", help = "Change the prefix by invoking the command `prefix <new prefix>`, where `<new prefix>` is your new prefix (duh).\nIf you want to have the prefix end with a space, add quotation marks around the prefix and a space, such as `\"pls \"`")
    async def prefix(self,ctx,*custom_prefix):
        new_prefix = " ".join(custom_prefix)
        
        #checks for perms
        if not ctx.channel.permissions_for(ctx.author).manage_guild:
            await ctx.channel.send("You don't have the `Manage Server` permission.")
            return
        
        #checks if prefix is empty
        if new_prefix == "":
            await ctx.channel.send("Please type in a prefix.")
            return
        

        dbase = sqlite3.connect("config.db")
        cursor = dbase.cursor()
        cursor.execute("SELECT prefix FROM prefix WHERE guild_id == ?", [str(ctx.guild.id)])

        if cursor.fetchone() is None:
            cursor.execute("INSERT INTO prefix (guild_id, prefix) VALUES (?, ?)", [str(ctx.guild.id), new_prefix])
        else:
            cursor.execute("UPDATE prefix SET prefix = ? WHERE guild_id == ?", [new_prefix, str(ctx.guild.id)])

        dbase.commit()
        dbase.close()
        await ctx.channel.send(f"Prefix set to `{new_prefix}`")

    # if somehow things get messed up
    @prefix.error
    async def prefix_error(self,ctx,error):
        print(error)
        await ctx.send("What even-")
    
    def valid_channels(self, message):     
        dbase = sqlite3.connect("config.db")
        cursor = dbase.cursor()
        cursor.execute("SELECT enabled, disabled FROM config WHERE guild_id == ?", [str(message.guild.id)])
        
        channels = cursor.fetchone()
        if channels is None:
            return True
        enabled, disabled = channels

        if enabled == "all":
            return not str(message.channel.id) in disabled
        return str(message.channel.id) in enabled
    
    
    @commands.Cog.listener()
    async def on_message(self,message):
        if not self.valid_channels(message):
            return
        if message.content == "<@779219582300586014>" or message.content == "<@!779219582300586014>":

            prefix_embed = discord.Embed(
                title = "The Cracker's prefix",
                description = f"Prefix for this server is: `{await self.determine_prefixes(message)}`",
                colour = self.getRandomColour()
            )

            prefix_embed.add_field(
                name = "How to change the prefix",
                value = "Type <@!779219582300586014> `prefix <prefix>`, where `<prefix>` is your new prefix.",
                inline = False
            )
            
            await message.channel.send(embed = prefix_embed)
        
        elif message.content.startswith("<@779219582300586014> prefix") or message.content.startswith("<@!779219582300586014> prefix"):
            await self.prefix(message," ".join(message.content.split()[2:]))


def setup(bot):
    bot.add_cog(prefixes(bot))