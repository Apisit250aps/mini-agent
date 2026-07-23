from pathlib import Path
import os
from pytubefix import YouTube, Search
from agents import Agent, Runner, function_tool


@function_tool
def search_youtube(query: str, limit: int = 10) -> list[dict]:
    """
    ค้นหาวิดีโอจาก YouTube

    Args:
        query: คำค้นหา
        limit: จำนวนเพลงที่ต้องการค้นหา

    Returns:
        รายการเพลงพร้อม URL
    """

    search = Search(query)
    results = search.videos[:limit]

    return [
        {
            "title": video.title,
            "url": video.watch_url,
        }
        for video in results
    ]


@function_tool
def download_youtube_video(url: str) -> str:
    """
    ดาวน์โหลดวิดีโอ YouTube จาก URL
    """

    try:
        output_dir = Path("downloads")
        output_dir.mkdir(exist_ok=True)

        yt = YouTube(url)

        stream = (
            yt.streams
            .filter(
                progressive=True,
                file_extension="mp4"
            )
            .order_by("resolution")
            .desc()
            .first()
        )

        if stream is None:
            return f"ดาวน์โหลดไม่ได้: {yt.title}"

        file_path = stream.download(
            output_path=str(output_dir)
        )

        return f"ดาวน์โหลดสำเร็จ: {file_path}"

    except Exception as e:
        return f"ดาวน์โหลดไม่สำเร็จ: {str(e)}"


@function_tool
def search_and_download_song(query: str) -> str:
    """
    ค้นหาและดาวน์โหลดเพลงจาก YouTube อัตโนมัติ โดยจะเลือกผลลัพธ์แรกที่ค้นเจอ (ดาวน์โหลดเป็นไฟล์เสียง)
    
    Args:
        query: ชื่อเพลงหรือคำค้นหา
        
    Returns:
        ข้อความแจ้งผลการดาวน์โหลดพร้อม path ของไฟล์ที่บันทึก
    """
    try:
        # 1. ค้นหาเพลง
        search = Search(query)
        results = search.videos
        
        if not results:
            return f"ไม่พบเพลงสำหรับคำค้นหา: {query}"
            
        video = results[0]
        url = video.watch_url
        title = video.title
        
        # 2. ดาวน์โหลดไฟล์เสียง
        output_dir = Path("downloads")
        output_dir.mkdir(exist_ok=True)

        yt = YouTube(url)
        
        # เลือก stream ที่เป็น audio อย่างเดียว
        stream = (
            yt.streams
            .filter(only_audio=True)
            .order_by('abr')
            .desc()
            .first()
        )

        if stream is None:
            return f"ไม่สามารถดาวน์โหลดไฟล์เสียงได้สำหรับ: {title}"

        file_path = stream.download(output_path=str(output_dir))
        
        if not file_path:
            return f"ดาวน์โหลดไฟล์ไม่สมบูรณ์ หรือไม่ทราบที่อยู่ไฟล์สำหรับ: {title}"
            
        file_path_str = str(file_path)
        
        # เปลี่ยนนามสกุลไฟล์เป็น .mp3 เพื่อความสะดวก
        base, _ = os.path.splitext(file_path_str)
        new_file = base + '.mp3'
        
        # ลบไฟล์เดิมถ้ามีอยู่แล้ว
        if os.path.exists(new_file):
            os.remove(new_file)
            
        os.rename(file_path_str, new_file)

        return f"ค้นหาและดาวน์โหลดเพลงสำเร็จ: {title} (บันทึกไว้ที่ {new_file})"

    except Exception as e:
        return f"ค้นหาและดาวน์โหลดไม่สำเร็จ: {str(e)}"