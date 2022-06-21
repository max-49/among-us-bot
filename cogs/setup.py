import json
import random
import discord
from discord.ext import commands 

class SetupView(discord.ui.View):
    def __init__(self, host):
        super().__init__()
        self.host = host
        self.value = True
        self.cancelled = False
        self.players = []

    @discord.ui.button(label='Join Game', style=discord.ButtonStyle.grey)
    async def join(self, button: discord.ui.Button, interaction: discord.Interaction):
        if interaction.user in self.players:
            return await interaction.response.send_message("You've already joined this game!", ephemeral=True)
        await interaction.channel.send(f'{interaction.user.mention} has joined the game!')
        self.players.append(interaction.user)
    
    @discord.ui.button(label='Start Game', style=discord.ButtonStyle.green)
    async def start(self, button: discord.ui.Button, interaction: discord.Interaction):
        if interaction.user.id != self.host:
            return await interaction.response.send_message("Only the host can start the game!", ephemeral=True)
        for child in self.children:
            child.disabled = True
        self.value = False
        embed = discord.Embed(title="IRL Among Us Setup", description="Game starting soon. Please wait...", color=0x00FF00)
        await interaction.message.edit(embed=embed, view=self)
        self.stop()

    @discord.ui.button(label='Cancel Game', style=discord.ButtonStyle.red)
    async def cancel(self, button: discord.ui.Button, interaction: discord.Interaction):
        if interaction.user.id != self.host:
            return await interaction.response.send_message("Only the host can cancel the game!", ephemeral=True)
        await interaction.channel.send('Cancelling game...')
        for child in self.children:
            child.disabled = True
        self.value = False
        self.cancelled = True
        embed = discord.Embed(title="IRL Among Us Setup", description="Setup Cancelled!", color=0xFF0000)
        await interaction.message.edit(embed=embed, view=self)
        self.stop()


class Setup(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name='setup', help='setup a new game of among us')
    async def setup(self, ctx):
        embed = discord.Embed(title="IRL Among Us Setup", description="Please press 'Join Game' to join the game!", color=0x00FFFF)
        setup_view = SetupView(ctx.author.id)
        await ctx.send(embed=embed, view=setup_view)
        await setup_view.wait()
        if not setup_view.cancelled:
            await ctx.send(f"Starting game with {', '.join([x.mention for x in setup_view.players])}...")
            await ctx.invoke(self.setup_channels, setup_view.players)
    
    async def setup_channels(self, ctx, players):
        with open('settings.json') as j:
            settings = json.load(j)
        crewmates = [{"player": player, "role": None} for player in players]
        neutrals = []
        impostors = []
        for _ in range(settings["game"][0]["value"]):
            impostor = random.choice(crewmates)
            impostors.append(impostor)
            crewmates.remove(impostor)
        for _ in range(settings["game"][2]["value"]):
            neutral = random.choice(crewmates)
            neutrals.append(neutral)
            crewmates.remove(neutral)
        crew_roles = [role for role in settings["roles"]["crew"] if role["value"]]
        neutral_roles = [role for role in settings["roles"]["neutral"] if role["value"]]
        impostor_roles = [role for role in settings["roles"]["impostor"] if role["value"]]
        for crew in crewmates:
            role = random.choice(crew_roles)
            crew["role"] = role
            crew_roles.remove(role)
        for neutral in neutrals:
            role = random.choice(neutral_roles)
            neutral["role"] = role
            neutral_roles.remove(role)
        for impostor in impostors:
            role = random.choice(impostor_roles)
            impostor["role"] = role
            impostor_roles.remove(role)
        category = await ctx.guild.create_category("Among Us Channels")
        for player in (crewmates + neutrals + impostors):
            channel = await category.create_text_channel(f'{player["player"].name}-{player["role"]["role"]}', overwrites={ctx.guild.default_role: discord.PermissionOverwrite(read_messages=False), player["player"]: discord.PermissionOverwrite(read_messages=True)})
            player["channel"] = channel
        await ctx.invoke(self.send_roles, crewmates + neutrals + impostors)

    async def send_roles(self, ctx, players):
        for player in players:
            if player["role"]["role"] == "Sheriff":
                await ctx.invoke(self.bot.get_command("sheriff"), player)
            if player["role"]["role"] == "Hacker":
                await ctx.invoke(self.bot.get_command("hacker"), player)
            if player["role"]["role"] == "Engineer":
                await ctx.invoke(self.bot.get_command("engineer"), player)
            if player["role"]["role"] == "Nice Guesser":
                await ctx.invoke(self.bot.get_command("niceguesser"), player)
            if player["role"]["role"] == "Mayor":
                await ctx.invoke(self.bot.get_command("mayor"), player)
            if player["role"]["role"] == "Jester":
                await ctx.invoke(self.bot.get_command("jester"), player)
            if player["role"]["role"] == "Lawyer":
                await ctx.invoke(self.bot.get_command("lawyer"), player)
            if player["role"]["role"] == "Evil Guesser":
                await ctx.invoke(self.bot.get_command("evilguesser"), player)
            if player["role"]["role"] == "Impostor":
                await ctx.invoke(self.bot.get_command("impostor"), player)


def setup(bot):
    bot.add_cog(Setup(bot))
