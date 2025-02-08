import yt_dlp
import os
import asyncio
from typing import Dict, Optional
import re

class YoutubeHelper:
    def __init__(self, download_path: str):
        # self.download_path = download_path
        # self.current_downloads = {}
        # 將相對路徑轉換為絕對路徑
        self.download_path = os.path.abspath(download_path)
        self.current_downloads = {}
        
        # 確保下載目錄存在
        try:
            os.makedirs(self.download_path, exist_ok=True)
            os.chmod(self.download_path, 0o777)
        except Exception as e:
            raise Exception(f"無法創建下載目錄 {self.download_path}: {str(e)}")
        
    def sanitize_filename(self, filename: str) -> str:
        # 移除或替換不安全的字符
        filename = re.sub(r'[\\/*?:"<>|⧸/]', '_', filename)  # 修改這行，將所有特殊字符替換為底線
        # 移除多餘的空格
        filename = ' '.join(filename.split())
        # 確保文件名不以點或空格開始或結束
        filename = filename.strip('. ')
        return filename
    
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
        # 再次確認目錄存在
        if not os.path.exists(self.download_path):
            os.makedirs(self.download_path)
        try:
            with yt_dlp.YoutubeDL({'quiet': True}) as ydl:
                    info = ydl.extract_info(url, download=False)
                    safe_title = self.sanitize_filename(info['title'])

            # 設置下載選項，使用安全的文件名
            ydl_opts = {
                'format': 'bestaudio/best' if format_type == 'mp3' else 'best',
                'outtmpl': os.path.join(self.download_path, f'{safe_title}.%(ext)s'),
                'progress_hooks': [progress_hook] if progress_hook else [],
                'keepvideo': True,
                'noprogress': True,
                'nooverwrites': True,
            }

            if format_type == 'mp3':
                ydl_opts.update({
                    'postprocessors': [{
                        'key': 'FFmpegExtractAudio',
                        'preferredcodec': 'mp3',
                        'preferredquality': '192',
                    }],
                })

            # 執行下載
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                ydl.download([url])
            
            # 構建最終文件名
            final_filename = os.path.join(self.download_path, f"{safe_title}.{format_type}")
            
            # 等待文件出現（最多等待5秒）
            for _ in range(50):
                if os.path.exists(final_filename):
                    return final_filename
                await asyncio.sleep(0.1)
            
                raise Exception(f"無法找到下載的文件: {final_filename}")
        
        except Exception as e:
            raise Exception(f"下載失敗: {str(e)}")

    def is_playlist(self, url: str) -> bool:
        return 'list=' in url

    def get_queue_info(self) -> Dict:
        return {
            'current_downloads': len(self.current_downloads),
            'estimated_time': len(self.current_downloads) * 2  # 預估每個下載需要2分鐘
        }