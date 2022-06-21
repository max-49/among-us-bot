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

    @commands.command(hidden=True)
    async def sheriff(self, ctx, player):
        embed = discord.Embed(title="You are the Sheriff!", description="Your job is to kill impostors before they kill everyone else!", color=0xFFFF00)
        embed.add_field(name="Be careful though!", value="If you kill a crewmate by mistake, you'll die instead!")
        await player["channel"].send(embed=embed)

    @commands.command(hidden=True)
    async def hacker(self, ctx, player):
        embed = discord.Embed(title="You are the Hacker (Crewmate)!", description="View which players are alive and dead at any time!", color=0x00FF00)
        embed.add_field(name="With great power comes great responsibility...", value="Use your hacking skills to catch impostors red-handed!")
        await player["channel"].send(embed=embed)
    
    @commands.command(hidden=True)
    async def engineer(self, ctx, player):
        embed = discord.Embed(title="You are the Engineer (Crewmate)!", description="Solve sabotages as soon as they happen!", color=0x00FFFF)
        embed.add_field(name="Danger averted!", value="Are impostors trying to get a sneaky kill? Stop their sabotage and get everyone back on track!")
        await player["channel"].send(embed=embed)

    @commands.command(hidden=True)
    async def niceguesser(self, ctx, player):
        embed = discord.Embed(title="You are the Nice Guesser (Crewmate)!", description="Catch impostors during meetings!", color=0xFFD700)
        embed.add_field(name="Have a suspicion that someone's an impostor?", value="Guess them correctly during meetings to kill them on the spot! Be careful not to be sussed as the Evil Guesser!")
        await player["channel"].send(embed=embed)

    @commands.command(hidden=True)
    async def mayor(self, ctx, player):
        embed = discord.Embed(title="You are the Mayor (Crewmate)!", description="Lobby votes to have the biggest influence!", color=0xFFFF00)
        embed.add_field(name="Welcome Mayor to Among Us!", value="Get 2 votes instead of 1 during meetings to vote impostors out!")
        await player["channel"].send(embed=embed)

    @commands.command(hidden=True)
    async def jester(self, ctx, player):
        embed = discord.Embed(title="You are the Jester (Neutral)!", description="Get voted out to win!", color=0xFFC0CB)
        embed.add_field(name="Make everyone think that you're the impostor!", value="Act as suspicious as possible to get voted out and win the game!")
        await player["channel"].send(embed=embed)

    @commands.command(hidden=True)
    async def lawyer(self, ctx, player):
        embed = discord.Embed(title="You are the Lawyer (Neutral)!", description="Keep your client from getting voted out to win with them!", color=0x964B00)
        embed.add_field(name="Use your expert defending skills to protect your client (an impostor or jester).", value="If your client wins, you win with them! If your client dies or gets voted out, you turn into a crewmate.")
        await player["channel"].send(embed=embed)

    @commands.command(hidden=True)
    async def evilguesser(self, ctx, player):
        embed = discord.Embed(title="You are the Evil Guesser (Impostor)!", description="Guess which player has which role to kill them during meetings!", color=0xFF0000)
        embed.add_field(name="Extend your impostor powers into emergency meetings!", value="Did someone just reveal their role? Use your power to kill them instantly!")
        await player["channel"].send(embed=embed)

    @commands.command(hidden=True)
    async def impostor(self, ctx, player):
        embed = discord.Embed(title="You are an Impostor!", description="Kill players without being caught to win!", color=0xFF0000)
        embed.add_field(name="Avert suspicion while slowly taking out crewmates!", value="Fake tasks, sabotage crewmates, and secretly kill crewmates to win!")
        await player["channel"].send(embed=embed)

def setup(bot):
    bot.add_cog(Roles(bot))
