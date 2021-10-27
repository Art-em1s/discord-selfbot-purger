import discord
from datetime import datetime, timedelta
import asyncio
auth = "DISCORD TOKEN GOES HERE"

whitelisted_dms = [733489401400918092] #discord system user, cannot delete messages
whitelisted_guilds = []
whitelisted_channels = []

dry_run = False
client = discord.Client()

delete_before_days = 31 #any message older than the current date less this number of days will be deleted


@client.event
async def on_message(message):
    if message.author.id == client.user.id and message.content == "test": #send a message anywhere with "test" to trigger the bot
        await nuke()


async def nuke():
    await iterate_dms()
    await iterate_servers()


async def iterate_servers():
    for server in client.guild:
        if server.id in whitelisted_guilds:
            continue
        else:
            for channel in server.channels:
                if str(channel.type) == "text" and channel.id not in whitelisted_channels:
                    #allows you to delete all messages from specific channels in your main server if you don't want to whitelist it
                    if server.id in [000000]:
                        do_delete = input(
                            f"Delete messages in {channel.name}: ")
                        if do_delete.lower() != "y":
                            continue
                        else:
                            await iterate_message_history(channel)
                    else:
                        await iterate_message_history(channel)


async def iterate_dms():
    for dm in client.private_channels:
        member = dm.recipient
        if member.id in whitelisted_dms:
            continue

        do_delete = input(f"Delete DMs with {member.name}: ")
        if do_delete.lower() != "y":
            continue
        else:
            await iterate_message_history(dm)


async def iterate_message_history(channel):
    delete_before = datetime.now() - timedelta(days=delete_before_days)
    async for m in channel.history(limit=9999):
        try:
            if m.author == client.user:
                if str(channel.type) == "text":
                    ch_name = m.channel.name
                elif str(channel.type) == "private":
                    ch_name = m.author.name

                if m.created_at < delete_before:
                    print(
                        f"{m.created_at} : {ch_name} : {m.clean_content[:50]}")
                    if dry_run == False:
                        await m.delete()
                        await asyncio.sleep(0.75)
        except Exception as e:
            print(f"Err: {e}")
            quit()


client.run(auth, bot=False)
