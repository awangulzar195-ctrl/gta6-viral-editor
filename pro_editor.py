import os, random, subprocess
from pathlib import Path
from PIL import Image, ImageDraw
from faster_whisper import WhisperModel

INPUT_DIR = Path("input_clips")
OUTPUT_DIR = Path("edited_reels")
PHONK_DIR = Path("assets/phonk")
SFX_DIR = Path("assets/sfx")
STICKER_DIR = Path("assets/stickers")
OUTPUT_DIR.mkdir(exist_ok=True)

HOOKS = [
    ("WAIT FOR THE ENDING 💀", "#FF1E1E", "#FFFFFF"),
    ("GTA 6 PHYSICS ARE UNREAL 🔥", "#FFD600", "#000000"),
    ("BRO BROKE THE MATRIX 😱", "#00E5FF", "#000000"),
    ("99% MISSED THIS DETAIL 👀", "#FF6D00", "#FFFFFF"),
]

def prepare_assets():
    if not list(PHONK_DIR.glob("*.mp3")) and not list(PHONK_DIR.glob("*.wav")):
        subprocess.run([
            "ffmpeg", "-f", "lavfi", "-i",
            "aevalsrc='0.4*sin(2*PI*55*t)*exp(-4*mod(t,0.5))+0.3*sin(2*PI*587.33*t)*exp(-14*mod(t,0.25))+0.18*(random(0)*2-1)*exp(-25*mod(t,0.25))':s=44100:d=60",
            str(PHONK_DIR / "phonk_808.wav"), "-y"
        ], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

    if not list(SFX_DIR.glob("*.mp3")) and not list(SFX_DIR.glob("*.wav")):
        subprocess.run([
            "ffmpeg", "-f", "lavfi", "-i",
            "aevalsrc='0.85*sin(2*PI*(140-95*t)*t)*exp(-2.8*t)+0.35*(random(0)*2-1)*exp(-9*t)':s=44100:d=1.2",
            str(SFX_DIR / "bass_boom.wav"), "-y"
        ], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

    badges = [("sticker_fire.png", "INSANE 🔥", "#FF2A2A"), ("sticker_skull.png", "NO WAY 💀", "#111111"), ("sticker_omg.png", "WHAT?! 😱", "#FF9100")]
    for fname, label, bg_hex in badges:
        p = STICKER_DIR / fname
        if not p.exists():
            img = Image.new("RGBA", (420, 130), (0, 0, 0, 0))
            draw = ImageDraw.Draw(img)
            draw.rounded_rectangle([5, 5, 415, 125], radius=30, fill=bg_hex, outline="#FFFFFF", width=6)
            draw.text((55, 42), label, fill="#FFFFFF")
            img.save(p)

def build_pop_ass(video_path, ass_path):
    model = WhisperModel("tiny", device="cpu", compute_type="int8")
    segments, _ = model.transcribe(str(video_path), word_timestamps=True)
    header = """[Script Info]
ScriptType: v4.00+
PlayResX: 1080
PlayResY: 1920

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: Pop,DejaVu Sans,88,&H00FFFFFF,&H0000FFFF,&H00000000,&H80000000,-1,0,0,0,100,100,0,0,1,6,3,2,40,40,430,1

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
            lines.append(f"Dialogue: 0,{fmt_time(w.start)},{fmt_time(w.end)},Pop,,0,0,0,,{{\\c{col}\\fscx125\\fscy125\\t(0,80,\\fscx100\\fscy100)}}{word}")
    ass_path.write_text("\n".join(lines), encoding="utf-8")
    return len(lines) > 1

def render_video(clip: Path):
    hook_text, box_color, text_color = random.choice(HOOKS)
    bgm = random.choice(list(PHONK_DIR.glob("*.*")))
    sfx = random.choice(list(SFX_DIR.glob("*.*")))
    sticker = random.choice(list(STICKER_DIR.glob("*.png")))
    style_mode = random.choice(["beat_zoom", "shake_drop", "flash_hdr"])
    ass_file = Path("temp_subs.ass")
    has_subs = build_pop_ass(clip, ass_file)
    out_file = OUTPUT_DIR / f"{clip.stem}_VIRAL_{style_mode.upper()}.mp4"

    if style_mode == "beat_zoom":
        fg_motion = "scale=w='if(lt(mod(t,3.0),0.25),1260,1080)':h=-2:eval=frame,eq=contrast=1.2:brightness=0.06:saturation=1.4"
    elif style_mode == "shake_drop":
        fg_motion = "scale=1180:-2,crop=1080:ih:'50+40*sin(t*18)*lt(mod(t,3.5),0.35)':'20*cos(t*18)*lt(mod(t,3.5),0.35)',eq=contrast=1.22:brightness=0.07:saturation=1.45"
    else:
        fg_motion = "scale=1080:-2,geq=r='if(lt(mod(t,4.0),0.12),min(255,r(X,Y)+95),r(X,Y))':g='if(lt(mod(t,4.0),0.12),min(255,g(X,Y)+95),g(X,Y))':b='if(lt(mod(t,4.0),0.12),min(255,b(X,Y)+95),b(X,Y))',eq=contrast=1.25:brightness=0.08:saturation=1.5"

    fc = (
        f"[0:v]scale=360:640:force_original_aspect_ratio=increase,crop=360:640,boxblur=14:4,scale=1080:1920,eq=brightness=-0.15[bg];"
        f"[0:v]{fg_motion},unsharp=5:5:1.1[fg];"
        f"[bg][fg]overlay=(W-w)/2:(H-h)/2[base];"
        f"[3:v]scale=340:-1[stk];"
        f"[base][stk]overlay=x='W-w-40':y='520+15*sin(t*6)':enable='between(t,1.5,4.5)+between(t,8.0,11.0)'[with_stk];"
        f"[with_stk]drawtext=text='{hook_text}':fontcolor={text_color}:fontsize=50:box=1:boxcolor={box_color}@0.95:boxborderw=20:x=(w-text_w)/2:y=270"
    )
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
        "ffmpeg", "-i", str(clip), "-i", str(bgm), "-i", str(sfx), "-i", str(sticker),
        "-filter_complex", fc, "-map", "[out_v]", "-map", "[out_a]",
        "-c:v", "libx264", "-preset", "veryfast", "-crf", "21",
        "-c:a", "aac", "-b:a", "192k", "-shortest", str(out_file), "-y"
    ], check=True)
    if ass_file.exists(): ass_file.unlink()

prepare_assets()
for video in INPUT_DIR.glob("*.mp4"):
    render_video(video)
