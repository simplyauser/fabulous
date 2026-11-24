import os
import asyncio
import random
import discord
from discord import app_commands
from discord.ext import commands

GUILD_ID = 1553891726710677554

intents = discord.Intents.all()
bot = commands.Bot(command_prefix="=", intents=intents, help_command=None)
tree = bot.tree

@bot.event
async def on_ready():
    guild = discord.Object(id=GUILD_ID)
    tree.copy_global_to(guild=guild)
    await tree.sync(guild=guild)
    print(f"Connecté : {bot.user}")

@bot.event
async def on_guild_join(guild):
    if guild.id != GUILD_ID:
        await guild.leave()

@tree.command(name="wakeup", description="Wakeup un membre", guild=discord.Object(id=GUILD_ID))
@app_commands.describe(user="Le membre à wakeup")
async def wakeup(interaction: discord.Interaction, user: discord.Member):
    if interaction.guild_id != GUILD_ID:
        return

    await interaction.response.send_message("Wakeup lancé.", ephemeral=True)

    msg = f"Réveille-toi ! C'est {interaction.user.mention} qui te l'ordonne."
    vcs = list(interaction.guild.voice_channels)

    async def spam():
        end = asyncio.get_event_loop().time() + 30
        while asyncio.get_event_loop().time() < end:
            try:
                await user.send(msg)
            except Exception:
                pass
            if user.voice and vcs:
                try:
                    await user.move_to(random.choice(vcs))
                except Exception:
                    pass
            await asyncio.sleep(0.3)
        try:
            await user.move_to(None)
        except Exception:
            pass

    asyncio.create_task(spam())

bot.run(os.environ["TOKEN"])
