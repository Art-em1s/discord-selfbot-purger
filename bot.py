import discord
import requests

from datetime import datetime, timedelta
auth = ""
whitelisted_dms = []
whitelisted_guilds = []
whitelisted_channels = []
checked_servers = []
has_nuked = []
dry_run = False

client = discord.Client()


@client.event
async def on_message(msg):
    if msg.author == client.user and msg.content == "purge":
        await nuke()


async def nuke():
    print("Nuking messages...")
    await iterate_servers()
    await iterate_dms()


async def iterate_servers():
    global checked_servers
    for server in client.guilds:
        print(checked_servers)
        if server.id in whitelisted_guilds or server.id in has_nuked:
            print(
                f"Skipping: {server.name} | Whitelisted: {server.id in whitelisted_guilds} | Nuked: {server.id in has_nuked}")
            continue
        else:
            print(f"Scanning: {server.name}")
            for channel in server.channels:
                if str(channel.type) == "text" and channel.id not in whitelisted_channels and channel.permissions_for(channel.guild.me).send_messages:
                    print(f"    Scanning: {channel.name}")
                    await iterate_message_history(channel)
            checked_servers.append(server.id)


async def iterate_dms():
    for dm in client.private_channels:
        if dm.type == discord.ChannelType.private:
            name = dm.recipient.name
            member = dm.recipient
            if member.id in whitelisted_dms:
                continue
            if "Deleted User" in name:
                await iterate_message_history(dm)
            else:
                do_delete = input(f"Delete DMs with {name}: ")
                if do_delete.lower() != "y":
                    continue
                else:
                    await iterate_message_history(dm)
        elif dm.type == discord.ChannelType.group:
            name = f"{dm.name} | {', '.join([member.name for member in dm.recipients])}"
            await iterate_message_history(dm)


async def iterate_message_history(channel):
    delete_before = datetime.now() - timedelta(days=31)
    i = 0
    a = 1
    ch_name = None
    exit_loop = False
    last_message_timestamp = channel.created_at
    while True:
        if exit_loop:
            break
        messages = await channel.history(limit=10000, oldest_first=True, after=last_message_timestamp).flatten()

        if len(messages) == 0:
            break

        last_message_timestamp = messages[-1].created_at
        filtered_messages = [
            message for message in messages if message.author == client.user and not message.pinned]
        msg = f"    Got {len(messages)} | {len(filtered_messages)} from self | {i} messages deleted / {a*10000} scanned\n"
        if len(filtered_messages) == 0:
            print(msg)
        else:
            print(f"\n{msg}")

        if str(channel.type) == "text":
            ch_name = f"{channel.guild.name} | {channel.name}"
        elif str(channel.type) == "private":
            ch_name = f"DM: {channel.recipient}"
        elif str(channel.type) == "group":
            ch_name = f"Group DM: {', '.join([member.name for member in channel.recipients])}"

        a += 1

        if len(filtered_messages) == 0:
            continue

        for m in filtered_messages:
            try:

                print(
                    f"{m.created_at} : {ch_name} : {m.author.name} : {m.clean_content[:50]}...")

                if m.created_at < delete_before:
                    i += 1
                    await m.delete()
                    # await asyncio.sleep(0.75) #uncomment this out if you want to use discord whilst messages are being deleted
                else:
                    exit_loop = True
                    break
            except Exception as e:
                print(f"Err: {e}")
                pass
            
    if str(channel.type) in ["private", "group"]:
        await close_dm(channel.id)

    print(f"    Deleted {i} messages in {ch_name}")


async def close_dm(dm_id):
    url = f"https://discord.com/api/v9/channels/{dm_id}"
    requests.delete(url, headers={'authorization': auth})
    return

try:
    client.run(auth, bot=False)
except Exception as e:
    print(checked_servers)
