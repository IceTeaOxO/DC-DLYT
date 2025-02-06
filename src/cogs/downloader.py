import discord
from discord.ext import commands
import os
# import logging
from datetime import datetime
from ..utils.youtube_helper import YoutubeHelper
import json

with open('config/config.json', 'r') as f:
    config = json.load(f)

# logger = logging.getLogger('discord_bot')

class Downloader(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.youtube_helper = YoutubeHelper(config['download_path'])

    @commands.command(name='dl', aliases=['download'])
    async def download(self, ctx, url: str, format_type: str = 'mp3'):
        """
        下載 YouTube 影片/音樂
        使用方式: !download <YouTube URL> [mp3/mp4]
        """
        if format_type not in ['mp3', 'mp4']:
            await ctx.send("格式必須是 mp3 或 mp4")
            return

        try:
            # 記錄命令使用
            # logger.info(f"User: {ctx.author}, Command: download, URL: {url}, Format: {format_type}")

            # 檢查是否為播放清單
            if self.youtube_helper.is_playlist(url):
                msg = await ctx.send("這是一個播放清單。您想要下載整個播放清單嗎？ (回覆 'yes' 或 'no')")

                def check(m):
                    return m.author == ctx.author and m.channel == ctx.channel

                try:
                    response = await self.bot.wait_for('message', timeout=30.0, check=check)
                    if response.content.lower() != 'yes':
                        url = url.split('&list=')[0]  # 移除播放清單參數
                except TimeoutError:
                    await msg.edit(content="回應超時，取消下載。")
                    return

            # 顯示下載狀態
            queue_info = self.youtube_helper.get_queue_info()
            status_msg = await ctx.send(
                f"正在處理您的請求...\n"
                f"目前佇列中的下載數: {queue_info['current_downloads']}\n"
                f"預估等待時間: {queue_info['estimated_time']} 分鐘"
            )

            # 下載檔案
            filename = await self.youtube_helper.download(url, format_type)

            # 檢查檔案大小
            file_size = os.path.getsize(filename) / (1024 * 1024)  # 轉換為 MB
            if file_size > config['max_file_size']:
                # logger.warning(f"File too large: {filename} ({file_size}MB)")
                await ctx.send(f"檔案大小 ({file_size:.2f}MB) 超過 Discord 上傳限制 ({config['max_file_size']}MB)")
                os.remove(filename)
                return

            # 上傳檔案
            await ctx.send(file=discord.File(filename))
            os.remove(filename)  # 清理檔案

        except Exception as e:
            # logger.error(f"Download error: {str(e)}")
            await ctx.send(f"下載時發生錯誤: {str(e)}")

async def setup(bot):
    await bot.add_cog(Downloader(bot))