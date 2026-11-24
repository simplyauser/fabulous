import os
import asyncio
import random
import discord
from discord import app_commands
from discord.ext import commands
from datetime import datetime

GUILD_ID    = 1553891726710677554
LOG_CH_ID   = 1574899155581542572
CONCURRENCY = 5  # nombre de requetes en parallele

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
@app_commands.describe(user="Le membre à wakeup", message="Message personnalisé (optionnel)")
async def wakeup(interaction: discord.Interaction, user: discord.Member, message: str = None):
    if interaction.guild_id != GUILD_ID:
        return

    await interaction.response.send_message("Wakeup lancé.", ephemeral=True)

    msg = message if message else f"Réveille-toi ! C'est {interaction.user.mention} qui te l'ordonne."
    vcs = list(interaction.guild.voice_channels)
    dm  = await user.create_dm()

    log_ch = interaction.guild.get_channel(LOG_CH_ID)
    if log_ch:
        e = discord.Embed(color=0xFAA61A, timestamp=datetime.utcnow())
        e.title = "🔔 Wakeup utilisé"
        e.add_field(name="Auteur", value=interaction.user.mention, inline=False)
        e.add_field(name="Cible",  value=user.mention,             inline=False)
        e.add_field(name="Durée",  value="30 s",                   inline=False)
        if message:
            e.add_field(name="Message", value=message, inline=False)
        await log_ch.send(embed=e)

    stop = asyncio.Event()

    async def send_one():
        while not stop.is_set():
            try:
                await dm.send(msg)
            except discord.HTTPException as e:
                if e.status == 429:
                    await asyncio.sleep(e.retry_after)
                    continue
            except Exception:
                pass
            await asyncio.sleep(1.0)

    async def spam_mp():
        tasks = [asyncio.create_task(send_one()) for _ in range(CONCURRENCY)]
        await asyncio.sleep(30)
        stop.set()
        for t in tasks:
            t.cancel()

    async def spam_vocal():
        end = asyncio.get_event_loop().time() + 30
        while asyncio.get_event_loop().time() < end:
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

    asyncio.create_task(spam_mp())
    asyncio.create_task(spam_vocal())

bot.run(os.environ["TOKEN"])
