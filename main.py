import discord
from discord.ext import commands
import datetime
import sys
import random

import secrets
import attributes
import rolesystem
import usefulshit

client = commands.Bot(secrets.PREFIX)


@client.event
async def on_ready():
    print("Started. Logged in as: {}".format(client.user.name))
    await client.change_presence(status=discord.Status.online, activity=discord.Game("Re:Zero Season 2"))
    await rolesystem.rollenverteilung(client)
    await usefulshit.leaveallguilds(client)


@client.event
async def on_member_join(member):
    blacklist_id = 503838726267600918
    log_id = 503902406724026370

    if (member.created_at + datetime.timedelta(minutes=15)) > member.joined_at:
        await client.ban(member)
        try:
            await client.send_message(member, "Your Accounts needs to be older than 15 minutes.")
        except(discord.errors.Forbidden):
            print("An Error has occured.")
        await client.unban(member)
        await client.send_message(
            client.get_channel(log_id),
            "User **{}** tried to join the Server. Account was younger than 15 minutes.".format(member.mention))
        return

    else:
        username = member.name
        guild = member.server

        blacklist = []
        async for message in client.logs_from(client.get_channel(blacklist_id)):
            blacklist.append(message)

        for message in blacklist:
            if message.content in username:
                word = message.content
                try:
                    await client.send_message(member,
                                              "**Error:** Your Username contains a banned word (" + message.content + ").")
                except(discord.errors.Forbidden):
                    print("An Error has occured.")
                await client.ban(member)
                await client.unban(guild, member)

                await client.send_message(
                    client.get_channel(log_id),
                    "User **{}** tried to join the Server. Kicked because of **{}**".format(member.mention, word))
                return


@client.event
async def on_reaction_add(reaction, user):

    if reaction.message.id in attributes.rolemessageid and user.bot is False:
        roleid = await rolesystem.emojitorole(reaction)
        role = reaction.message.guild.get_role(int(roleid))
        await user.add_roles(role)


@client.event
async def on_reaction_remove(reaction, user):
    if reaction.message.id in attributes.rolemessageid and user.id != client.user.id:
        roleid = await rolesystem.emojitorole(reaction)
        role = reaction.message.guild.get_role(int(roleid))
        await user.remove_roles(role)


@client.event
async def on_member_ban(guild, user):

    messagetext = user.name + "* (" + str(user.id) + ") was banned."
    await log(messagetext)


@client.event
async def on_message_delete(message):
    if message.author.bot is False:
        attachments = message.attachments
        attachtext = ""
        if not attachments:
            attachtext = "None"
        else:
            for attachment in attachments:
                attachtext += "\n" + attachment.url
        messagetext = "A message was deleted:\n" + message.clean_content \
                      + "\nAuthor: " + message.author.name \
                      + "\nAttachments: " + attachtext
        await log(messagetext)


# -----------------
# -------------------


@client.command(pass_context=True)
async def hallo(ctx):
    await ctx.channel.send("Hallo")


@client.command(pass_context=True)
@commands.has_permissions(manage_messages=True)
async def clear(ctx, amount=2):

    channel = ctx.channel

    messages = []

    async for message in channel.history(limit=amount+1):
        messages.append(message)

    await channel.delete_messages(messages)
    await usefulshit.logmessage(ctx, len(messages)-1)


@client.command(pass_context=True)
@commands.has_permissions(manage_messages=True)
async def sclear(ctx, keyword):

    channel = ctx.channel

    messages = []

    async for message in channel.history(limit=99):
        if keyword.lower() in message.content.lower():
            messages.append(message)

    await channel.delete_messages(messages)
    await usefulshit.logmessage(ctx, len(messages)-1)


@client.command(pass_context=True)
@commands.has_permissions(manage_messages=True)
async def uclear(ctx, member: discord.User):

    channel = ctx.channel
    messages = []

    async for message in channel.history(limit=100):
        if message.author.id == member.id:
            messages.append(message)

    messages.append(message)

    await channel.delete_messages(messages)
    await usefulshit.logmessage(ctx, len(messages)-1)


@client.command(pass_context=True)
@commands.has_permissions(administrator=True)
async def bans(ctx):

    messagetext = ""
    bans = await ctx.guild.bans()

    for ban in bans:
        username = await usefulshit.deleteduser(client, ban[1].name)
        messagetext += "◘ ``" + username + "#" + ban[1].discriminator + "``\n"

    await ctx.channel.send(messagetext)


@client.command()
async def info():
    await client.say(
        "A private bot for the mint_gaming network.\nMade by Noro#0676 \nPrefix: ``{}``".format(secrets.PREFIX))


@client.command(pass_context=True)
@commands.has_permissions(administrator=True)
async def shutdown(ctx):
    await ctx.channel.send("``>Shutting down...`` ")
    try:
        sys.exit(0)
    except:
        print("Shutdown Error")


@client.command(pass_context=True)
async def kekse(ctx):

    zufallszahl = random.randint(1, 11)
    messagetext = ""
    i=0

    while i < zufallszahl:
        messagetext += "<:keks:400369264009150464> "
        i = i+1

    await client.send_message(ctx.message.channel, messagetext)


@client.command(pass_context=True)
@commands.has_permissions(manage_guild=True)
async def roles(ctx):
    await ctx.channel.send("Reloading...")
    await rolesystem.rollenverteilung(client)


@client.command(pass_context=True)
@commands.has_permissions(manage_guild=True)
async def nsfw(channel):
    if channel.is_nsfw():
        await channel.edit(nsfw=False)
        await channel.send("NSFW: Off")
    else:
        await channel.edit(nsfw=True)
        await channel.send("NSFW: On")


async def log(message):
    serverid = client.get_guild(attributes.mint_serverid)
    for channel in serverid.channels:
        if channel.name == "yvred-log":
            embed = discord.Embed(title="Log", description=message, color=0xb9babd)
            await channel.send(embed=embed)


# -----------------
# -------------------
# -----------------


client.run(secrets.TOKEN)
