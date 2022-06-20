import os
import discord
from discord.ext import commands
from discord.ext.commands import CommandNotFound

intents = discord.Intents.default()
intents.members = True
intents.message_content = True
bot = commands.Bot(command_prefix='?', intents=intents)

if __name__ == '__main__':
    for filename in os.listdir('cogs'):
        if filename.endswith('.py'):
            bot.load_extension(f'cogs.{filename[:-3]}')

@bot.event
async def on_ready():
    await bot.change_presence(activity=discord.Game(name="among us"))
    print(f"Logged in as {bot.user.name}!")

# @bot.event
# async def on_command_error(ctx, error):
#     if isinstance(error, CommandNotFound):
#         not_found = str(error).split('"')[1]
#         await ctx.send(f"Command **`{not_found}`** not found.")

bot.run(os.getenv("AMOGUSTOKEN"))