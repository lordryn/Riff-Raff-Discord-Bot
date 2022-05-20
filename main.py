import sqlite3
import os
import discord
import pytz as pytz
from dotenv import load_dotenv
import random
import datetime
import asyncio
from discord.utils import get


intents = discord.Intents.all()


# grabs discord bot token from .env file and initializes
load_dotenv()
my_secret = os.environ['DISCORD_TOKEN']
client = discord.Client(intents=intents)


@client.event
# debug items done after successful bot startup/reboot
async def on_ready():
    print(f'{client.user} has connected to Discord!'
          )  # discord connection verified
    await client.change_presence(activity=discord.Activity(type=discord.ActivityType.watching, name="the misfits and influencing elections on Facebook"))


    # time retrieval loop
    while True:
        cst = pytz.timezone('US/Central')
        now = datetime.datetime.now(cst)
        an_chan = client.get_channel(947328202483830794)
        refresh_time = 60  # time refresh rate in seconds

        # daily and weekly announcements

        if now.hour == 19 and now.minute == 00:
            announcement = 'A daily reset has occurrered!\n Don\'t forget You\'re daily challenges and free keys today!'
            print(announcement)
            if now.weekday() == 1:
                announcement = 'A weekly reset has occurred!'
            await an_chan.send(announcement)
            if now.weekday() == 3:
                announcement = '''Weekly cit build tick!\n
                      Don't forget to help cap the resources for the cit raffle!\n
                      Don't forget to use your clan cape xp!\n
                      Don't forget to collect your xp from the quartermaster after capping!\n
                      '''
            refresh_time = 120
        await asyncio.sleep(refresh_time)


@client.event
async def on_raw_reaction_add(payload):
    rules_message_id = 976923160387682358

    if rules_message_id == payload.message_id:
        print(f"new member->{payload.member}")
        member = payload.member
        guild = member.guild
        print(member.name)
        # emoji = payload.emoji.name
        # if emoji == '👍':
        role = discord.utils.get(guild.roles, name='Member')
        await member.add_roles(role)

@client.event
async def on_member_remove(member):
    leave_list = ['went to the wildy and never came back', 'forgot to bring waterskins to the desert', 'was dominated by the KBD', 'lost a 1v1 with Zezima', 'failed to many agility obstacles', ' was found by seasonal elf', 'Changed their title to "The Betrayed"']
    channel = client.get_channel(976928345897963600)
    list_length = len(leave_list) - 1
    print(f"{member.name}->left")
    await channel.send(f"{member} {leave_list[random.randint(0, list_length)]}.")



