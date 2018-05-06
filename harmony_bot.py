import discord
from discord.ext import commands
import random
import datetime as dt
import subprocess
import logging
# ***Bot Settings BEGIN***
# Set logging level. Logs are outputted to STDOUT by default
logging.basicConfig(level=logging.INFO)
# Create bot object. Set the command prefix here, as well as a description for the bot.
prefix = '?' # Command prefix. Change to your liking.
bot_description = 'A bot inspired by ponies! Currently under development'
bot = commands.Bot(command_prefix=prefix, description=bot_description)
# Create Globals
global volume_level
# Set startup functionality. "Playing" status can be set in change_presence, usually used to display help command.
@bot.event
async def on_ready():
    print('Logged in as')
    print(bot.user.name)
    print(bot.user.id)
    print('------')
    await bot.change_presence(game=discord.Game(name='!help'))
    #global player #TODO delete the player value below
    volume_init(25)

# ***Bot Settings END***

# ***Bot Commands BEGIN.***
@bot.command()
async def ping():
    """📖You say ping, I say pong!"""
    await bot.say('Pong!')

@bot.command()
async def invite():
    """📖Shows invite link for bot!"""
    await bot.say("Invite me to your server!")
    await bot.say("DISCLAIMER: Harmony Bot is still in its testing period! Invite at your and your server's risk! Harmony and its creators are not responsible for damages. Harmony Bot is offered “as-is”, without warranty.")
    await bot.say("https://discordapp.com/oauth2/authorize?&client_id=348893458812895233&scope=bot&permissions=0")


@bot.command()
async def roll(dice: str):
    """📖Rolls an n-sided die n-times! e.g. 3d20"""
    try:
        roll_limit, die_type = map(int, dice.split('d'))
        result = ', '.join(str(random.randint(1, die_type)) for r in range(roll_limit))
        await bot.say(result)
    except:
        await bot.say("Needs to be in NdN format!")
        return

@bot.command(pass_context=True)
async def hours(ctx):
    """📖Is it real hours?"""
    server_id = ctx.message.server.id
    channels = bot.get_all_channels()
    channel_list = []
    for channel in channels:
        try:
            if channel.server.id == server_id and channel.type.name == 'voice':
                channel_list.append(str(channel))
        except Exception:
            print("Possible channel group hit.") # Discord's new "groups" are considered channels, but lack attributes.
    hour = dt.datetime.now().hour
    if hour >= 21 or hour < 6:
        princess = "🌙 Luna: \""
        conclusion = ", even though you should be asleep right now.\""
    else:
        princess = "☀ Celestia: \""
        conclusion = ", although playing in my sunlight could be just as fun.\""
    await bot.say(princess + "I think its real " + random.choice(channel_list) + " hours" + conclusion)

@bot.command()
async def viswax():
    """📖Vis Wax stats for Runescape"""
    await bot.say("Fetching prices...please wait...")
    output = subprocess.getoutput("printf '\n' | /home/pi/go/bin/viswax")
    output = output[:output.rfind('\n')]
    await bot.say(str(output))

@bot.group(pass_context=True)
async def play(ctx):
    """📖Play some audio in MusicBot channel!"""
    if ctx.invoked_subcommand is None:
        await bot.say('Invalid play command passed...')

