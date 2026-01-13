import discord
from discord.ext import commands
import logging
from dotenv import load_dotenv
import os
import openrouterai
import threading
from http.server import HTTPServer, BaseHTTPRequestHandler

class HealthHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"OK")

def start_server():
    port = int(os.environ.get("PORT", 10000))
    server = HTTPServer(("0.0.0.0", port), HealthHandler)
    server.serve_forever()

threading.Thread(target=start_server, daemon=True).start()


load_dotenv()
token = os.getenv('DISCORD_TOKEN')
handler = logging.FileHandler(filename='discord.log', encoding='utf-8', mode='w')
intents = discord.Intents.default()
intents.message_content = True
intents.members = True

bot = commands.Bot(command_prefix='!', intents=intents)

bot_role_1 = "sockfive"


@bot.event
async def on_ready():
    print(f"Bot is ready, {bot.user.name}")


@bot.event
async def on_member_join(member):
    await member.send(f"Welcome to the server {member.name}")


def ai_check_for_swearing(message):
    response = openrouterai.chat_devstral("With this following message reply with only f\"true\" if it "
                                          f"contains something which is offensive: {message}")
    print(response)
    if response == "true":
        return True
    return False


@bot.event
async def on_message(message):
    if message.author == bot.user:
        return
    if "shit" in message.content.lower():
        await message.delete()
        await message.channel.send(f"{message.author.mention} sybau")

    await bot.process_commands(message)


@bot.command()
async def hello(ctx):
    await ctx.send(f"Hello {ctx.author.mention}!")


@bot.command()
async def replyai(ctx, *, msg):
    await ctx.send(f"{ctx.author.mention}, here is your response")
    # print(msg)
    response = openrouterai.chat_devstral(f"Using the following message: {msg},"
                                          f" write a response in under 50 words & no non-english characters.")
    await ctx.send(f"{response}")


@bot.command()
async def assign(ctx):
    role = discord.utils.get(ctx.guild.roles, name=bot_role_1)
    if role:
        await ctx.author.add_roles(role)
        await ctx.send(f"{ctx.author.mention} is now assigned to {bot_role_1}")
    else:
        await ctx.send("Role doesn't exist")


@bot.command()
async def remove(ctx):
    role = discord.utils.get(ctx.guild.roles, name=bot_role_1)
    if role:
        await ctx.author.remove_roles(role)
        await ctx.send(f"{ctx.author.mention} has had {bot_role_1} removed")
    else:
        await ctx.send("Role doesn't exist")


@bot.command()
async def dm(ctx, *, msg):
    await ctx.author.send(f"You said {msg}")


@bot.command()
async def reply(ctx):
    await ctx.reply("This is a reply to your message.")


@bot.command()
async def poll(ctx, *, question):
    embed = discord.Embed(title=f"Poll by {ctx.author.mention}", description=question)
    poll_message = await ctx.send(embed=embed)
    await poll_message.add_reaction("👎")
    await poll_message.add_reaction("👍")


@bot.command()
@commands.has_role(bot_role_1)
async def secret(ctx):
    await ctx.send("Welcome to the club")


@secret.error
async def secret_error(ctx, error):
    if isinstance(error, commands.MissingRole):
        await ctx.send("You do not have permission.")


bot.run(token, log_handler=handler, log_level=logging.DEBUG)
