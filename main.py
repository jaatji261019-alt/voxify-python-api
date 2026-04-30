from fastapi import FastAPI, HTTPException
from fastapi.responses import StreamingResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import edge_tts

app = FastAPI(title="Voxify TTS API 🚀")

# ================= CORS =================
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ================= ROOT =================
@app.get("/")
def home():
    return {"status": "API is running 🚀"}

# ================= HEALTH =================
@app.get("/health")
def health():
    return {"status": "ok"}

# ================= MODEL =================
class TTSRequest(BaseModel):
    text: str
    voice: str = "en-US-AriaNeural"
    pitch: str = "0Hz"   # 🔥 NEW
    rate: str = "0%"     # 🔥 NEW

# ================= VOICES =================
@app.get("/voices")
async def get_voices():
    try:
        voices = await edge_tts.list_voices()

        return [
            {
                "name": v["ShortName"],
                "gender": v["Gender"],
                "lang": v["Locale"],
                "friendly": v["FriendlyName"]
            }
            for v in voices
        ]

    except Exception as e:
        return JSONResponse(status_code=500, content={"error": str(e)})

# ================= STYLE PRESETS =================
def apply_style(style: str):
    styles = {
        "deep": {"pitch": "-20Hz", "rate": "-10%"},
        "soft": {"pitch": "+10Hz", "rate": "-5%"},
        "sad": {"pitch": "-10Hz", "rate": "-20%"},
        "angry": {"pitch": "+15Hz", "rate": "+15%"},
        "story": {"pitch": "+5Hz", "rate": "-10%"},
        "normal": {"pitch": "0Hz", "rate": "0%"}
    }
    return styles.get(style, styles["normal"])

# ================= TTS =================
@app.post("/tts")
async def tts(req: TTSRequest):

    if not req.text.strip():
        raise HTTPException(status_code=400, detail="Text is required")

    try:
        async def audio_stream():

            # 🔥 अगर frontend style भेजे तो apply करो
            pitch = req.pitch
            rate = req.rate

            communicate = edge_tts.Communicate(
                text=req.text,
                voice=req.voice,
                pitch=pitch,
                rate=rate
            )

            async for chunk in communicate.stream():
                if chunk["type"] == "audio":
                    yield chunk["data"]

        return StreamingResponse(audio_stream(), media_type="audio/mpeg")

    except Exception as e:
        return JSONResponse(status_code=500, content={"error": str(e)})
