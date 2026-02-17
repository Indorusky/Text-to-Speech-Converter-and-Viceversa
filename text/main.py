from fastapi import FastAPI
from fastapi.responses import HTMLResponse, StreamingResponse
from fastapi.middleware.cors import CORSMiddleware
from gtts import gTTS
from io import BytesIO

app = FastAPI(
    title="Real-Time Multilingual TTS-STT",
    docs_url=None,
    redoc_url=None
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# ---------------- HOME PAGE ----------------
@app.get("/", response_class=HTMLResponse)
def home():
    return """
<!DOCTYPE html>
<html>
<head>
    <title>Real-Time Speech ↔ Text</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            background: #0f172a;
            color: white;
            display: flex;
            justify-content: center;
            align-items: center;
            height: 100vh;
        }
        .box {
            background: #020617;
            padding: 30px;
            border-radius: 10px;
            width: 480px;
            text-align: center;
        }
        textarea, select {
            width: 100%;
            margin-bottom: 12px;
            padding: 10px;
            font-size: 15px;
            border-radius: 6px;
            border: none;
        }
        textarea {
            height: 140px;
            resize: none;
        }
        button {
            padding: 10px 18px;
            margin: 5px;
            font-size: 16px;
            cursor: pointer;
            border-radius: 6px;
            border: none;
        }
        .listening {
            color: #22c55e;
            font-weight: bold;
        }
    </style>
</head>
<body>
    <div class="box">
        <h2>🎙 Real-Time Speech ↔ Text</h2>

        <select id="lang">
            <option value="en-US">English</option>
            <option value="hi-IN">Hindi</option>
            <option value="te-IN">Telugu</option>
            <option value="ta-IN">Tamil</option>
            <option value="kn-IN">Kannada</option>
            <option value="ml-IN">Malayalam</option>
            <option value="bn-IN">Bengali</option>
            <option value="mr-IN">Marathi</option>
            <option value="ur-IN">Urdu</option>
            <option value="gu-IN">Gujarati</option>
            <option value="pa-IN">Punjabi</option>
            <option value="fr-FR">French</option>
            <option value="es-ES">Spanish</option>
            <option value="de-DE">German</option>
            <option value="ja-JP">Japanese</option>
        </select>

        <textarea id="text" placeholder="Your words will appear here..."></textarea>

        <button onclick="startListening()">🎧 Listen</button>
        <button onclick="stopListening()">⛔ Stop</button>
        <button onclick="speak()">🔊 Speak</button>

        <p id="status"></p>
    </div>

<script>
let recognition;
let listening = false;

function startListening() {
    if (listening) return;

    const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
    if (!SpeechRecognition) {
        alert("Your browser does not support Speech Recognition. Use Chrome or Edge.");
        return;
    }

    recognition = new SpeechRecognition();
    recognition.lang = document.getElementById("lang").value;
    recognition.continuous = true;
    recognition.interimResults = true;

    recognition.onresult = (event) => {
        let finalText = "";
        let interimText = "";

        for (let i = 0; i < event.results.length; i++) {
            if (event.results[i].isFinal) {
                finalText += event.results[i][0].transcript + " ";
            } else {
                interimText += event.results[i][0].transcript;
            }
        }

        document.getElementById("text").value = finalText + interimText;
    };

    recognition.start();
    listening = true;
    document.getElementById("status").innerHTML = "● Listening...";
    document.getElementById("status").className = "listening";
}

function stopListening() {
    if (recognition && listening) {
        recognition.stop();
        listening = false;
        document.getElementById("status").innerHTML = "Stopped";
        document.getElementById("status").className = "";
    }
}

async function speak() {
    const text = document.getElementById("text").value;
    if (!text) return;

    const lang = document.getElementById("lang").value.split("-")[0];

    const res = await fetch(`/tts?text=${encodeURIComponent(text)}&lang=${lang}`, {
        method: "POST"
    });

    const blob = await res.blob();
    new Audio(URL.createObjectURL(blob)).play();
}
</script>
</body>
</html>
"""

# ---------------- TEXT TO SPEECH (IN-MEMORY) ----------------
@app.post("/tts")
async def text_to_speech(text: str, lang: str = "en"):
    audio_buffer = BytesIO()
    gTTS(text=text, lang=lang).write_to_fp(audio_buffer)
    audio_buffer.seek(0)

    return StreamingResponse(
        audio_buffer,
        media_type="audio/mpeg"
    )
