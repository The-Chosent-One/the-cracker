from discord.ext import commands
import discord
import sqlite3
import sys
import traceback

class serverConfigurations(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    def present_channels(self, channel_str):
        return "<#" + channel_str + ">"

    def format_channels(self, channel_data):
        return " ".join(map(self.present_channels, channel_data.split("|")[1:]))

    def init_guild(self, guild_id):
        dbase = sqlite3.connect("config.db")
        cursor = dbase.cursor()

        cursor.execute("SELECT enabled, disabled FROM config WHERE guild_id == ?", [str(guild_id)])
        channels = cursor.fetchone()

        if channels is None:
            cursor.execute("INSERT INTO config (guild_id, enabled, disabled) VALUES (?, ?, ?)", [str(guild_id), "all", ""])
            dbase.commit()
        dbase.close()

    async def send_channel_list(self, ctx, guild_id):
        dbase = sqlite3.connect("config.db")
        cursor = dbase.cursor()

        cursor.execute("SELECT enabled, disabled FROM config WHERE guild_id == ?", [str(guild_id)])
        enabled, disabled = cursor.fetchone()

        channels_embed = discord.Embed(
            title = "Current channels that are enabled/disabled",
            colour = 0x3f51b5
        )
        if enabled == "all" and disabled == "":
            channels_embed.description = "All channels are enabled"
        elif enabled == "" and disabled == "all": channels_embed.description = "All channels are disabled"

        elif enabled == "all":
            channels_embed.description = f"These channels are **__disabled__**: {self.format_channels(disabled)}\nAll other channels are enabled"

        elif disabled == "all":
            channels_embed.description = f"These channels are **__enabled__**: {self.format_channels(enabled)}\nAll other channels are disabled"

        dbase.close()
        return await ctx.send(embed = channels_embed)
        
    async def update_all_channels(self, ctx, option, guild_id):
        dbase = sqlite3.connect("config.db")
        cursor = dbase.cursor()
        cursor.execute("SELECT enabled, disabled FROM config WHERE guild_id == ?", [str(guild_id)])
        enabled, disabled = cursor.fetchone()

        if option: # enabling
            if enabled == "all" and disabled == "":
                dbase.close()
                return await ctx.send("All channels are already enabled!")

            cursor.execute("UPDATE config SET enabled = ?, disabled = ? WHERE guild_id = ?", ["all", "", str(guild_id)])
            dbase.commit()
            dbase.close()
            return await ctx.send("All channels enabled!")
         
        if disabled == "all" and enabled == "":
            dbase.close()
            return await ctx.send("All channels are already disabled!")

        cursor.execute("UPDATE config SET enabled = ?, disabled = ? WHERE guild_id = ?", ["", "all", str(guild_id)])
        dbase.commit()
        dbase.close()
        return await ctx.send("All channels disabled!")


    async def get_valid_channels(self, ctx, channels):
        channel_ids = set()
        for channel in "".join(channels).split("|"):
            try:
                valid_channel = await commands.TextChannelConverter().convert(ctx, channel)
            except commands.errors.ChannelNotFound:
                return None
            
            channel_ids.add(valid_channel.id)

        return channel_ids
    
    async def add_enabled_channels(self, ctx, guild_id, channel_ids):
        dbase = sqlite3.connect("config.db")
        cursor = dbase.cursor()
        cursor.execute("SELECT enabled, disabled FROM config WHERE guild_id == ?", [str(guild_id)])
        enabled, disabled = cursor.fetchone()

        successful_channels = []
        failed_channels = []
        
        for channel_id in channel_ids:

            channel_id = str(channel_id)
            if disabled != "" and channel_id in disabled:
                disabled = disabled.replace(f"|{channel_id}", "")
                successful_channels.append(channel_id)
            
            elif enabled == "all" or channel_id in enabled:
                failed_channels.append(channel_id)
            
            else:
                enabled += f"|{channel_id}"
                successful_channels.append(channel_id)

        cursor.execute("UPDATE config SET enabled = ?, disabled = ? WHERE guild_id == ?", [enabled, disabled, str(guild_id)])
        dbase.commit()
        dbase.close()

        enabled_message = f"Enabled {' '.join(map(self.present_channels, successful_channels))}"
        failed_message = f"The channels {' '.join(map(self.present_channels, failed_channels))} are already enabled."

        if len(failed_channels) == 0:
            return await ctx.send(enabled_message)
        if len(successful_channels) == 0:
            return await ctx.send(failed_message)
        return await ctx.send(f"{enabled_message}\n{failed_message}")

    async def add_disabled_channels(self, ctx, guild_id, channel_ids):
        dbase = sqlite3.connect("config.db")
        cursor = dbase.cursor()
        cursor.execute("SELECT enabled, disabled FROM config WHERE guild_id == ?", [str(guild_id)])
        enabled, disabled = cursor.fetchone()

        successful_channels = []
        failed_channels = []
        
        for channel_id in channel_ids:

            channel_id = str(channel_id)
            if enabled != "" and channel_id in enabled:
                enabled = enabled.replace(f"|{channel_id}", "")
                successful_channels.append(channel_id)
            
            elif disabled == "all" or channel_id in disabled:
                failed_channels.append(channel_id)
            
            else:
                disabled += f"|{channel_id}"
                successful_channels.append(channel_id)

        cursor.execute("UPDATE config SET enabled = ?, disabled = ? WHERE guild_id == ?", [enabled, disabled, str(guild_id)])
        dbase.commit()
        dbase.close()

        enabled_message = f"Disabled {' '.join(map(self.present_channels, successful_channels))}"
        failed_message = f"The channels {' '.join(map(self.present_channels, failed_channels))} are already disabled."

        if len(failed_channels) == 0:
            return await ctx.send(enabled_message)
        if len(successful_channels) == 0:
            return await ctx.send(failed_message)
        return await ctx.send(f"{enabled_message}\n{failed_message}")

    @commands.command(brief = "Customises which channels the bot will respond to. Requires `Manage Server` permissions.", help = "Set which channels the bot would respond to by using either \n`serverconfig enable <channel>`\n`serverconfig disable <channel>`\nThe channels can be multiple channels separated by `|`, or the usage of `all` is allowed as well.\n All channels are enabled by default.\nRequires `Manage Server` permissions to invoke.")
    async def serverconfig(self, ctx, option: str, *channels):
        # a bunch of checks
        if not ctx.channel.permissions_for(ctx.author).manage_guild:
            return await ctx.channel.send("You don't have the `Manage Server` permission.")

        if option.lower() not in ("e", "en", "enable", "d", "di", "disable", "list"):
            return await ctx.send("You only can `enable`, `disable` or check channels with `list`")

        self.init_guild(ctx.guild.id) # initialise data
        if option.lower() == "list":
            return await self.send_channel_list(ctx, ctx.guild.id)

        if channels == ():
            return await ctx.send("You need to key in channels")

        if option.lower() in ("e", "en", "enable"): option = 1 
        else: option = 0 # 1 for enable and 0 for disable

        if channels[0].lower() == "all":
            return await self.update_all_channels(ctx, option, ctx.guild.id)

        channel_ids = await self.get_valid_channels(ctx, channels)
        if channel_ids is None:
            return await ctx.send("One of those isn't a channel")

        if option: # enabling
            return await self.add_enabled_channels(ctx, ctx.guild.id, channel_ids)

        return await self.add_disabled_channels(ctx, ctx.guild.id, channel_ids)

    @serverconfig.error
    async def config_error(self, ctx, error):
        if isinstance(error, commands.errors.MissingRequiredArgument):
            help = self.bot.get_cog("help")
            await help.send_command_help(ctx, "serverconfig")
            return
        print('Ignoring exception in command {}:'.format(ctx.command), file=sys.stderr)
        traceback.print_exception(type(error), error, error.__traceback__, file=sys.stderr)


def setup(bot):
    bot.add_cog(serverConfigurations(bot))


