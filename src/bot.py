import discord
from discord.ext import commands
import json
# import logging
import os
from datetime import datetime
import sys
import os
import asyncio
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
# 設定日誌
# logging.basicConfig(
#     level=logging.INFO,
#     format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
#     handlers=[
#         logging.FileHandler('logs/bot.log', encoding='utf-8'),
#         logging.StreamHandler()
#     ]
# )
# logger = logging.getLogger('discord_bot')

# 載入設定
with open('config/config.json', 'r') as f:
    config = json.load(f)

# 建立下載目錄
if not os.path.exists(config['download_path']):
    os.makedirs(config['download_path'])

# 設定 Intent
intents = discord.Intents.default()
intents.message_content = True

# 建立 Bot 實例
bot = commands.Bot(command_prefix=config['prefix'], intents=intents)


@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.errors.MissingRequiredArgument):
        await ctx.send(f"缺少必要參數。請使用 `{config['prefix']}help` 查看命令用法。")
    else:
        # logger.error(f'Error: {str(error)}')
        await ctx.send(f"發生錯誤: {str(error)}")

# 修改 run_bot 函數
async def setup():
    # logger.info(f'Bot logged in as {bot.user}')
    await bot.load_extension('src.cogs.downloader')

def run_bot():
    # 在啟動 bot 前載入擴展
    asyncio.run(setup())
    bot.run(config['token'])

