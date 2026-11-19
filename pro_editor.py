import os, random, subprocess, urllib.request
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont
from faster_whisper import WhisperModel

INPUT_DIR = Path("input_clips")
OUTPUT_DIR = Path("edited_reels")
CACHE_DIR = Path("auto_assets")
for d in [OUTPUT_DIR, CACHE_DIR]:
    d.mkdir(exist_ok=True)

HOOKS = [
    ("WAIT FOR THE ENDING 💀", "#FF1E1E", "#FFFFFF"),
    ("GTA 6 PHYSICS ARE UNREAL 🔥", "#FFD600", "#000000"),
    ("BRO BROKE THE MATRIX 😱", "#00E5FF", "#000000"),
    ("99% MISSED THIS DETAIL 👀", "#FF6D00", "#FFFFFF"),
    ("NO WAY THIS HAPPENED 🤯", "#FF0055", "#FFFFFF")
]

PHONK_QUERIES = [
    "ytsearch1:aggressive phonk drift no copyright 1 minute",
    "ytsearch1:brazilian phonk bass boosted no copyright",
    "ytsearch1:memphis phonk instrumental loop no copyright",
    "ytsearch1:sigma phonk beat no copyright"
]

EMOJI_URLS = [
    ("fire.png", "https://cdnjs.cloudflare.com/ajax/libs/twemoji/14.0.2/72x72/1f525.png"),
    ("skull.png", "https://cdnjs.cloudflare.com/ajax/libs/twemoji/14.0.2/72x72/1f480.png"),
    ("shock.png", "https://cdnjs.cloudflare.com/ajax/libs/twemoji/14.0.2/72x72/1f631.png"),
    ("eyes.png", "https://cdnjs.cloudflare.com/ajax/libs/twemoji/14.0.2/72x72/1f440.png"),
]

