import json
import discord
from discord.ext import commands

class BackArrow(discord.ui.View):
    def __init__(self, user):
        super().__init__()
        self.user = user
        self.value = True
    
    @discord.ui.button(label='Back', style=discord.ButtonStyle.green)
    async def back(self, button: discord.ui.Button, interaction: discord.Interaction):
        if interaction.user == self.user:
            self.value = False
            self.stop()

class SettingsView(discord.ui.View):
    def __init__(self, user):
        super().__init__()
        self.user = user 
        self.value = True
        self.choice = None
    
    @discord.ui.button(label='Game Settings', style=discord.ButtonStyle.grey)
    async def game(self, button: discord.ui.Button, interaction: discord.Interaction):
        if interaction.user == self.user:
            self.choice = 'game'
            self.stop()

    @discord.ui.button(label='Cooldowns', style=discord.ButtonStyle.grey)
    async def cool(self, button: discord.ui.Button, interaction: discord.Interaction):
        if interaction.user == self.user:
            self.choice = 'cool'
            self.stop()

    @discord.ui.button(label='Role Settings', style=discord.ButtonStyle.grey)
    async def roles(self, button: discord.ui.Button, interaction: discord.Interaction):
        if interaction.user == self.user:
            self.choice = 'role' 
            self.stop()
    
    @discord.ui.button(label='Exit', style=discord.ButtonStyle.red)
    async def exitt(self, button: discord.ui.Button, interaction: discord.Interaction):
        if interaction.user == self.user:
            for child in self.children:
                child.disabled = True
            await interaction.message.edit(view=self)
            self.stop()


class Settings(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name='set', help="set values for settings")
    async def sett(self, ctx, setting, value):
        with open('settings.json') as j:
            settings = json.load(j)
        

    @commands.command(name='settings', help='manage game settings')
    async def setting(self, ctx, mess=None):
        embed = discord.Embed(title="Among Us Settings", description="Click on the categories below to manage settings", color=0x00FFFF)
        settings_view = SettingsView(ctx.author)
        if mess:
            await mess.edit(embed=embed, view=settings_view)
        else:
            mess = await ctx.send(embed=embed, view=settings_view)
        await settings_view.wait()
        if settings_view.choice == 'game':
            await ctx.invoke(self.gamesettings, mess)
        elif settings_view.choice == 'cool':
            await ctx.invoke(self.coolsettings, mess)
        elif settings_view.choice == 'role':
            await ctx.invoke(self.rolesettings, mess)
        else:
            return

    async def gamesettings(self, ctx, mess):
        with open('settings.json') as j:
            settings = json.load(j)
        embed = discord.Embed(title="Game Settings", color=0x00FFFF)
        for setting in settings["game"]:
            embed.add_field(name=setting["setting"], value=setting["value"], inline=False)
        arrow = BackArrow(ctx.author)
        await mess.edit(embed=embed, view=arrow)
        await arrow.wait()
        await ctx.invoke(self.setting, mess)

    async def coolsettings(self, ctx, mess):
        with open('settings.json') as j:
            settings = json.load(j)
        embed = discord.Embed(title="Cooldown Settings", description="All values are in seconds", color=0x00FFFF)
        for setting in settings["cool"]:
            embed.add_field(name=setting["setting"], value=setting["value"], inline=False)
        arrow = BackArrow(ctx.author)
        await mess.edit(embed=embed, view=arrow)
        await arrow.wait()
        await ctx.invoke(self.setting, mess)
    
    async def rolesettings(self, ctx, mess):
        with open('settings.json') as j:
            settings = json.load(j)
        embed = discord.Embed(title="Role Settings", color=0x00FFFF)
        embed.add_field(name="Crewmate Roles:", value="\n".join([f"{x['role']}: {x['value']}" for x in settings["roles"]["crew"]]), inline=False)
        embed.add_field(name="Neutral Roles:", value="\n".join([f"{x['role']}: {x['value']}" for x in settings["roles"]["neutral"]]), inline=False)
        embed.add_field(name="Impostor Roles:", value="\n".join([f"{x['role']}: {x['value']}" for x in settings["roles"]["impostor"]]), inline=False)
        arrow = BackArrow(ctx.author)
        await mess.edit(embed=embed, view=arrow)
        await arrow.wait()
        await ctx.invoke(self.setting, mess)

def setup(bot):
    bot.add_cog(Settings(bot))