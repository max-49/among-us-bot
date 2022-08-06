import json
import random
import asyncio
import discord
from discord.ext import commands 

class Clean(discord.ui.View):
    def __init__(self, user):
        super().__init__(timeout=None)
        self.clean = None
        self.restart = None
        self.user = user 

    @discord.ui.button(label="Clean", style=discord.ButtonStyle.red)
    async def clean(self, button: discord.ui.Button, interaction: discord.Interaction):
        if interaction.user == self.user:
            self.clean = True
        else:
            await interaction.response.send_message("Only the host can use these buttons!", ephemeral=True)
    
    @discord.ui.button(label="Clean and Restart", style=discord.ButtonStyle.green)
    async def cleanstart(self, button: discord.ui.Button, interaction: discord.Interaction):
        if interaction.user == self.user:
            self.clean = True
            self.restart = True
        else:
            await interaction.response.send_message("Only the host can use these buttons!", ephemeral=True)


class VotingButton(discord.ui.Button):
    def __init__(self, label):
        super().__init__(label=label, style=discord.ButtonStyle.grey)

    async def callback(self, interaction):
        name = self.label
        for player in self.view.players:
            if player["player"].name == name:
                for playerr in self.view.players:
                    if playerr["player"] == interaction.user:
                        if playerr["role"]["role"] == "Mayor":
                            player["votes"] += 2
                        else:
                            player["votes"] += 1
                        playerr["voted"] = True
                        break
                break
        else:
            for player in self.view.players:
                if player["player"] == interaction.user:
                    if player["role"]["role"] == "Mayor":
                        self.view.skipped += 2
                    else:
                        self.view.skipped += 1
                    player["voted"] = True
                    
        for child in self.view.children:
            child.disabled = True
        await interaction.response.edit_message(view=self.view)


class VotingView(discord.ui.View):
    def __init__(self, players):
        super().__init__()
        self.players = players
        self.user_selected = None
        self.skipped = 0
        for i in range(len(players)):
            if players[i]["alive"]:
                self.add_item(VotingButton(players[i]["player"].name))
        self.add_item(VotingButton("Skip Vote"))

