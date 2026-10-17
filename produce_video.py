"""
MoneyPrinterTurbo 模式视频生成器
主题：7大视频制作工具横评
流程：主题词 → AI生成文案 → 生成画面帧 → edge-tts配音 → ffmpeg合成
"""
import os
import sys
import asyncio
import json
import subprocess
import tempfile
from pathlib import Path

import edge_tts
from openai import OpenAI
from PIL import Image, ImageDraw, ImageFont

# ── 配置 ──────────────────────────────────────────────
OUTPUT_DIR = Path(os.path.expandvars(r"%USERPROFILE%\Documents\trae_projects\0-1agent\video_output"))
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

VIDEO_WIDTH = 1920
VIDEO_HEIGHT = 1080
FPS = 24

# Agnes AI (兼容OpenAI格式)
client = OpenAI(
    api_key=os.environ.get("AGNES_API_KEY"),
    base_url="https://apihub.agnes-ai.com/v1",
)
MODEL = "agnes-1.5-flash"

# ── Step 1: AI生成文案 ──────────────────────────────────
def generate_script() -> list[dict]:
    """调用LLM生成视频文案，返回分镜列表"""
    prompt = """你是一个短视频文案编剧。请为一条90秒的横评视频生成文案，主题是"7大开源视频制作工具横评"。

7个工具（按两条轴分类）：
1. MoneyPrinterTurbo (91.9K星) - Agent自主+图库素材，一键生成短视频
2. OpenCut (59.3K星) - 手动剪辑+已有素材，浏览器内时间线编辑器
3. Open Generative AI (20.6K星) - 手动生成+AI生成，200+模型统一界面
4. OpenMontage (16.4K星) - Agent自主+AI生成，无GUI嵌入代码编辑器
5. ViMax (10.6K星) - Agent自主+AI生成，小说转多镜头叙事
6. Toonflow (10.4K星) - Agent自主+AI生成，小说转AI短剧
7. Palmier Pro (8.5K星) - 手动+AI混合，macOS原生剪辑器

两条轴：
- 素材来源：已有素材 vs 从零生成
- 操作方式：手动操作 vs Agent自主

请生成8个分镜（含开场和结尾），每个分镜包含：
- id: 分镜编号
- narration: 旁白文字（口语化，每段3-8秒）
- visual: 画面描述（用于生成文字卡片）
- duration: 预计时长（秒）

只返回JSON数组，不要其他内容。"""

    response = client.chat.completions.create(
        model=MODEL,
        messages=[{"role": "user", "content": prompt}],
        temperature=0.7,
    )

    content = response.choices[0].message.content.strip()
    # 清理可能的markdown代码块
    if content.startswith("```"):
        content = content.split("\n", 1)[1].rsplit("```", 1)[0].strip()

    shots = json.loads(content)

    # 标准化字段名（LLM可能返回中文key）
    key_map = {
        "id": ["id", "编号", "分镜编号", "序号"],
        "narration": ["narration", "旁白", "配音", "文案"],
        "visual": ["visual", "画面", "画面描述", "视觉"],
        "duration": ["duration", "时长", "预计时长"],
    }
    normalized = []
    for s in shots:
        ns = {}
        for target, sources in key_map.items():
            for src in sources:
                if src in s:
                    ns[target] = s[src]
                    break
            if target not in ns:
                ns[target] = 5 if target == "duration" else ""
        ns["id"] = int(ns["id"]) if ns["id"] else len(normalized) + 1
        normalized.append(ns)

    print(f"[Step 1] 文案生成完成: {len(normalized)} 个分镜")
    for s in normalized:
        print(f"  分镜{s['id']}: {s['narration'][:40]}...")
    return normalized


# ── Step 2: 生成画面帧 ──────────────────────────────────
def get_font(size: int) -> ImageFont.FreeTypeFont:
    """获取中文字体"""
    font_paths = [
        r"C:\Windows\Fonts\msyh.ttc",
        r"C:\Windows\Fonts\msyhbd.ttc",
        r"C:\Windows\Fonts\simhei.ttf",
    ]
    for fp in font_paths:
        if os.path.exists(fp):
            return ImageFont.truetype(fp, size)
    return ImageFont.load_default()


def render_frame(shot: dict, output_path: Path):
    """为每个分镜渲染一张画面帧（文字卡片风格）"""
    # 创建深色背景
    img = Image.new("RGB", (VIDEO_WIDTH, VIDEO_HEIGHT), "#0a0a1a")
    draw = ImageDraw.Draw(img)

    # 渐变背景效果（简单模拟）
    for y in range(VIDEO_HEIGHT):
        r = int(10 + (y / VIDEO_HEIGHT) * 20)
        g = int(10 + (y / VIDEO_HEIGHT) * 10)
        b = int(26 + (y / VIDEO_HEIGHT) * 40)
        draw.line([(0, y), (VIDEO_WIDTH, y)], fill=(r, g, b))

    # 顶部标题
    title_font = get_font(48)
    title = f"分镜 {shot['id']}"
    draw.text((100, 80), title, fill="#666666", font=title_font)

    # 主视觉文字
    visual = shot["visual"]
    main_font = get_font(64)
    # 自动换行
    max_chars_per_line = 22
    lines = []
    for line in visual.split("\n"):
        while len(line) > max_chars_per_line:
            lines.append(line[:max_chars_per_line])
            line = line[max_chars_per_line:]
        lines.append(line)

    y_start = 300
    for i, line in enumerate(lines):
        draw.text((100, y_start + i * 80), line, fill="#ffffff", font=main_font)

    # 底部旁白
    narration_font = get_font(36)
    narration = shot["narration"]
    max_narration_chars = 40
    narration_lines = []
    while len(narration) > max_narration_chars:
        narration_lines.append(narration[:max_narration_chars])
        narration = narration[max_narration_chars:]
    narration_lines.append(narration)

    y_narration = VIDEO_HEIGHT - 200
    for i, line in enumerate(narration_lines):
        draw.text((100, y_narration + i * 50), line, fill="#aaaaaa", font=narration_font)

    # 底部进度条
    draw.rectangle([(0, VIDEO_HEIGHT - 8), (VIDEO_WIDTH, VIDEO_HEIGHT)], fill="#4a4aff")

    img.save(str(output_path), "PNG")


