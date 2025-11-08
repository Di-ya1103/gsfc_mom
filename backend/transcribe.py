# backend/transcribe.py
import os
import whisper
import ffmpeg
import tempfile
from pathlib import Path
from typing import Tuple, List, Dict

# Load Whisper model once at startup (fast subsequent calls)
print("Loading Whisper 'small' model... (10-60 seconds)")
model = whisper.load_model("tiny")
print("Whisper model loaded successfully!")

def convert_to_wav(input_path: str) -> str:
    """
    Convert any audio format to 16kHz mono WAV using ffmpeg.
    Returns path to temporary WAV file.
    """
    temp_wav = tempfile.NamedTemporaryFile(suffix=".wav", delete=False)
    output_path = temp_wav.name
    temp_wav.close()

    try:
        stream = ffmpeg.input(input_path)
        stream = ffmpeg.output(
            stream, output_path,
            format="wav",
            acodec="pcm_s16le",
            ac=1,
            ar="16000",
            loglevel="error"
        )
        ffmpeg.run(stream, overwrite_output=True, capture_stdout=True, capture_stderr=True)
    except ffmpeg.Error as e:
        error_msg = e.stderr.decode() if e.stderr else "Unknown ffmpeg error"
        raise RuntimeError(f"FFmpeg conversion failed: {error_msg}")
    except Exception as e:
        raise RuntimeError(f"Audio conversion failed: {str(e)}")

    return output_path


def transcribe_file(path_in: str) -> Tuple[str, List[Dict], str]:
    """
    Transcribe audio file using Whisper.
    Returns (full_text, segments, detected_language)
    """
    p = Path(path_in)
    wav_path = None
    need_cleanup = False

    try:
        # Convert to WAV if not already
        if p.suffix.lower() != ".wav":
            wav_path = convert_to_wav(path_in)
            need_cleanup = True
        else:
            wav_path = path_in

        # Transcribe
        result = model.transcribe(
            wav_path,
            language=None,
            fp16=False,  
            beam_size=5,
            best_of=5,
            temperature=0.0,
            word_timestamps=False
        )

        text = result.get("text", "").strip()
        language = result.get("language", "en")

        segments = []
        for seg in result.get("segments", []):
            segments.append({
                "start": round(seg["start"], 2),
                "end": round(seg["end"], 2),
                "text": seg["text"].strip()
            })

        return text, segments, language

    finally:
        # Always clean up temp file
        if need_cleanup and wav_path and os.path.exists(wav_path):
            try:
                os.unlink(wav_path)
            except:
                pass


# Translation 
from transformers import pipeline
_translation_pipeline_cache = {}

def get_translator(src_lang: str):
    if src_lang in _translation_pipeline_cache:
        return _translation_pipeline_cache[src_lang]

    # Best models for Indian languages
    model_map = {
        "hi": "Helsinki-NLP/opus-mt-hi-en",
        "ta": "Helsinki-NLP/opus-mt-ta-en",
        "te": "Helsinki-NLP/opus-mt-te-en",
        "bn": "Helsinki-NLP/opus-mt-bn-en",
        "mr": "Helsinki-NLP/opus-mt-mr-en",
        "gu": "Helsinki-NLP/opus-mt-gu-en",
        "pa": "Helsinki-NLP/opus-mt-pa-en",
        "ml": "Helsinki-NLP/opus-mt-ml-en",
        "kn": "Helsinki-NLP/opus-mt-kn-en",
        "ur": "Helsinki-NLP/opus-mt-ur-en",
    }

    model_name = model_map.get(src_lang, "Helsinki-NLP/opus-mt-mul-en")
    print(f"Loading translator: {src_lang} → en ({model_name})")

    translator = pipeline(
        "translation",
        model=model_name,
        device=-1,  
        max_length=512
    )
    _translation_pipeline_cache[src_lang] = translator
    return translator


def translate_text_if_needed(text: str, detected_lang: str) -> Tuple[str, bool]:
    """
    Translate non-English text to English.
    Returns (translated_text, was_translated)
    """
    if not detected_lang or detected_lang.startswith("en"):
        return text, False

    try:
        translator = get_translator(detected_lang)
        chunks = [text[i:i+4000] for i in range(0, len(text), 4000)]
        translated_chunks = []

        for chunk in chunks:
            if not chunk.strip():
                continue
            result = translator(chunk, max_length=512)
            translated_chunks.append(result[0]["translation_text"])

        return " ".join(translated_chunks), True

    except Exception as e:
        print(f"Translation failed for {detected_lang}: {e}")
        return text, False