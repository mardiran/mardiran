import discord
from discord.ext import commands
from discord import app_commands
import aiohttp
import logging
from colorama import init, Fore, Style
import time
import random

init(autoreset=True)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

RANDOM_COLORS = [
    discord.Color.red(),
    discord.Color.blue(),
    discord.Color.green(),
    discord.Color.purple(),
    discord.Color.orange(),
    discord.Color.teal(),
    discord.Color.magenta(),
    discord.Color.gold(),
    discord.Color.dark_red(),
    discord.Color.dark_blue()
]

class MyBot(commands.Bot):
    def __init__(self):
        intents = discord.Intents.default()
        intents.messages = True
        intents.guilds = True
        intents.message_content = True
        super().__init__(command_prefix="!", intents=intents)
        self.chat_log_settings = {}

    async def setup_hook(self):
        try:
            await self.tree.sync()
            logger.info("Synchronized slash commands")
        except Exception as e:
            logger.error(f"Error syncing slash commands: {e}")

    async def on_ready(self):
        try:
            activity = discord.Activity(
                type=discord.ActivityType.watching,
                name=" Your Massages 👀"  # Bot Activity
            )
            await self.change_presence(activity=activity) 

            ascii_art = [
                "╔══════════════════════════════════════╗",
                "║                                      ║",
                "║          M A R D I R A N             ║",
                "║                                      ║",
                "║     Creator of Bot Chat Logger       ║",
                "║        Powered by Python             ║",
                "╚══════════════════════════════════════╝"
            ]
            colors = [Fore.RED, Fore.YELLOW, Fore.GREEN, Fore.CYAN, Fore.BLUE, Fore.MAGENTA, Fore.WHITE]
            
            print("\n" + Fore.CYAN + "🚀 Bot is booting up..." + Style.RESET_ALL)
            for i, line in enumerate(ascii_art):
                print(colors[i % len(colors)] + line + Style.RESET_ALL)
                time.sleep(0.2)
            print(Fore.GREEN + f"✅ {self.user} is now online!" + Style.RESET_ALL + "\n")
            
            logger.info(f"Bot connected as {self.user}")
        except Exception as e:
            logger.error(f"Error in on_ready: {e}")

    async def on_message(self, message):
        if message.author.bot:
            return

        if message.channel.id in self.chat_log_settings:
            try:
                log_channel_id, webhook_url = self.chat_log_settings[message.channel.id]
                log_channel = self.get_channel(log_channel_id)
                if not log_channel:
                    logger.error(f"Log channel {log_channel_id} not found")
                    return
                if not webhook_url:
                    logger.error(f"No webhook URL for channel {message.channel.id}")
                    return

                embed = discord.Embed(
                    title="New Message",
                    description=f"**Message:**\n{message.content or 'No text content'}",
                    color=random.choice(RANDOM_COLORS),
                    timestamp=message.created_at
                )
                embed.set_author(name=str(message.author), icon_url=message.author.avatar.url if message.author.avatar else None)
                embed.set_footer(text=f"User ID: {message.author.id}")

                async with aiohttp.ClientSession() as session:
                    try:
                        webhook = discord.Webhook.from_url(webhook_url, session=session)
                        await webhook.send(
                            embed=embed,
                            username=str(message.author),
                            avatar_url=message.author.avatar.url if message.author.avatar else None
                        )
                    except discord.InvalidArgument:
                        logger.error(f"Invalid webhook URL for channel {message.channel.id}")
                    except aiohttp.ClientError as e:
                        logger.error(f"Network error sending webhook: {e}")
                    except Exception as e:
                        logger.error(f"Unexpected error sending webhook: {e}")
            except Exception as e:
                logger.error(f"Error processing message in channel {message.channel.id}: {e}")

        try:
            await self.process_commands(message)
        except Exception as e:
            logger.error(f"Error processing commands: {e}")

@app_commands.command(name="setlog", description="Sets up a chat log for a channel")
@app_commands.describe(
    main_channel="The channel to log messages from",
    log_channel="The channel to send logs to",
    webhook_url="The webhook URL for logging"
)
@app_commands.default_permissions(administrator=True)
async def setlog(interaction: discord.Interaction, main_channel: discord.TextChannel, log_channel: discord.TextChannel, webhook_url: str):
    try:
        async with aiohttp.ClientSession() as session:
            webhook = discord.Webhook.from_url(webhook_url, session=session)
            try:
                await webhook.fetch()
            except discord.InvalidArgument:
                await interaction.response.send_message("Invalid webhook URL provided.", ephemeral=True)
                return
            except aiohttp.ClientError as e:
                await interaction.response.send_message(f"Failed to validate webhook: {e}", ephemeral=True)
                return

        bot.chat_log_settings[main_channel.id] = (log_channel.id, webhook_url)
        logger.info(f"Chat log set for channel {main_channel.id} to log channel {log_channel.id}")
        await interaction.response.send_message("Chat log setup successfully!", ephemeral=True)
    except Exception as e:
        logger.error(f"Error setting chat log: {e}")
        await interaction.response.send_message("An error occurred while setting up the chat log.", ephemeral=True)

bot = MyBot()
bot.tree.add_command(setlog)
try:
    bot.run("Token")  # Your Bot Token
except discord.errors.LoginFailure:
    logger.error("Invalid bot token provided")
except Exception as e:
    logger.error(f"Error running bot: {e}")