def fetch_online_assets():
    # 1. Auto-fetch real Phonk BGM from YouTube via yt-dlp
    bgm_file = CACHE_DIR / "auto_phonk.mp3"
    query = random.choice(PHONK_QUERIES)
    subprocess.run([
        "yt-dlp", "-x", "--audio-format", "mp3", "--audio-quality", "5",
        "--max-filesize", "10M", "-o", str(bgm_file), query
    ], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

    # Fallback synthesized phonk if yt-dlp blocked
    if not bgm_file.exists():
        bgm_file = CACHE_DIR / "fallback_phonk.wav"
        subprocess.run([
            "ffmpeg", "-f", "lavfi", "-i",
            "aevalsrc='0.4*sin(2*PI*55*t)*exp(-4*mod(t,0.5))+0.3*sin(2*PI*587.33*t)*exp(-14*mod(t,0.25))':s=44100:d=60",
            str(bgm_file), "-y"
        ], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

    # 2. Generate crisp Whoosh + Sub-Bass Drop SFX
    sfx_file = CACHE_DIR / "impact_sfx.wav"
    subprocess.run([
        "ffmpeg", "-f", "lavfi", "-i",
        "aevalsrc='0.85*sin(2*PI*(150-100*t)*t)*exp(-2.8*t)+0.35*(random(0)*2-1)*exp(-8*t)':s=44100:d=1.2",
        str(sfx_file), "-y"
    ], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

    # 3. Auto-download HD Emoji PNG Stickers
    stickers = []
    for name, url in EMOJI_URLS:
        p = CACHE_DIR / name
        try:
            if not p.exists():
                urllib.request.urlretrieve(url, p)
            if p.exists():
                stickers.append(p)
        except Exception:
            pass
    return bgm_file, sfx_file, stickers

def build_pop_ass(video_path, ass_path):
    model = WhisperModel("tiny", device="cpu", compute_type="int8")
    segments, _ = model.transcribe(str(video_path), word_timestamps=True)
    header = """[Script Info]
ScriptType: v4.00+
PlayResX: 1080
PlayResY: 1920

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: Pop,DejaVu Sans,90,&H00FFFFFF,&H0000FFFF,&H00000000,&H80000000,-1,0,0,0,100,100,0,0,1,7,3,2,40,40,420,1

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
"""
    colors = ["&H0000FFFF", "&H0000FF66", "&H00FFFFFF", "&H0000D4FF"]
    lines = [header]
    def fmt_time(sec):
        return f"{int(sec//3600)}:{int((sec%3600)//60):02d}:{sec%60:05.2f}"
    for seg in segments:
        if not seg.words: continue
        for w in seg.words:
            word = w.word.strip().upper()
            if not word: continue
            col = random.choice(colors)
            lines.append(f"Dialogue: 0,{fmt_time(w.start)},{fmt_time(w.end)},Pop,,0,0,0,,{{\\c{col}\\fscx130\\fscy130\\t(0,80,\\fscx100\\fscy100)}}{word}")
    ass_path.write_text("\n".join(lines), encoding="utf-8")
    return len(lines) > 1

def render_video(clip: Path, bgm: Path, sfx: Path, stickers: list):
    hook_text, box_color, text_color = random.choice(HOOKS)
    style_mode = random.choice(["beat_zoom", "shake_drop", "flash_hdr"])
    ass_file = Path("temp_subs.ass")
    has_subs = build_pop_ass(clip, ass_file)
    out_file = OUTPUT_DIR / f"{clip.stem}_VIRAL.mp4"

    if style_mode == "beat_zoom":
        fg_motion = "scale=w='if(lt(mod(t,3.0),0.25),1260,1080)':h=-2:eval=frame,eq=contrast=1.22:brightness=0.06:saturation=1.45"
    elif style_mode == "shake_drop":
        fg_motion = "scale=1180:-2,crop=1080:ih:'50+40*sin(t*18)*lt(mod(t,3.5),0.35)':'20*cos(t*18)*lt(mod(t,3.5),0.35)',eq=contrast=1.24:brightness=0.07:saturation=1.45"
    else:
        fg_motion = "scale=1080:-2,geq=r='if(lt(mod(t,4.0),0.12),min(255,r(X,Y)+95),r(X,Y))':g='if(lt(mod(t,4.0),0.12),min(255,g(X,Y)+95),g(X,Y))':b='if(lt(mod(t,4.0),0.12),min(255,b(X,Y)+95),b(X,Y))',eq=contrast=1.25:brightness=0.08:saturation=1.5"

    inputs = ["-i", str(clip), "-i", str(bgm), "-i", str(sfx)]
    fc = (
        f"[0:v]scale=360:640:force_original_aspect_ratio=increase,crop=360:640,boxblur=14:4,scale=1080:1920,eq=brightness=-0.15[bg];"
        f"[0:v]{fg_motion},unsharp=5:5:1.1[fg];"
        f"[bg][fg]overlay=(W-w)/2:(H-h)/2[base];"
    )
    if stickers:
        stk = random.choice(stickers)
        inputs += ["-i", str(stk)]
        fc += (
            f"[3:v]scale=220:220[stk];"
            f"[base][stk]overlay=x='W-w-50':y='520+20*sin(t*7)':enable='between(t,1.2,4.5)+between(t,7.5,11.0)'[v_pre];"
        )
    else:
        fc += "[base]copy[v_pre];"

    fc += f"[v_pre]drawtext=text='{hook_text}':fontcolor={text_color}:fontsize=50:box=1:boxcolor={box_color}@0.95:boxborderw=20:x=(w-text_w)/2:y=270"
    if has_subs:
        fc += f",ass={ass_file}"
    fc += "[out_v];"
    fc += (
        "[0:a]volume=1.35,bass=g=5[voice];"
        "[1:a]aloop=loop=-1:size=2e+09,volume=0.35,bass=g=7[bgm];"
        "[bgm][voice]sidechaincompress=threshold=0.03:ratio=6:attack=50:release=400[ducked_bgm];"
        "[2:a]volume=0.9[sfx];"
        "[voice][ducked_bgm][sfx]amix=inputs=3:duration=first:dropout_transition=2[out_a]"
    )

    subprocess.run([
        "ffmpeg", *inputs, "-filter_complex", fc,
        "-map", "[out_v]", "-map", "[out_a]",
        "-c:v", "libx264", "-preset", "veryfast", "-crf", "21",
        "-c:a", "aac", "-b:a", "192k", "-shortest", str(out_file), "-y"
    ], check=True)
    if ass_file.exists(): ass_file.unlink()

bgm, sfx, stickers = fetch_online_assets()
for video in INPUT_DIR.glob("*.mp4"):
    render_video(video, bgm, sfx, stickers)
