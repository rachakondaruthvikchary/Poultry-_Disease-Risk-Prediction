from fastapi import APIRouter, Query, HTTPException
from fastapi.responses import StreamingResponse
import io

from gtts import gTTS

router = APIRouter()


@router.get("/")
def tts(text: str = Query(..., min_length=1), lang: str = Query("hi")):
    try:
        # gTTS supports many languages; we pass through the requested lang
        tts_obj = gTTS(text=text, lang=lang)
        buf = io.BytesIO()
        tts_obj.write_to_fp(buf)
        buf.seek(0)
        return StreamingResponse(buf, media_type="audio/mpeg")
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))
