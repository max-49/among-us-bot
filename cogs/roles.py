import discord
from discord.ext import commands

class RolesView(discord.ui.View):
    def __init__(self, host):
        super().__init__()

    @discord.ui.button(label='Join Game', style=discord.ButtonStyle.grey)
    async def join(self, button: discord.ui.Button, interaction: discord.Interaction):
        if interaction.user in self.players:
            await interaction.response.send_message("You've already joined this game!", ephemeral=True)
        await interaction.channel.send(f'{interaction.user.mention} has joined the game!')
        self.players.append(interaction.user)


class Roles(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name='setuproles', help='setup a new game of among us')
    async def setup(self, ctx):
        embed = discord.Embed(title="IRL Among Us Setup", description="Please press 'Join Game' to join the game!", color=0x00FFFF)
        setup_view = RolesView(ctx.author.id)
        await ctx.send(embed=embed, view=setup_view)
        await setup_view.wait()
        await ctx.send(f"Starting game with {', '.join([x.mention for x in setup_view.players])}...")



def setup(bot):
    bot.add_cog(Roles(bot))