@client.event
# constantly monitors all channels the bot has access to and responds to keywords accordingly
async def on_message(message):
    username = str(message.author).split('#')[
        0]  # username grab and removal of discriminator
    user_message = str(message.content)
    channel = str(message.channel.id)

    # omits bot chats
    if message.author == client.user:
        return

    # help list of current commands, secret commands omitted
    if user_message.lower().split(' ')[0] == '!help':
        cmds = """Riff Raff Raffler by Lord Ryn \n
        Designed for the Misfit Marauders Discord\n
        !help - this menu(list of commands)\n
        !raffle - chooses a user that reacts to a post*\n
        !list - lists all users who react to a post*\n
        !rand or !random - chooses a random number 1-100\n
        !poll - currently adds a thumbs up and down to post\n
        !rswiki - creates a link based on post command text\n
        *list and raffle require you to be replying to the target post\n
        *raffle currently only works in a channel named 🎫weekly-raffle
        """
        await message.channel.send(cmds)

    # reacts to positive affirmation
    if user_message.lower() == 'good bot':
        print(f'{username}->{user_message}')
        await message.channel.send('💖')
    # todo add db access to tally affirmations

    # negative reaction to mark poor experience
    if user_message.lower() == 'bad bot':
        print(f'{username}->{user_message}')
        await message.channel.send('😔')

    # todo add suggestions command
    if user_message.lower().split(' ')[0] == '!bonghit':
        ma_id = '<@542436163395387407>'
        emoji = client.get_emoji(977020269682106419)
        await message.add_reaction(emoji)
        await message.channel.send(f'{ma_id} {username} has redeemed a bong hit!')
        print(f'{username}->bonghit ')
        

    # converts post command text to rswiki link
    if user_message.lower().split(' ')[0] == '!rswiki':
        command_removed = user_message.lower().replace('!rswiki ', '')
        item = command_removed.replace(' ', '_')
        link = f'https://runescape.wiki/w/{item}'
        print(f'{username}->{item}->{link}')
        await message.channel.send(f'Results for: {command_removed}\n  {link}')

    # bot greeting for testing
    if user_message.lower() == 'hello riff raff':
        print(f'{username}->{user_message}')
        await message.channel.send(f'Hello {username}')

    # generates a random number
    elif user_message.lower().split(' ')[0] == '!random' or user_message.lower().split(' ')[0] == '!rand':
        print(user_message.lower().split(' ')[0])
        try:
            randrange = int(user_message.lower().split(' ')[1])
        except IndexError:
            randrange = 100
        random_number = random.randrange(randrange)
        print(f'{username}->{user_message}->{random_number}')
        response = f'From 1-{randrange} I have chosen: {random_number}'  # todo add ability to specify the range
        await message.channel.send(response)

    # polling, thumbs up or down
    if user_message.lower().split(' ')[0] == '!poll':
        # todo? add number to specify multiple choice
        yn_emojis = ['\N{THUMBS UP SIGN}', '\N{THUMBS DOWN SIGN}']
        print(f'{username}->{user_message}')
        for emoji in yn_emojis:
            await message.add_reaction(emoji)

    # lists users that react to a post
    if user_message.lower().split(' ')[0] == '!list':
        print(f'{username}->{user_message}')
        msg_id = message.reference.message_id  # targets replied message
        chan = message.channel
        msg = await chan.fetch_message(msg_id)  # grabs target id

        # adds users to a dataset
        users = set()
        for reaction in msg.reactions:
            async for user in reaction.users():
                users.add(user)

        # user's names are extracted and posted
        await message.channel.send(
            f"users: {', '.join(user.name for user in users)}")
        print(f"users: {', '.join(user.name for user in users)}")

    # the main show, the raffle
    if message.channel.name != '#💬general':  # channel prerequisite, more may be added using and

        # raffle init
        if user_message.lower().split(' ')[0] == '!raffle':
            print(f'{username}->{user_message}')

            # sqlite database connect
            conn = sqlite3.connect('raffle.sqlite')
            cur = conn.cursor()

            # clears name table for fresh raffle
            cur.executescript('\n'
                              '			DROP TABLE IF EXISTS Name;\n'
                              '			CREATE TABLE Name (\n'
                              '				id     INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT UNIQUE,\n'
                              '				name   TEXT\n'
                              '			);\n'
                              '			')

            # Discord message scrape
            msg_id = message.reference.message_id
            chan = message.channel
            msg = await chan.fetch_message(msg_id)

            # creates set and grabs reacted users
            users = set()
            for reaction in msg.reactions:
                async for user in reaction.users():
                    users.add(user)

            # takes the userdata and commits the usernames to the database
            contestants = []
            for entrant in users:
                cur.execute(
                    'INSERT INTO Name (name)\n'
                    '					VALUES ( ? )', (str(entrant),))
                cur.execute('SELECT id FROM Name WHERE name = ? ',
                            (str(entrant),))
                conn.commit()
                contestants.append(entrant)  # debugging list of entrants

            # picks a winner
            cur.execute('''SELECT name FROM Name ORDER BY RANDOM() LIMIT 1'''
                        )  # there is room to have multiple winners
            winner = cur.fetchone()[0]

            # results message construction and push
            number_of_contestants = len(contestants)
            result = f"Out of {number_of_contestants} contestants, {winner} has won the raffle!"
            await message.channel.send(result)

            # debug print
            print(contestants)
            print(result)
    if user_message.lower().split(' ')[0] == '!announce':  # todo make anouncements work
        announcement = ''
    if user_message.lower().split(' ')[0] == '!chanid':
        await message.channel.send(channel)

    # weekly event


client.run(my_secret)
#
