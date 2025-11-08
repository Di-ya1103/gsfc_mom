# backend/nlp.py
from typing import List, Dict
import nltk
from nltk.tokenize import sent_tokenize
from transformers import pipeline
import math

nltk.download('punkt', quiet=True)

# Summarizer pipeline (lightweight). We enable truncation safety.
# Using sshleifer/distilbart-cnn-12-6 (small) as before for speed.
summarizer = pipeline(
    "summarization",
    model="sshleifer/distilbart-cnn-12-6",
    truncation=True
)

def chunk_sentences(text: str, max_chars: int = 900) -> List[str]:
    """
    Split text into chunks composed of whole sentences.
    max_chars is conservative to avoid exceeding token limits.
    """
    if not text:
        return []
    sents = sent_tokenize(text)
    chunks = []
    cur = ""
    for s in sents:
        # if adding this sentence would exceed max_chars, flush current
        if cur and (len(cur) + len(s) + 1) > max_chars:
            chunks.append(cur.strip())
            cur = s
        else:
            cur = (cur + " " + s).strip()
    if cur:
        chunks.append(cur.strip())
    return chunks

def safe_summarize(text: str, max_length: int = 120, min_length: int = 20) -> str:
    """
    Summarize safely with fallbacks:
      1) try full text
      2) if fails, trim to first N chars and retry
      3) if still fails, return a short fallback string
    """
    if not text or text.isspace():
        return ""
    try:
        out = summarizer(text, max_length=max_length, min_length=min_length, truncation=True, do_sample=False)
        return out[0]['summary_text']
    except Exception as e:
        # fallback: shorten and retry
        try:
            short = text[:800]
            out = summarizer(short, max_length=max_length, min_length=min_length, truncation=True, do_sample=False)
            return out[0]['summary_text']
        except Exception as e2:
            # last resort: return first 1-2 sentences as "summary"
            sents = sent_tokenize(text)
            return " ".join(sents[:2]) if sents else text[:200]

def generate_mom_content(text: str, segments: List[Dict], metadata: Dict) -> Dict:
    """
    Returns structured MoM content:
      - meeting_objective (from metadata)
      - summary (safe concatenated summary)
      - action_items (heuristic extraction)
      - detailed_minutes (mirrors incoming segments)
    Designed to work with both full transcripts and small incremental (live) transcripts.
    """
    # Defensive defaults
    if text is None:
        text = ""

    # 1) Chunk by sentences (safe size)
    chunks = chunk_sentences(text, max_chars=900)  # conservative size

    # 2) Summarize chunk-by-chunk, then combine
    summaries = []
    for c in chunks:
        s = safe_summarize(c, max_length=120, min_length=20)
        if s:
            summaries.append(s)
    overall_summary = " ".join(summaries).strip()
    if not overall_summary and text:
        # fallback: short raw text if summarizer couldn't run
        overall_summary = " ".join(sent_tokenize(text)[:3])

    # 3) Extract action items with heuristics
    action_items = []
    for sent in sent_tokenize(text):
        lower = sent.lower()
        if any(k in lower for k in [
            "action", "target date", "due", "deadline", "assign", "responsible",
            "will do", "to do", "task", "deliver", "deliverable", "complete by"
        ]):
            action_items.append(sent)

    # fallback to top sentences from summary if none found
    if not action_items:
        action_items = sent_tokenize(overall_summary)[:3]

    # 4) Build detailed minutes from segments (keep existing shape)
    detailed_minutes = []
    for s in segments or []:
        detailed_minutes.append({
            "start": s.get("start"),
            "end": s.get("end"),
            "text": s.get("text", ""),
            "speaker": s.get("speaker", None)
        })

    mom = {
        "meeting_objective": metadata.get("meeting_objective", ""),
        "summary": overall_summary,
        "action_items": action_items,
        "detailed_minutes": detailed_minutes
    }
    return mom

def generate_person_summaries(text: str, segments: List[Dict]) -> Dict:
    """
    Create per-speaker summaries.
    - If segments already contain speaker labels, group by them.
    - Otherwise, fallback to alternating assignment (keeps previous behavior).
    - Each speaker's text is chunked and summarized safely.
    """
    speakers = {}
    # group text under speaker labels if present
    for seg in segments or []:
        sp = seg.get("speaker")
        seg_text = seg.get("text", "")
        if sp:
            speakers.setdefault(sp, []).append(seg_text)

    # fallback: alternate assignment if no speaker labels
    if not speakers:
        for i, seg in enumerate(segments or []):
            sp = f"Person{(i % 2) + 1}"
            speakers.setdefault(sp, []).append(seg.get("text", ""))

    # summarize each speaker's joined text
    person_summaries = {}
    for sp, texts in speakers.items():
        joined = " ".join(texts).strip()
        if not joined:
            person_summaries[sp] = ""
            continue
        # chunk by sentences
        chunks = chunk_sentences(joined, max_chars=800)
        out_summ = []
        for c in chunks:
            s = safe_summarize(c, max_length=80, min_length=12)
            if s:
                out_summ.append(s)
        person_summaries[sp] = " ".join(out_summ).strip() or "No summary available."
    return person_summaries
