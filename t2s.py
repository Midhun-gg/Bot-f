import asyncio
import edge_tts
import pygame
import time
import os
import io

async def _speak_async(text: str, voice: str = "en-US-AriaNeural", output_buffer: io.BytesIO = None):
    communicate = edge_tts.Communicate(text, voice)
    
    if output_buffer:
        async for chunk in communicate.stream():
            if chunk["type"] == "audio":
                output_buffer.write(chunk["data"])
    else:
        await communicate.save("bot_response.mp3")

def speak(text: str, output_buffer: io.BytesIO = None):
    if output_buffer:
        asyncio.run(_speak_async(text, output_buffer=output_buffer))
    else:
        asyncio.run(_speak_async(text))
        time.sleep(0.1)
        pygame.mixer.init()
        pygame.mixer.music.load("bot_response.mp3")
        pygame.mixer.music.play()
        while pygame.mixer.music.get_busy():
            pygame.time.Clock().tick(1)

        pygame.mixer.quit()
        os.remove("bot_response.mp3")
