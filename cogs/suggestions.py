from discord.ext import commands
import discord
import pymongo
import math


class suggestions(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        mongoClient = pymongo.MongoClient("REDACTED")
        suggestionsdb = mongoClient["suggestionsdb"]  #database
        self.suggestions = suggestionsdb["suggestions"]  #collection

    @commands.command(brief = "Suggest an additional feature/change to an existing one to the developer of this bot", help = "Gives a suggestion to the developer of the bot, could be any feature you want added/ removed, or have just general feedback about the bot")
    async def suggest(self, ctx, *textInput):
        if textInput == ():
            await ctx.send("You need to type in a suggestion")
            return

        # discord embeds limits
        if len(" ".join(textInput)) > 1024:
            await ctx.send("That's too long of a suggestion!")

        else:
            async with ctx.typing():  # to let user know that it'll take a while
                pass

            self.suggestions.insert_one(
                {"user": str(ctx.author),
                "user_id": ctx.author.id,
                "server": str(ctx.guild),
                "server_invite": str(await ctx.channel.create_invite()),
                "suggestion": " ".join(textInput)}
            )
            await ctx.send("Thank you for your suggestion!")

    @commands.command(hidden=True)
    async def suggestions(self, ctx, *methods):
        if ctx.author.id != 531317158530121738:
            await ctx.send("Only the owner of the bot can use this command!")
            return

        suggestionsList = self.suggestions.find()  # caching it for convenience

        async with ctx.typing():  # pretty self-explanitory
            pass

        if methods == ():  # if the input is empty set it to page 1 of suggestions
            methods = ("1")

        if methods[0].lower() == "info":
            index = int(methods[1]) - 1  # lazy to test for type cuz i'll be the one using it

            suggestInfo = suggestionsList[index]

            info_embed = discord.Embed(
                title = f"Suggestion number {index + 1}",
                description = 
                f"From {suggestInfo['user']}, user id {suggestInfo['user_id']}",
                colour = 0xA54CFF
            )

            info_embed.add_field(
                name = 
                f"Server name: {suggestInfo['server']}\nInvite link: {suggestInfo['server_invite']}",
                value = f"Suggestion is: {suggestInfo['suggestion']}",
                inline = False
            )

            await ctx.send(embed = info_embed)
            return

        elif methods[0].lower() == "del":
            index = int(methods[1]) - 1  # lazy to test for type cuz i'll be the one using it

            try:
                await self.bot.delete_invite(suggestionsList[index]['server_invite'])  # if the invite has already been deleted
            except discord.errors.NotFound:
                pass

            self.suggestions.delete_one(suggestionsList[index])
            await ctx.send(f"Deteled suggestion {index + 1}")
            return

        else:
            suggest_embed = discord.Embed(
                title = "All suggestions",
                description = "Current methods are: `info, del`",
                colour=0xA54CFF
            )

            pageNum = int(methods[0])
            pages = math.ceil(self.suggestions.count_documents({}) / 5)
            if pageNum > pages:
                await ctx.send(f"Page {pageNum} doesn't exist dummy")
                return

            startSuggestionNum = pageNum * 5 - 4
            for index in range(startSuggestionNum - 1, startSuggestionNum + 4):  # minus 1 cuz of indicies
                # code below is to account for the last page, where there isn't 5 documents left
                try:
                    suggestInfo = suggestionsList[index]
                except IndexError:
                    continue

                suggest_embed.add_field(
                    name = f"{index + 1}) Suggestion from {suggestInfo['user']}",
                    value = f"{suggestInfo['suggestion']}",
                    inline = False
                )

            suggest_embed.set_footer(text = f"Page {pageNum} of {pages}")

            await ctx.send(embed = suggest_embed)


def setup(bot):
    bot.add_cog(suggestions(bot))
