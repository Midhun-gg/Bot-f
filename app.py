import asyncio
import ollama
from fastapi import FastAPI, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from s2t import listen_to_user_whisper
from t2s import speak
import json
from typing import List, Dict
import io
import soundfile as sf
import noisereduce as nr
import os
import tempfile
from pydub import AudioSegment

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

model = 'bot'
global conversation_state

conversation_state = {
    "conversation": [],
    "iteration": 0,
    "max_iterations": 5
}

async def ask(prompt: str, conversation_history: List[Dict]):
    try:
        limited_prompt = f"{prompt}\n\nPlease respond in no more than 20 words. Be concise and clear. Ask engaging questions that can be answered in a few words."
        messages = conversation_history + [{"role": "user", "content": limited_prompt}]
        response = await asyncio.to_thread(ollama.chat, model=model, messages=messages)
        return response['message']['content']
    except Exception as e:
        print("Error in asking the LLM:", e)
        return "I'm sorry, I couldn't process that."

@app.post("/initial-greeting")
async def initial_greeting():
    initial_prompt = """Greet the user, be concise and avoid special characters like *, &, %, etc.
                        and the questions can be about anything but they should be as concise as 
                        possible. Ask moderate level questions that can be answered in a few words.
                        Do not ask questions that require long answers or explanations."""
    bot_response = await ask(initial_prompt, [])
    conversation_state["conversation"].append({"role": "assistant", "content": bot_response})
    return {"response": bot_response}

@app.post("/final-greeting")
async def final_greeting():

    global conversation_state
    
    final_prompt = """You are ending a conversation. Do not greet the user again.Give a response to the prompt by the user and after that thank the user for the conversation, and give a warm, friendly closing message. End the conversation with a positive note, and do not ask any questions.Do not ask any questions, just provide a warm closing message, after responding to user said"""
    
    bot_response = await ask(final_prompt, conversation_state["conversation"])
    conversation_state["conversation"].append({"role": "assistant", "content": bot_response})
    return {"response": bot_response}


@app.post("/summary-generation")
async def summary_generation():
    global conversation_state
    
    # Check if there's conversation data to summarize
    if len(conversation_state["conversation"]) > 0:
        summary_prompt = "Give a brief summary of this conversation after analysing the conversation between the user and the bot in around 40 words\n" + \
                         "\n".join([f"{msg['role']}: {msg['content']}" for msg in conversation_state["conversation"]])
        
        summary = await ask(summary_prompt, [])
        
        # Reset conversation state after generating summary
        conversation_state = {
            "conversation": [],
            "iteration": 0,
            "max_iterations": 5
        }
        
        return {
            "response": summary,
            "is_summary": True,
            "conversation": []
        }
    else:
        return {
            "response": "No conversation to summarize.",
            "is_summary": False,
            "conversation": []
        }

@app.post("/process-audio")
async def process_audio(audio: UploadFile = File(...)):
    global conversation_state

    if conversation_state["iteration"] < conversation_state["max_iterations"]:
        # Step 1: Save uploaded (probably webm/ogg) to temp
        with tempfile.NamedTemporaryFile(delete=False, suffix=".webm") as temp_orig:
            temp_orig.write(await audio.read())
            temp_orig_path = temp_orig.name

        # Step 2: Convert to WAV using pydub
        temp_wav_path = temp_orig_path.replace(".webm", ".wav")
        try:
            audio_segment = AudioSegment.from_file(temp_orig_path)
            audio_segment.export(temp_wav_path, format="wav")
        except Exception as e:
            print("Error converting audio:", e)
            return {"error": "Invalid audio format."}

        # Step 3: Denoise
        cleaned_path = temp_wav_path.replace(".wav", "_cleaned.wav")
        try:
            y, sr = sf.read(temp_wav_path)
            noise_sample = y[:int(sr * 0.5)]
            reduced_noise = nr.reduce_noise(
                y=y,
                sr=sr,
                y_noise=noise_sample,
                prop_decrease=0.7,
                stationary=False,
            )
            sf.write(cleaned_path, reduced_noise, sr)
        except Exception as e:
            print("Noise reduction failed, using original audio:", e)
            cleaned_path = temp_wav_path  # fallback

        # Step 4: Whisper transcription
        user_input = await asyncio.to_thread(listen_to_user_whisper, cleaned_path)

        # Step 5: Bot logic
        bot_response = await ask(user_input, conversation_state["conversation"])
        conversation_state["conversation"].append({"role": "user", "content": user_input})
        conversation_state["conversation"].append({"role": "assistant", "content": bot_response})
        conversation_state["iteration"] += 1

        # Step 6: Cleanup
        for f in [temp_orig_path, temp_wav_path, cleaned_path]:
            try:
                if os.path.exists(f):
                    os.remove(f)
            except:
                pass

        return {
            "user_input": user_input,
            "response": bot_response,
            "iteration": conversation_state["iteration"],
            "is_summary": False,
            "conversation": conversation_state["conversation"]
        }

    return {
        "user_input": None,
        "response": "Max iterations reached.",
        "iteration": conversation_state["iteration"],
        "is_summary": True,
        "conversation": conversation_state["conversation"]
    }


@app.post("/text-to-speech")
async def text_to_speech(text: Dict):
    try:
        audio_buffer = io.BytesIO()
        await asyncio.to_thread(speak, text["text"], audio_buffer)
        audio_buffer.seek(0)
        return StreamingResponse(
            audio_buffer,
            media_type="audio/wav",
            headers={"Content-Disposition": "attachment; filename=response.wav"}
        )
    except Exception as e:
        print("Error in text-to-speech:", e)
        return {"error": "Failed to generate speech"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)