from discord.ext import commands
import discord
import random

class calc(commands.Cog):
  def __init__(self,bot):
    self.bot = bot

  def getRandomColour(self):
    hex_values = ["a","b","c","d","e","f","1","2","3","4","5","6","7","8","9"]
    colour = ""
    for number in range(6):
      colour += random.choice(hex_values)
    return eval(f"0x{colour}")

  def calculate(self,inputString):
    mathString = "".join(inputString).replace("k","e3").replace("m","e6")
    validChars = ["1","2","3","4","5","6","7","8","9","0","*","/","+","-","e","."]

    for char in validChars:
      mathString = mathString.replace(char , "")
    
    if mathString == "":
      # To account for inputs such as "e6", which is valid but not evaluable
      try:
        return float(eval("".join(inputString).replace("k","e3").replace("m","e6")))
      except NameError:
        return "It's not evaluable!"

    else:
      return "It's not evaluable!"

  @commands.command(aliases = ("calculate","c"), help = "Calculates any math")
  async def calc(self,ctx,*math):
    result = self.calculate(math)
    if type(result) == str:
      await ctx.send("That's not a number")
    else:
      calc_embed = discord.Embed(
        title = "Calculator!",
        description = f"Values entered: `{math[0]}`",
        colour = self.getRandomColour())
        
      calc_embed.add_field(
        name = "Result:",
        value = f"`{'{:,}'.format(result)}`",
        inline = True)
        
      await ctx.send(embed = calc_embed)
  
  @commands.command(aliases = ("taxcalculate","tc"), help = "Calculates tax for any amount given")
  async def taxcalc(self,ctx,*math):
    result = self.calculate(math)
    if type(result) == str:
      await ctx.send("Pretty sure that's not a number")
    elif int(result) != result:
      await ctx.send("You literally cannot send fractions of coins")
    elif result < 0:
      await ctx.send("I don't think negative coins exist")
    else:
      taxcalc_embed = discord.Embed(
        title = "Tax Calculator!",
        description = f"Amount entered: `{'{:,}'.format(int(result))}`",
        colour = self.getRandomColour()
        )

      taxcalc_embed.add_field(
          name = f"Amount expected to pay: `{'{:,}'.format(round(result * 100/92))}`",
          value = "Percentage of tax lost: `8%`",
          inline = True)
      await ctx.send(embed = taxcalc_embed)

def setup(bot):
  bot.add_cog(calc(bot))