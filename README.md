# Bot-f 🤖

A conversational AI bot with audio processing capabilities, built with FastAPI, Ollama, and Whisper.

## Features ✨

- **Voice-to-Text**: Convert user audio input to text using Whisper
- **AI Conversations**: Powered by Ollama for intelligent responses
- **Text-to-Speech**: Convert bot responses back to audio
- **Noise Reduction**: Audio preprocessing for better transcription quality
- **Conversation Management**: Track conversation state and generate summaries
- **RESTful API**: FastAPI backend with CORS support

## Tech Stack 🛠️

- **Backend**: FastAPI (Python)
- **AI Model**: Ollama
- **Speech Recognition**: Whisper
- **Text-to-Speech**: Custom TTS implementation
- **Audio Processing**: Pydub, SoundFile, Noisereduce
- **Server**: Uvicorn

## Prerequisites 📋

- Python 3.8+
- Ollama installed and running locally
- A custom model named 'bot' in Ollama

## Installation 🚀

1. **Clone the repository**

   ```bash
   git clone https://github.com/Midhun-gg/Bot-f.git
   cd Bot-f
   ```

2. **Install Python dependencies**

   ```bash
   pip install -r requirements.txt
   ```

3. **Install and setup Ollama**

   - Visit [Ollama.ai](https://ollama.ai) for installation instructions
   - Create a custom model named 'bot' or modify the model name in `app.py`

4. **Run the application**
   ```bash
   python app.py
   ```

The server will start on `http://localhost:8000`

## API Endpoints 📡

### `POST /initial-greeting`

- Generates an initial greeting from the bot
- Returns a concise greeting message

### `POST /process-audio`

- Accepts audio file upload (webm/ogg format)
- Processes audio through noise reduction
- Transcribes to text using Whisper
- Generates AI response
- Returns conversation data

### `POST /text-to-speech`

- Accepts text input
- Converts text to speech
- Returns audio file (WAV format)

### `POST /final-greeting`

- Generates a closing message
- Thanks the user and ends conversation

### `POST /summary-generation`

- Generates a summary of the conversation
- Resets conversation state

## Usage Examples 💡

### Starting a Conversation

```bash
curl -X POST http://localhost:8000/initial-greeting
```

### Processing Audio

```bash
curl -X POST http://localhost:8000/process-audio \
  -F "audio=@your_audio_file.webm"
```

### Text to Speech

```bash
curl -X POST http://localhost:8000/text-to-speech \
  -H "Content-Type: application/json" \
  -d '{"text": "Hello, how are you?"}'
```

## Project Structure 📁

```
Bot-f/
├── app.py              # Main FastAPI application
├── s2t.py              # Speech-to-text functionality
├── t2s.py              # Text-to-speech functionality
├── Modelfile            # Ollama model configuration
├── requirements.txt     # Python dependencies
├── audio_files/        # Audio file storage
└── README.md           # This file
```

## Configuration ⚙️

### Conversation Settings

- **Max Iterations**: 5 (configurable in `conversation_state`)
- **Response Length**: Limited to 20 words for concise interactions
- **Audio Formats**: Supports webm, ogg, and converts to WAV

### Audio Processing

- **Noise Reduction**: 70% noise reduction with stationary=False
- **Sample Rate**: Preserves original audio sample rate
- **Temporary Files**: Automatically cleaned up after processing

## Development 🧪

### Running in Development Mode

```bash
uvicorn app:app --reload --host 0.0.0.0 --port 8000
```

### Testing

The API can be tested using tools like:

- Postman
- Insomnia
- curl commands
- Frontend applications

## Troubleshooting 🔧

### Common Issues

1. **Ollama Connection Error**

   - Ensure Ollama is running: `ollama serve`
   - Verify model 'bot' exists: `ollama list`

2. **Audio Processing Errors**

   - Check audio file format (webm/ogg recommended)
   - Ensure sufficient disk space for temporary files

3. **Dependencies Issues**
   - Update pip: `pip install --upgrade pip`
   - Install system audio dependencies if needed

## Contributing 🤝

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## Support 💬

For issues and questions:

- Create an issue in the repository
- Check the troubleshooting section above
- Ensure all prerequisites are met

---

**Note**: This bot is designed for concise, engaging conversations with a maximum of 5 iterations before requiring a summary or restart.
