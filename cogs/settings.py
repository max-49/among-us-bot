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
    async def sett(self, ctx, num: int, value):
        with open('settings.json') as j:
            settings = json.load(j)
        if not value.isdigit():
            return await ctx.reply("All values must be an integers!")
        if num <= 4:
            for setting in settings["game"]:
                if setting["num"] == num:
                    if num <= 3:
                        setting["value"] = int(value)
                        await ctx.reply(f"Value of `{setting['setting']}` successfully set to `{value}`")
                    if num == 4:
                        setting["value"] = bool(int(value))
                        await ctx.reply(f"Value of `{setting['setting']}` successfully set to `{bool(int(value))}`")
        elif num <= 8:
            for setting in settings["cool"]:
                if setting["num"] == num:
                    setting["value"] = int(value)
                    await ctx.reply(f"Value of `{setting['setting']}` successfully set to `{value}`")
        elif num <= 13:
            for role in settings["roles"]["crew"]:
                if role["num"] == num:
                    role["value"] = bool(int(value))
                    await ctx.reply(f"Value of `{role['role']}` successfully set to `{bool(int(value))}`")
        elif num <= 15:
            for role in settings["roles"]["neutral"]:
                if role["num"] == num:
                    role["value"] = bool(int(value))
                    await ctx.reply(f"Value of `{role['role']}` successfully set to `{bool(int(value))}`")
        elif num == 16:
            for role in settings["roles"]["impostor"]:
                if role["num"] == num:
                    role["value"] = bool(int(value))
                    await ctx.reply(f"Value of `{role['role']}` successfully set to `{bool(int(value))}`")
        with open('settings.json', 'w') as j:
            json.dump(settings, j)

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
        embed = discord.Embed(title="Game Settings", description="Use ?set <setting number> <value> to change settings.", color=0x00FFFF)
        for setting in settings["game"]:
            embed.add_field(name=f'{setting["num"]}) {setting["setting"]}', value=setting["value"], inline=False)
        arrow = BackArrow(ctx.author)
        await mess.edit(embed=embed, view=arrow)
        await arrow.wait()
        await ctx.invoke(self.setting, mess)

    async def coolsettings(self, ctx, mess):
        with open('settings.json') as j:
            settings = json.load(j)
        embed = discord.Embed(title="Cooldown Settings", description="Use ?set <setting number> <value> to change settings. (All values are in seconds)", color=0x00FFFF)
        for setting in settings["cool"]:
            embed.add_field(name=f'{setting["num"]}) {setting["setting"]}', value=setting["value"], inline=False)
        arrow = BackArrow(ctx.author)
        await mess.edit(embed=embed, view=arrow)
        await arrow.wait()
        await ctx.invoke(self.setting, mess)
    
    async def rolesettings(self, ctx, mess):
        with open('settings.json') as j:
            settings = json.load(j)
        embed = discord.Embed(title="Role Settings", description="Use ?set <setting number> <value> to change settings.", color=0x00FFFF)
        embed.add_field(name="Crewmate Roles:", value="\n".join([f"{x['num']}) {x['role']}: {x['value']}" for x in settings["roles"]["crew"]]), inline=False)
        embed.add_field(name="Neutral Roles:", value="\n".join([f"{x['num']}) {x['role']}: {x['value']}" for x in settings["roles"]["neutral"]]), inline=False)
        embed.add_field(name="Impostor Roles:", value="\n".join([f"{x['num']}) {x['role']}: {x['value']}" for x in settings["roles"]["impostor"]]), inline=False)
        arrow = BackArrow(ctx.author)
        await mess.edit(embed=embed, view=arrow)
        await arrow.wait()
        await ctx.invoke(self.setting, mess)

def setup(bot):
    bot.add_cog(Settings(bot))