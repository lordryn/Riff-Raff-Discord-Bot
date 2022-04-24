import sqlite3
import os
import discord
from dotenv import load_dotenv
import random

# grabs discord bot token from .env file and initializes
load_dotenv()
my_secret = os.environ['DISCORD_TOKEN']
client = discord.Client()


@client.event
# debug items done after successful bot startup/reboot
async def on_ready():
    print(f'{client.user} has connected to Discord!'
          )  # discord connection verified


@client.event
# constantly monitors all channels the bot has access to and responds to keywords accordingly
async def on_message(message):
    username = str(message.author).split('#')[
        0]  # username grab and removal of discriminator
    user_message = str(message.content)
    channel = str(message.channel.name)

    # omits bot chats
    if message.author == client.user:
        return

    # identifies bot dev, destroys bot lol
    # if username.lower() == 'lord ryn':
    #     emojis = [
    #         '<:LawRune:962174931502759936>', '<:BloodRune:962173212001726474>',
    #         '<:SoulRune:962165403948318812>',
    #         '<:NatureRune:962165392141344849>'
    #     ]

    # # adds emojis from above list
    # for emoji in emojis:
    #     await message.add_reaction(emoji)

    # help list of current commands, secret commands omitted
    if user_message.lower().split(' ')[0] == '!help':
        cmds = """Riff Raff Raffler by Lord Ryn \n
        Designed for the Misfit Marauders Discord\n
        !help - this menu(list of commands)\n
        !raffle - chooses a user that reacts to a post*\n
        !list - lists all users who react to a post*\n
        !rand or !random - chooses a random number 1-100\n
        !poll - currently adds a thumbs up and down to post\n
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
    if message.channel.name == '🎫weekly-raffle':  # channel prerequisite, more may be added using and

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
                entrant_id = cur.fetchone(
                )[0]  # came with the sqlite raffle code, but has no known usage
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

    # print('coined')
    # emoji = '<:GP:962161665229619210>'
    # await message.add_reaction(emoji)


client.run(my_secret)
#