class ReportView(discord.ui.View):
    def __init__(self, players):
        super().__init__(timeout=None)
        self.reported = False
        self.meeting = False
        self.players = players
        self.reported_by = None

    @discord.ui.button(label="📣 Report Body", style=discord.ButtonStyle.red)
    async def report(self, button, interaction):
        self.reported = True
        self.reported_by = interaction.user
        self.stop()

    @discord.ui.button(label="🚨 Call Emergency Meeting", style=discord.ButtonStyle.red)
    async def emergency(self, button: discord.ui.Button, interaction: discord.Interaction):
        for player in self.players:
            if player["player"] == interaction.user:
                if player["meetings"] > 0:
                    player["meetings"] -= 1
                    self.meeting = True
                    self.stop()
                else:
                    await interaction.response.send_message("You don't have any emergency meetings left!", ephemeral=True)
                    button.disabled = True
                    await interaction.message.edit(view=self)

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
        self.category = None
        self.roles = None
        self.imp_roles = None
        self.announcement_channel = None
        self.ghost_chat = None
        self.is_reported = None
        self.alive_role = None
        self.ghost_role = None
        self.dead_role = None

    @commands.command(name='setup', help='setup a new game of among us')
    async def setup(self, ctx):
        embed = discord.Embed(title="IRL Among Us Setup", description="Please press 'Join Game' to join the game!", color=0x00FFFF)
        setup_view = SetupView(ctx.author.id)
        await ctx.send(embed=embed, view=setup_view)
        await setup_view.wait()
        if not setup_view.cancelled:
            await ctx.send(f"Starting game with {', '.join([x.mention for x in setup_view.players])}...")
            await ctx.invoke(self.setup_channels, setup_view.players)

    @commands.command(name='clean', help='clean up chats')
    async def clean(self, ctx):
        if self.alive_role is not None:
            for member in ctx.guild.members:
                if self.alive_role in member.roles:
                    await member.remove_roles(self.alive_role)
                if self.dead_role in member.roles:
                    await member.remove_roles(self.dead_role)
                if self.ghost_role in member.roles:
                    await member.remove_roles(self.ghost_role)
        if self.category is not None:
            for channel in self.category.channels:
                await channel.delete()
            await self.category.delete()
            self.category = None
            await ctx.send("Cleaned")
        else:
            await ctx.send("No category to clean")
    
    async def setup_channels(self, ctx, players):
        with open('settings.json') as j:
            settings = json.load(j)
        crewmates = [{"player": player, "role": None} for player in players]
        players = [{"player": player, "role": None} for player in players]
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
        self.roles = crew_roles + neutral_roles + impostor_roles
        self.imp_roles = [role for role in impostor_roles]
        for crew in crewmates:
            index = players.index(crew)
            role = random.choice(crew_roles)
            players[index]["role"] = role
            crew_roles.remove(role)
            players[index]["is_impostor"] = False
        for neutral in neutrals:
            index = players.index(neutral)
            role = random.choice(neutral_roles)
            players[index]["role"] = role
            neutral_roles.remove(role)
            players[index]["is_impostor"] = False
        for impostor in impostors:
            index = players.index(impostor)
            role = random.choice(impostor_roles)
            players[index]["role"] = role
            impostor_roles.remove(role)
            players[index]["is_impostor"] = True
        self.alive_role = discord.utils.get(ctx.guild.roles, name='Alive')
        self.dead_role = discord.utils.get(ctx.guild.roles, name='Dead')
        self.ghost_role = discord.utils.get(ctx.guild.roles, name='Ghost')
        category = await ctx.guild.create_category("Among Us Channels")
        self.category = category
        self.announcement_channel = await category.create_text_channel('announcements', overwrites={ctx.guild.default_role: discord.PermissionOverwrite(read_messages=False), self.alive_role: discord.PermissionOverwrite(read_messages=True), self.ghost_role: discord.PermissionOverwrite(read_messages=True), self.dead_role: discord.PermissionOverwrite(read_messages=True)})
        self.ghost_chat = await category.create_text_channel('ghost-chat', overwrites={ctx.guild.default_role: discord.PermissionOverwrite(read_messages=False), self.alive_role: discord.PermissionOverwrite(read_messages=False), self.dead_role: discord.PermissionOverwrite(read_messages=True), self.ghost_role: discord.PermissionOverwrite(read_messages=True)})
        jester_player = None
        for player in players:
            if player["role"]["role"] == "Jester":
                jester_player = player["player"]
                break
        
        for player in players:
            await player["player"].add_roles(self.alive_role)
            channel = await category.create_text_channel(f'{player["player"].name}-{player["role"]["role"]}', overwrites={ctx.guild.default_role: discord.PermissionOverwrite(read_messages=False), player["player"]: discord.PermissionOverwrite(read_messages=True)})
            player["channel"] = channel
            player["alive"] = True
            player["meetings"] = settings["game"][1]["value"]
            player["votes"] = 0
            player["voted"] = False
            if player["role"]["role"] == "Lawyer":
                lawyer_clients = [x["player"] for x in players if x["is_impostor"]]
                if jester_player is not None:
                    lawyer_clients.append(jester_player)
                player["client"] = random.choice(lawyer_clients)
        await ctx.invoke(self.send_roles, players)

    async def send_roles(self, ctx, players, rounds=""):
        for player in players:
            if player["role"]["role"] == "Sheriff":
                await ctx.invoke(self.bot.get_command("sheriff" + rounds), player)
            if player["role"]["role"] == "Hacker":
                await ctx.invoke(self.bot.get_command("hacker" + rounds), player)
            if player["role"]["role"] == "Engineer":
                await ctx.invoke(self.bot.get_command("engineer" + rounds), player)
            if player["role"]["role"] == "Nice Guesser":
                await ctx.invoke(self.bot.get_command("niceguesser" + rounds), player)
            if player["role"]["role"] == "Mayor":
                await ctx.invoke(self.bot.get_command("mayor" + rounds), player)
            if player["role"]["role"] == "Jester":
                await ctx.invoke(self.bot.get_command("jester" + rounds), player)
            if player["role"]["role"] == "Lawyer":
                await ctx.invoke(self.bot.get_command("lawyer" + rounds), player)
            if player["role"]["role"] == "Evil Guesser":
                await ctx.invoke(self.bot.get_command("evilguesser" + rounds), player)
            if player["role"]["role"] == "Impostor":
                await ctx.invoke(self.bot.get_command("impostor" + rounds), player)
        await ctx.invoke(self.start_round, players)
    
    async def start_round(self, ctx, players):
        report_view = ReportView(players)
        await self.announcement_channel.set_permissions(self.alive_role, read_messages=False)
        for player in players:
            if player["alive"]:
                # if player["role"]["role"] == "Sheriff":
                #     await ctx.invoke(self.bot.get_command("sheriffround"), player)
                #     await asyncio.sleep(1.5)
                # if player["role"]["role"] == "Hacker":
                #     await ctx.invoke(self.bot.get_command("hackerround"), player)
                #     await asyncio.sleep(1.5)
                # if player["role"]["role"] == "Engineer":
                #     await ctx.invoke(self.bot.get_command("engineerround"), player)
                #     await asyncio.sleep(1.5)
                # if player["role"]["role"] == "Lawyer":
                #     await ctx.invoke(self.bot.get_command("lawyerround"), player)
                #     await asyncio.sleep(1.5)
                # if player["is_impostor"]:
                #     await ctx.invoke(self.bot.get_command("impostorround"), player)
                #     await asyncio.sleep(1.5)
                embed = discord.Embed(title="Task Round", description="Do your tasks and try not to get killed! To report a body, press the report button when you're touching a body. To call an emergency meeting, press the emergency button when you are at the meeting table!", color=0x808080)
                embed.add_field(name="Emergency meetings left:", value=str(player["meetings"]))
                await player["channel"].send(embed=embed, view=report_view)
            else:
                embed = discord.Embed(title="You are Dead!", description="Even though you're dead, you can still do tasks and chat with other dead people!", color=0x000000)
                await player["channel"].send(embed=embed)
        await report_view.wait()
        await self.announcement_channel.set_permissions(self.alive_role, read_messages=True)
        players = report_view.players
        if report_view.reported:
            embed = discord.Embed(title="A body has been reported!", description="Please head to the meeting table immediately!", color=0xFF0000)
            self.is_reported = report_view.reported_by
        elif report_view.meeting:
            embed = discord.Embed(title="An emergency meeting has been called!", description="Please head to the meeting table immediately!", color=0xFF0000)
        await self.announcement_channel.send(f"**everyone, Attention!**", embed=embed)
        for player in players:
            if player["alive"]:
                await player["channel"].purge(limit=1)
        await ctx.invoke(self.start_meeting, players)
    
    async def start_meeting(self, ctx, players):
        with open('settings.json') as j:
            settings = json.load(j)
        for player in players:
            if player["alive"]:
                embed = discord.Embed(title="Discussion Time", description="Use this time to discuss what happened!", color=0x0000FF)
                if self.is_reported is not None:
                    embed.add_field(name="Reported By", value=self.is_reported.name)
                await player["channel"].send(embed=embed)
        await asyncio.sleep(settings["cool"][1]["value"])
        voting_view = VotingView(players)
        for player in players:
            if player["alive"]:
                await player["channel"].purge(limit=1)
                if player["role"]["role"] == "Nice Guesser":
                    await ctx.invoke(self.bot.get_command("niceguessermeeting"), player, players, self.imp_roles)
                    await asyncio.sleep(1)
                if player["role"]["role"] == "Evil Guesser":
                    await ctx.invoke(self.bot.get_command("evilguessermeeting"), player, players, self.roles)
                    await asyncio.sleep(1)
                embed = discord.Embed(title="Voting Time", description="Vote out who you think is the impostor!", color=0x0000FF)
                await player["channel"].send(embed=embed, view=voting_view)
        for i in range(settings["cool"][2]["value"]):
            players = voting_view.players
            if all([player["voted"] for player in players if player["alive"]]):
                break
            if i == (settings["cool"][2]["value"]-6):
                for player in players:
                    if player["alive"]:
                        await player["channel"].send(f"{player['player'].mention}, 5 seconds left!")
            await asyncio.sleep(1)
        players = voting_view.players
        voted_players = {x["player"].name: x["votes"] for x in players}
        sorted_players = {k: v for k, v in sorted(voted_players.items(), key=lambda item: item[1], reverse=True)}
        sorted_players = [{"player": k, "votes": v} for (k,v) in sorted_players.items()]
        embed = discord.Embed(title="Voting Complete!", color=0x00FF00)
        for player in players:
            if player["votes"] == 0:
                text = "\u200b"
            else:
                text = ''.join(["✅" for _ in range(player["votes"])])
            embed.add_field(name=player["player"].name, value=text)
        if voting_view.skipped == 0:
            text = "\u200b"
        else:
            text = ''.join(["✅" for _ in range(voting_view.skipped)])
        embed.add_field(name="Skipped Voting", value=text)
        end_game = None
        if voting_view.skipped >= sorted_players[0]["votes"]:
            text = "No one was ejected (Skipped)"
        elif sorted_players[0]["votes"] == sorted_players[1]["votes"]:
            text = "No one was ejected (Tie)"
        else:
            text = f"{sorted_players[0]['player']} was ejected"
            for player in players:
                if player["player"].name == sorted_players[0]["player"]:
                    player["alive"] = False
                    await player["player"].remove_roles(self.alive_role)
                    await player["player"].add_roles(self.ghost_role)
                    if player["role"]["role"] == "Jester":
                        end_game = 0
        for player in players:
            await player["channel"].purge(limit=1)
            await player["channel"].send(embed=embed)
        await asyncio.sleep(5)
        for player in players:
            await player["channel"].send(text)
        await asyncio.sleep(5)
        num_impostors = 0
        num_crewmates = 0
        for player in players:
            await player["channel"].purge(limit=2)
            player["voted"] = False
            player["votes"] = 0
            if player["alive"] and player["is_impostor"]:
                num_impostors += 1
            elif player["alive"]:
                num_crewmates += 1
        if num_impostors == 0 and end_game is None:
            end_game = 1
        elif num_impostors >= num_crewmates and end_game is None:
            end_game = 2
        if end_game is not None:
            await ctx.invoke(self.end_game, players, end_game)
        else:
            await ctx.invoke(self.start_round, players)
    
    async def end_game(self, ctx, players, reason):
        if reason == 0:
            embed = discord.Embed(title="Jester wins!", description="The Jester has been voted out!", color=0xFFC0CB)
            text = ""
            for player in players:
                if player["role"]["role"] == "Jester":
                    for person in players:
                        if person["role"]["role"] == "Lawyer":
                            if person["client"] == player["player"]:
                                text = f" and **{person['player'].name}** also wins as their Lawyer"
                    embed.add_field(name="Winners", value=f"**{player['player'].name}** wins{text}!")
            clean_view = Clean(ctx.author)
            await ctx.send(embed=embed, view=clean_view)
            await clean_view.wait()
            if clean_view.clean and clean_view.restart:
                await ctx.invoke(self.clean)
                await ctx.invoke(self.setup)
            else:
                await ctx.invoke(self.clean)
        if reason == 1:
            embed = discord.Embed(title="Crewmates win!", description="All impostors have been voted out!", color=0x0000FF)
            text = []
            for player in players:
                if not player["is_impostor"]:
                    text.append(player["player"].name)
            embed.add_field(name="Winners", value=', '.join([f"**{player}**" for player in text]))
            clean_view = Clean(ctx.author)
            await ctx.send(embed=embed, view=clean_view)
            await clean_view.wait()
            if clean_view.clean and clean_view.restart:
                await ctx.invoke(self.clean)
                await ctx.invoke(self.setup)
            else:
                await ctx.invoke(self.clean)
        if reason == 2:
            embed = discord.Embed(title="Impostors win!", description="The crewmates failed to outlive the impostors", color=0xFF0000)
            text = []
            extra = ""
            for player in players:
                if player["is_impostor"]:
                    text.append(player["player"].name)
            for player in players:
                if player["is_impostor"]:
                    for person in players:
                        if person["role"]["role"] == "Lawyer":
                            if person["client"] == player["player"]:
                                extra = f"and **{person['player'].name}** also wins as the Lawyer"
            embed.add_field(name="Winners", value=', '.join([f"**{player}**" for player in text]) + extra)
            clean_view = Clean(ctx.author)
            await ctx.send(embed=embed, view=clean_view)
            await clean_view.wait()
            if clean_view.clean and clean_view.restart:
                await ctx.invoke(self.clean)
                await ctx.invoke(self.setup)
            else:
                await ctx.invoke(self.clean)

def setup(bot):
    bot.add_cog(Setup(bot))
