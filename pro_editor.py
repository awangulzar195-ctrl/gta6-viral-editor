import os, random, subprocess, urllib.request
from pathlib import Path
from faster_whisper import WhisperModel

INPUT_DIR = Path("input_clips")
OUTPUT_DIR = Path("edited_reels")
CACHE_DIR = Path("auto_assets")
for d in [OUTPUT_DIR, CACHE_DIR]:
    d.mkdir(exist_ok=True)

HOOKS = [
    ("WAIT FOR THE CLIMAX", "#FF1E1E", "#FFFFFF"),
    ("GTA 6 PHYSICS ARE UNREAL", "#FFD600", "#000000"),
    ("BRO BROKE THE MATRIX", "#00E5FF", "#000000"),
    ("99% MISSED THIS DETAIL", "#FF6D00", "#FFFFFF"),
    ("NO WAY THIS HAPPENED", "#FF0055", "#FFFFFF")
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

def has_audio_stream(video_path: Path) -> bool:
    res = subprocess.run(
        ["ffprobe", "-v", "error", "-select_streams", "a", "-show_entries", "stream=codec_type", "-of", "csv=p=0", str(video_path)],
        capture_output=True, text=True
    )
    return bool(res.stdout.strip())

def get_duration(video_path: Path) -> float:
    res = subprocess.run(
        ["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "default=noprint_wrappers=1:nokey=1", str(video_path)],
        capture_output=True, text=True
    )
    try:
        return float(res.stdout.strip())
    except Exception:
        return 10.0

def fetch_online_assets():
    bgm_file = CACHE_DIR / "auto_phonk.mp3"
    query = random.choice(PHONK_QUERIES)
    subprocess.run([
        "yt-dlp", "-x", "--audio-format", "mp3", "--audio-quality", "5",
        "--max-filesize", "10M", "-o", str(bgm_file), query
    ], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

    if not bgm_file.exists():
        bgm_file = CACHE_DIR / "fallback_phonk.wav"
        subprocess.run([
            "ffmpeg", "-f", "lavfi", "-i",
            "aevalsrc='0.45*sin(2*PI*55*t)*exp(-4*mod(t,0.5))+0.3*sin(2*PI*587.33*t)*exp(-14*mod(t,0.25))+0.15*(random(0)*2-1)*exp(-22*mod(t,0.25))':s=44100:d=60",
            str(bgm_file), "-y"
        ], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

    sfx_file = CACHE_DIR / "impact_sfx.wav"
    subprocess.run([
        "ffmpeg", "-f", "lavfi", "-i",
        "aevalsrc='0.9*sin(2*PI*(160-110*t)*t)*exp(-2.8*t)+0.4*(random(0)*2-1)*exp(-8*t)':s=44100:d=1.2",
        str(sfx_file), "-y"
    ], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

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

def build_pop_ass(video_path: Path, ass_path: Path, has_audio: bool) -> bool:
    if not has_audio:
        return False
    try:
        model = WhisperModel("tiny", device="cpu", compute_type="int8")
        segments, _ = model.transcribe(str(video_path), word_timestamps=True)
        header = """[Script Info]
ScriptType: v4.00+
PlayResX: 1080
PlayResY: 1920

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: Pop,DejaVu Sans,92,&H00FFFFFF,&H0000FFFF,&H00000000,&H80000000,-1,0,0,0,100,100,0,0,1,7,3,2,40,40,420,1

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
        if len(lines) > 1:
            ass_path.write_text("\n".join(lines), encoding="utf-8")
            return True
    except Exception:
        pass
    return False

def render_video(clip: Path, bgm: Path, sfx: Path, stickers: list):
    hook_text, box_color, text_color = random.choice(HOOKS)
    visual_hook_type = random.choice(["climax_teaser", "rgb_punch_zoom", "flash_shake_intro"])
    has_audio = has_audio_stream(clip)
    dur = get_duration(clip)
    ass_file = Path("temp_subs.ass")
    has_subs = build_pop_ass(clip, ass_file, has_audio)
    out_file = OUTPUT_DIR / f"{clip.stem}_VIRAL.mp4"

    # Visual Hook + Dynamic Motion Engine
    if visual_hook_type == "rgb_punch_zoom":
        # Opening 2.5s rapid punch-in + RGB split + beat zoom
        fg_motion = (
            "scale=w='if(lt(t,2.2),1320-100*t,if(lt(mod(t,3.0),0.25),1240,1080))':h=-2:eval=frame,"
            "rgbashift=rh='if(lt(t,2.0),14*sin(t*25),0)':bh='if(lt(t,2.0),-14*sin(t*25),0)',"
            "eq=contrast=1.22:brightness=0.06:saturation=1.45"
        )
    elif visual_hook_type == "flash_shake_intro":
        # Opening white flash + violent camera shake + beat drops
        fg_motion = (
            "scale=1200:-2,"
            "crop=1080:ih:'60+45*sin(t*24)*if(lt(t,2.0),1,lt(mod(t,3.5),0.3))':'25*cos(t*24)*if(lt(t,2.0),1,lt(mod(t,3.5),0.3))',"
            "geq=r='if(lt(t,0.18)+lt(mod(t,4.0),0.1),min(255,r(X,Y)+110),r(X,Y))':g='if(lt(t,0.18)+lt(mod(t,4.0),0.1),min(255,g(X,Y)+110),g(X,Y))':b='if(lt(t,0.18)+lt(mod(t,4.0),0.1),min(255,b(X,Y)+110),b(X,Y))',"
            "eq=contrast=1.24:brightness=0.07:saturation=1.45"
        )
    else:
        # Climax Teaser Hook: Flash-forwards ending 1.5s at the very start (0-1.5s) with zoom + border
        fg_motion = (
            "scale=w='if(lt(t,1.5),1280,if(lt(mod(t,3.0),0.25),1240,1080))':h=-2:eval=frame,"
            "eq=contrast=1.25:brightness=0.08:saturation=1.5"
        )

    inputs = ["-i", str(clip), "-i", str(bgm), "-i", str(sfx)]
    fc = (
        f"[0:v]scale=360:640:force_original_aspect_ratio=increase,crop=360:640,boxblur=14:4,scale=1080:1920,eq=brightness=-0.16[bg];"
        f"[0:v]{fg_motion},unsharp=5:5:1.1[fg];"
        f"[bg][fg]overlay=(W-w)/2:(H-h)/2[base];"
    )

    # Visual Hook: Top Neon Retention Progress Bar
    fc += f"[base]drawbox=x=0:y=0:w='W*(t/{max(dur,1.0)})':h=16:color=#00FF88@0.95:t=fill[bar_v];"

    # Visual Hook: Climax Flash-Forward Overlay (0.0s to 1.4s) if video > 5s
    if visual_hook_type == "climax_teaser" and dur > 5.0:
        teaser_start = max(0.0, dur - 2.0)
        fc += (
            f"[0:v]trim=start={teaser_start}:duration=1.4,setpts=PTS-STARTPTS,scale=920:-2,"
            f"pad=944:ih+24:12:12:color=#FF1E1E,rgbashift=rh=8:bh=-8[teaser];"
            f"[bar_v][teaser]overlay=(W-w)/2:(H-h)/2:enable='lt(t,1.4)'[hook_v];"
        )
    else:
        fc += "[bar_v]copy[hook_v];"

    if stickers:
        stk = random.choice(stickers)
        inputs += ["-i", str(stk)]
        fc += (
            f"[3:v]scale=220:220[stk];"
            f"[hook_v][stk]overlay=x='W-w-50':y='500+22*sin(t*7)':enable='between(t,0.5,3.5)+between(t,6.5,10.0)'[v_pre];"
        )
    else:
        fc += "[hook_v]copy[v_pre];"

    # Text Hook Banner (Top)
    fc += f"[v_pre]drawtext=text='{hook_text}':fontcolor={text_color}:fontsize=52:box=1:boxcolor={box_color}@0.95:boxborderw=22:x=(w-text_w)/2:y=250"
    if has_subs:
        fc += f",ass={ass_file}"
    fc += "[out_v];"

    # Crash-Proof Audio Mixing (Works even if clip has NO microphone/game audio!)
    if has_audio:
        fc += (
            "[0:a]volume=1.35,bass=g=5[voice];"
            "[1:a]aloop=loop=-1:size=2e+09,volume=0.38,bass=g=7[bgm];"
            "[bgm][voice]sidechaincompress=threshold=0.03:ratio=6:attack=50:release=400[ducked_bgm];"
            "[2:a]volume=0.95[sfx];"
            "[voice][ducked_bgm][sfx]amix=inputs=3:duration=first:dropout_transition=2[out_a]"
        )
    else:
        fc += (
            "[1:a]aloop=loop=-1:size=2e+09,volume=0.75,bass=g=8[bgm];"
            "[2:a]volume=0.95[sfx];"
            "[bgm][sfx]amix=inputs=2:duration=first:dropout_transition=2[out_a]"
        )

    subprocess.run([
        "ffmpeg", *inputs, "-filter_complex", fc,
        "-map", "[out_v]", "-map", "[out_a]",
        "-c:v", "libx264", "-preset", "veryfast", "-crf", "21",
        "-c:a", "aac", "-b:a", "192k", "-shortest", str(out_file), "-y"
    ], check=True)
    if ass_file.exists(): ass_file.unlink()

bgm, sfx, stickers = fetch_online_assets()
clips = sorted(INPUT_DIR.glob("*.mp4"), key=lambda p: p.stat().st_mtime, reverse=True)
if clips:
    render_video(clips[0], bgm, sfx, stickers)
