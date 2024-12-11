import yt_dlp
import os
import asyncio
from typing import Dict, Optional

class YoutubeHelper:
    def __init__(self, download_path: str):
        self.download_path = download_path
        self.current_downloads = {}

    async def get_video_info(self, url: str) -> Dict:
        ydl_opts = {
            'quiet': True,
            'no_warnings': True,
            'extract_flat': True,
        }
        
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            try:
                info = ydl.extract_info(url, download=False)
                return info
            except Exception as e:
                raise Exception(f"無法獲取影片資訊: {str(e)}")

    async def download(self, url: str, format_type: str = 'mp3', progress_hook=None) -> str:
        ydl_opts = {
            'format': 'bestaudio/best' if format_type == 'mp3' else 'best',
            'outtmpl': os.path.join(self.download_path, '%(title)s.%(ext)s'),
            'progress_hooks': [progress_hook] if progress_hook else [],
        }

        if format_type == 'mp3':
            ydl_opts.update({
                'postprocessors': [{
                    'key': 'FFmpegExtractAudio',
                    'preferredcodec': 'mp3',
                    'preferredquality': '192',
                }],
            })

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            try:
                info = await asyncio.get_event_loop().run_in_executor(
                    None, lambda: ydl.extract_info(url, download=True)
                )
                if format_type == 'mp3':
                    filename = os.path.join(self.download_path, f"{info['title']}.mp3")
                else:
                    filename = os.path.join(self.download_path, f"{info['title']}.mp4")
                return filename
            except Exception as e:
                raise Exception(f"下載失敗: {str(e)}")

    def is_playlist(self, url: str) -> bool:
        return 'list=' in url

    def get_queue_info(self) -> Dict:
        return {
            'current_downloads': len(self.current_downloads),
            'estimated_time': len(self.current_downloads) * 2  # 預估每個下載需要2分鐘
        }