def generate_frames(shots: list[dict]) -> list[Path]:
    """生成所有分镜的画面帧"""
    frames_dir = OUTPUT_DIR / "frames"
    frames_dir.mkdir(exist_ok=True)

    frame_paths = []
    for shot in shots:
        frame_path = frames_dir / f"shot_{shot['id']:02d}.png"
        render_frame(shot, frame_path)
        frame_paths.append(frame_path)

    print(f"[Step 2] 画面帧生成完成: {len(frame_paths)} 张")
    return frame_paths


# ── Step 3: TTS配音 ─────────────────────────────────────
async def generate_tts(shots: list[dict]) -> list[Path]:
    """为每个分镜生成TTS音频"""
    audio_dir = OUTPUT_DIR / "audio"
    audio_dir.mkdir(exist_ok=True)

    audio_paths = []
    voice = "zh-CN-YunxiNeural"

    for shot in shots:
        audio_path = audio_dir / f"shot_{shot['id']:02d}.mp3"
        communicate = edge_tts.Communicate(shot["narration"], voice)
        await communicate.save(str(audio_path))
        audio_paths.append(audio_path)

    print(f"[Step 3] TTS配音完成: {len(audio_paths)} 段")
    return audio_paths


# ── Step 4: FFmpeg合成视频 ───────────────────────────────
def get_audio_duration(audio_path: Path) -> float:
    """获取音频时长"""
    cmd = [
        "ffprobe", "-v", "quiet", "-show_entries", "format=duration",
        "-of", "default=noprint_wrappers=1:nokey=1", str(audio_path)
    ]
    result = subprocess.run(cmd, capture_output=True, text=True)
    return float(result.stdout.strip())


def compose_video(shots: list[dict], frames: list[Path], audios: list[Path]) -> Path:
    """用FFmpeg合成最终视频"""
    temp_dir = OUTPUT_DIR / "temp"
    temp_dir.mkdir(exist_ok=True)

    # 为每个分镜生成视频片段
    segment_paths = []
    total_duration = 0

    for i, (shot, frame, audio) in enumerate(zip(shots, frames, audios)):
        duration = get_audio_duration(audio)
        total_duration += duration

        segment_path = temp_dir / f"segment_{i:02d}.mp4"
        cmd = [
            "ffmpeg", "-y",
            "-loop", "1", "-i", str(frame),
            "-i", str(audio),
            "-c:v", "libx264", "-tune", "stillimage",
            "-c:a", "aac", "-b:a", "192k",
            "-pix_fmt", "yuv420p",
            "-t", str(duration),
            "-r", str(FPS),
            "-vf", f"scale={VIDEO_WIDTH}:{VIDEO_HEIGHT}",
            "-shortest",
            str(segment_path)
        ]
        subprocess.run(cmd, capture_output=True, text=True)
        segment_paths.append(segment_path)
        print(f"  片段{i+1}/{len(shots)}: {duration:.1f}s")

    # 合并所有片段
    concat_file = temp_dir / "concat.txt"
    with open(concat_file, "w") as f:
        for seg in segment_paths:
            f.write(f"file '{seg}'\n")

    final_video = OUTPUT_DIR / "7视频工具横评.mp4"
    cmd = [
        "ffmpeg", "-y",
        "-f", "concat", "-safe", "0",
        "-i", str(concat_file),
        "-c", "copy",
        str(final_video)
    ]
    result = subprocess.run(cmd, capture_output=True, text=True)

    if result.returncode != 0:
        # concat copy失败时重编码
        cmd = [
            "ffmpeg", "-y",
            "-f", "concat", "-safe", "0",
            "-i", str(concat_file),
            "-c:v", "libx264", "-c:a", "aac",
            str(final_video)
        ]
        subprocess.run(cmd, capture_output=True, text=True)

    print(f"[Step 4] 视频合成完成: {final_video}")
    print(f"  总时长: {total_duration:.1f}s")
    print(f"  文件大小: {final_video.stat().st_size / 1024 / 1024:.1f} MB")

    # 清理临时文件
    import shutil
    shutil.rmtree(temp_dir, ignore_errors=True)

    return final_video


# ── 主流程 ──────────────────────────────────────────────
async def main():
    print("=" * 60)
    print("MoneyPrinterTurbo 模式视频生成")
    print("主题: 7大开源视频制作工具横评")
    print("=" * 60)

    # Step 1: AI生成文案
    print("\n[Step 1] 调用 Agnes AI 生成文案...")
    shots = generate_script()

    # Step 2: 生成画面帧
    print("\n[Step 2] 生成画面帧...")
    frames = generate_frames(shots)

    # Step 3: TTS配音
    print("\n[Step 3] 生成TTS配音...")
    audios = await generate_tts(shots)

    # Step 4: FFmpeg合成
    print("\n[Step 4] FFmpeg合成视频...")
    video = compose_video(shots, frames, audios)

    print("\n" + "=" * 60)
    print(f"视频已生成: {video}")
    print("=" * 60)


if __name__ == "__main__":
    asyncio.run(main())