@play.command(pass_context=True)
async def url(ctx, url):
    """📖Plays audio from a single URL"""
    # Stop current audio playing.
    try:
        player
        if player.is_playing:
            player.stop()
    except:
        pass
    server_id = ctx.message.server.id
    channel = bot.get_channel('300454519467409410')
    channel_name = channel.name
    # Create voice object globally, set encoding options, connect to channel.
    global voice
    try:
        # Check if voice object exists
        voice
        #pass
    except NameError:
        # If voice object doesnt exist, make it and set it up.
        voice = await bot.join_voice_channel(channel) # Create voice and join channel
        await bot.say("Connected to channel!")
        discord.VoiceClient.encoder_options(voice, sample_rate=48000, channels=1) # Set encoder options
    else:
        # If voice object exists, check if its connected. If not, reconnect and set encoder options.
        if voice.is_connected() is False:
            voice = await bot.join_voice_channel(channel)
            await bot.say("Reconnected to channel!")
            discord.VoiceClient.encoder_options(voice, sample_rate=48000, channels=1)

    # Voice should be connected, bot will begin to buffer audio
    await bot.say("Buffering...")
    # Create audio player object.
    global player
    try:
        player = await voice.create_ytdl_player(url) # Get audio stream from URL, assign to player
    except:
        # Excepts if the url does not work. This currently does not work, I'll have to figure it out.
        await bot.say("Invalid url!")
        return
    # With voice connected and player set up, notify user and begin audio playback.
    await bot.say("Hear me in " + channel_name)
    player.volume = volume_level
    player.start()
def volume_init(input):
    new_volume = volume_manipulator(input)
    if new_volume is False:
        print("Initial volume out of bounds, using default value instead!")
        volume_level = 0.1
    else:
        print("Initialized volume set to " + str(input) + "%")
        volume_level = new_volume


def volume_manipulator(input):
    # Set the adjusted min and max volumes. These are floats between 0 and 2.0
    max = 0.4
    min = 0.0
    input = float(input)
    # The user will enter a number range of 0-100. The number will be adjusted proportionately to the "max" value
    vol_adjusted = input / 250  # 250 will adjust the volume proportionately to 0.4.
    # Check if user input is within range. Adjust volume if it is. Adjust values as necessary.
    if vol_adjusted > max or vol_adjusted < min:
        return False
    else: return vol_adjusted


@play.command()
async def volume(vol = None):
    """📖Set the volume for Harmony"""
    # Calling "!play volume" will display the current volume
    if vol is None:
        try:
            await bot.say("Current volume is " + str(player.volume * 250) + "/100")
            return
        except TypeError:
            pass
        except:
            await bot.say("Cant show volume if the player hasn't been started at least once!")
            return
    new_volume = volume_manipulator(vol)
    if new_volume is False:
        await bot.say("Must be between 0 and 100!")
        return
    else: volume_level = new_volume
    try:
        player.volume = new_volume
        await bot.say("Volume is now " + str(player.volume * 250) + "/100")
    except Exception:
        await bot.say("Volume set to " + str(volume_level * 250) + ". Will be applied to next reconnect.")

@bot.command()
async def stop():
    """📖Stops the audio stream and disconnects Harmony from voice."""
    #Uses the global object variables declared in "url" function
    try:
        # Check if object "player" exists
        player
    except NameError:
        # If object "player" non-existent, display error message
        await bot.say("Player never existed, so nothing to stop here!")
    else:
        # If exists, Stop the player object
        if player.is_playing:
            player.stop()
            await bot.say("Audio stopped!")
    try:
        # Check if object "voice" exists
        voice
    except:
        # If non-existent, display error message
        await bot.say("Error: Voice connection never existed!")
    else:
        # If exists, disconnect the voice client.
        if voice.is_connected() is True:
            await voice.disconnect()
            await bot.say("Successful disconnect. Goodbye!")

@bot.command(pass_context=True)
async def who(ctx, name : str):
    pass

# ***Bot Commands END***

# Statements to run the bot and load its dependencies.
opus_linux = '/usr/lib/arm-linux-gnueabihf/libopus.so.0' # Modify architecture directory appropriately
opus_win = 'opus'
opus_win64 = 'opus64'
# Load libopus-0
discord.opus.load_opus(opus_win64)
# Open your application token. REMEMBER TO KEEP THE TOKEN KEY PRIVATE!
tk_file = open('C:\\discordbot_token.txt', 'r')
token = str.strip(tk_file.read())
# Run HarmonyBot using your token.
try:
    bot.run(token)
except InvalidArguement:
    print("Launch failed! Did you provide a valid token?")
