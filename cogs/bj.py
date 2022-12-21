from discord.ext import commands
import discord
import sqlite3

class bj(commands.Cog):
    def __init__(self,bot):
        self.bot = bot
    
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
    
    def disabled_stats(self, name):
        dbase = sqlite3.connect("blackjack_disable.db")
        cursor = dbase.cursor()
        cursor.execute("SELECT user_name FROM disabled_stats WHERE user_name == ? ", [name])
        result = cursor.fetchone() is not None
        dbase.close()
        return result

    @commands.command(brief = "Toggles blackjack statistics on and off", help = "Toggles blackjack statistics on and off.\nDo note that the statistics disabling are tagged to your name. If you do happen to change it, make sure to run this command again to update the name change.", aliases = ["bj", "blackj"])
    async def blackjack(self, ctx):
        dbase = sqlite3.connect("blackjack_disable.db")
        cursor = dbase.cursor()
        cursor.execute("SELECT user_name FROM disabled_stats WHERE user_name == ? AND user_id == ?", [ctx.author.name, ctx.author.id])
        name_in_db = cursor.fetchone()
        
        if name_in_db is None:
            cursor.execute("INSERT INTO disabled_stats (user_name, user_id) VALUES (?, ?)", [ctx.author.name, ctx.author.id])
            dbase.commit()
            dbase.close()
            return await ctx.reply("Blackjack statistics disabled")
        
        elif name_in_db[0] != ctx.author.name:
            cursor.execute("UPDATE disabled_stats SET user_name = ? WHERE user_id == ?", [ctx.author.name, ctx.author.id])
            dbase.commit()
            dbase.close()
            return await ctx.reply("Updated your name to reflect the name change, blackjack statistics are still disabled")
        
        else:
            cursor.execute("DELETE FROM disabled_stats WHERE user_id == ?", [ctx.author.id])
            dbase.commit()
            dbase.close()
            return await ctx.reply("Blackjack statistics are enabled")
            
    @commands.Cog.listener()
    async def on_message(self,message):
        if message.author.id != 270904126974590976:
            return
        
        if not (message.content.startswith("What do you want to do?") or message.content.startswith("Type `h` to **hit**")):
            return

        if not message.channel.permissions_for(message.guild.me).send_messages:
            return
        
        if not self.valid_channels(message):
            return
        
        player_name = message.embeds[0].fields[0].name
        
        if self.disabled_stats(player_name):
            return
        
        player_message = f"{player_name}'s blackjack statistics"
        
        player_hand = [card[3:len(card)-1] for card in [text.split("]")[0] for text in message.embeds[0].fields[0].value.split("[") if text.find("]") != -1]]

        dealer_hand = [card[3:len(card)-1] for card in [text.split("]")[0] for text in message.embeds[0].fields[1].value.split("[") if text.find("]") != -1]]

        player = ["10" if card in ("J", "Q", "K") else card for card in player_hand]
        dealer = ["10" if card in ("J", "Q", "K") else card for card in dealer_hand]


        dbase = sqlite3.connect("blackjack_stats.db")
        cursor = dbase.cursor()
        cursor.execute("SELECT hit_percent, stand_percent_wins, stand_percent_ties FROM stats WHERE dealer == ? AND player == ?", [dealer[0], "".join(sorted(player, key = lambda o: 1 if o == 'A' else int(o)))])

        hit_percent, stand_percent_wins, stand_percent_ties = cursor.fetchone()

        dbase.close()
        statistics = f"**{player_message}**\nPercentage of surviving if hit: {round(hit_percent,1)}%\nPercentage of winning if stand: {round(stand_percent_wins*100,1)}%" + f"\nPercentage of tying if stand: {round(stand_percent_ties*100,1)}%" * (stand_percent_ties != 0)

        await message.channel.send(statistics)


def setup(bot):
    bot.add_cog(bj(bot))