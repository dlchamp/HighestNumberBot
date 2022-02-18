from re import findall
from json import load, dump
from os import getenv, path
from dotenv import load_dotenv
from disnake.ext import commands
from disnake import Intents, Embed
from disnake.ui import View, Button

# declare intents and initialize bot as client
intents = Intents.default()
intents.members = True
bot = commands.Bot(command_prefix="-", intents=intents, help_command=None)

# Load the current high number from JSON
def get_number():
    with open("./number.json") as f:
        data = load(f)
    if data["high_number"] is None:
        return 0
    return data["high_number"]


# update the high number, member_id, and message url
def update_data(number: int, member_id: int, message_url: str):
    # open the JSON and load into data variable
    with open("./number.json") as f:
        data = load(f)
    # update the value for high_number
    data["high_number"] = number
    data["member_id"] = member_id
    data["url"] = message_url

    # dump the new data dict to json
    with open("./number.json", "w") as f:
        dump(data, f, indent=4)


def get_top():
    with open("./number.json") as f:
        data = load(f)

    number = data["high_number"]
    member_id = data["member_id"]
    url = data["url"]

    return number, member_id, url


# create number.json if it does not exist
def check_numbers_file():
    if not path.isfile("number.json"):
        print("number.json is missing - creating file...")
        data = {}
        data["high_number"] = 0

        with open("./number.json", "w") as f:
            dump(data, f, indent=4)


@bot.listen()
async def on_ready():
    print(f"Bot has connected as {bot.user}")


@bot.listen()
async def on_message(message):
    # verify message is not from a bot account
    if message.author.bot:
        return
    # get clean message content, user mentions return name instead of ID
    msg = message.clean_content.lower()
    # use regex to searc for all instances of up to 10 digit numbers
    numbers = findall(r"\d{1,10}", msg)
    """
    check the length of numbers list,
    if greater than 0, get the current high number from number.txt
    """
    if len(numbers) > 0:
        current_high_num = get_number()

        # convert numbers list items (str) to (int) items
        int_map = map(int, numbers)
        numbers = list(int_map)

        # sort lowest to highest, get highest number from message list of numbers
        numbers.sort()
        highest_in_message = numbers[-1]

        # check if message high num  is greater than current high num, if true, update current high number
        if highest_in_message > current_high_num:
            update_data(highest_in_message, message.author.id, message.jump_url)


# slash command - return an embed response to the channel for the highest number, the author, and link to message
@bot.slash_command(
    name="top",
    description="See who holds the record for the highest number mentioned in messages.",
)
async def rank_command(inter):
    guild = inter.guild
    number, member_id, url = get_top()
    member = guild.get_member(int(member_id))

    # setup view with url button
    view = View(timeout=None)
    view.add_item(Button(label="Jump to Message", url=url))

    # Build the embed
    embed = Embed(title=f"Top Number: {number}")
    embed.add_field(name="Member:", value=f"{member.mention}")

    await inter.response.send_message(embed=embed, view=view)


if __name__ == "__main__":
    """
    Start script
    - create number.txt and write '0' if not exists
    - load token from .env
    - run the bot, auth with token
    """
    check_numbers_file()
    load_dotenv()
    bot.run(getenv("TOKEN"))
