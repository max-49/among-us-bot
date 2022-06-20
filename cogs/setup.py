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
            await interaction.response.send_message("You've already joined this game!", ephemeral=True)
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
        await ctx.send(f"Starting game with {', '.join([x.mention for x in setup_view.players])}...")


def setup(bot):
    bot.add_cog(Setup(bot))
