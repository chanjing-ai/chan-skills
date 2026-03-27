#!/usr/bin/env python3
"""
创建蝉镜视频合成任务。
用法:
  公共数字人文本驱动:
    create_task --person-id <id> --figure-type sit_body --text "台词" --audio-man <声音id> --subtitle show
  定制数字人文本驱动:
    create_task --person-id <id> --text "台词" --audio-man <声音id> --subtitle hide
  音频驱动:
    create_task --person-id <id> --audio-file-id <file_id>
    create_task --person-id <id> --wav-url https://example.com/demo.wav
输出: video_id（一行）或错误到 stderr
"""
import argparse
import json
import re
import sys
import urllib.request
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from _auth import get_token

API_BASE = (__import__("os").environ.get("CHANJING_OPENAPI_BASE_URL") or __import__("os").environ.get("CHANJING_API_BASE") or "https://open-api.chanjing.cc").rstrip("/")


def validate_hex_color(value, arg_name):
    if value is None:
        return
    if not re.fullmatch(r"#[0-9A-Fa-f]{6}", value):
        raise ValueError(f"{arg_name} 格式不正确，应为 #RRGGBB")


def get_default_subtitle_fields(args):
    # 官方文档给出了 1080p 和 4K 两组推荐值；只有在画布已放大到 4K 尺寸时才使用 4K 组。
    use_4k_defaults = args.resolution_rate == 1 and args.screen_width >= 2160 and args.screen_height >= 3840
    if use_4k_defaults:
        return {
            "x": 80,
            "y": 2840,
            "width": 2000,
            "height": 1000,
            "font_size": 150,
            "color": "#FFFFFF",
            "stroke_width": 7,
            "asr_type": 0,
        }
    return {
        "x": 31,
        "y": 1521,
        "width": 1000,
        "height": 200,
        "font_size": 64,
        "color": "#FFFFFF",
        "stroke_width": 7,
        "asr_type": 0,
    }


def build_subtitle_config(args):
    subtitle_fields = {
        "x": args.subtitle_x,
        "y": args.subtitle_y,
        "width": args.subtitle_width,
        "height": args.subtitle_height,
        "font_size": args.subtitle_font_size,
        "color": args.subtitle_color,
        "stroke_color": args.subtitle_stroke_color,
        "stroke_width": args.subtitle_stroke_width,
        "font_id": args.subtitle_font_id,
        "asr_type": args.subtitle_asr_type,
    }
    has_style_fields = any(value is not None for value in subtitle_fields.values())

    if args.hide_subtitle:
        if has_style_fields:
            raise ValueError("隐藏字幕时，不能同时传字幕位置或样式参数")
        return {"show": False}

    if args.subtitle is None:
        if has_style_fields:
            raise ValueError("传字幕位置或样式参数时，必须同时传 --subtitle show")
        return None

    config = {"show": args.subtitle == "show"}
    if not config["show"]:
        if has_style_fields:
            raise ValueError("使用 --subtitle hide 时，不能同时传字幕位置或样式参数")
        return config

    validate_hex_color(args.subtitle_color, "--subtitle-color")
    validate_hex_color(args.subtitle_stroke_color, "--subtitle-stroke-color")

    config.update(get_default_subtitle_fields(args))

    for key, value in subtitle_fields.items():
        if value is not None:
            config[key] = value

    if config["width"] > args.screen_width:
        raise ValueError("字幕宽度不能超过屏幕宽度")
    if config["height"] > args.screen_height:
        raise ValueError("字幕高度不能超过屏幕高度")
    if config["x"] + config["width"] > args.screen_width:
        raise ValueError("字幕区域超出屏幕宽度，请检查 --subtitle-x 和 --subtitle-width")
    if config["y"] + config["height"] > args.screen_height:
        raise ValueError("字幕区域超出屏幕高度，请检查 --subtitle-y 和 --subtitle-height")
    return config


def build_body(args):
    if args.audio_file_id and args.wav_url:
        raise ValueError("--audio-file-id 和 --wav-url 只能二选一")

    person = {
        "id": args.person_id,
        "x": args.person_x,
        "y": args.person_y,
        "width": args.person_width,
        "height": args.person_height,
    }
    if args.figure_type:
        person["figure_type"] = args.figure_type

    if args.audio_file_id or args.wav_url:
        audio = {
            "type": "audio",
            "volume": args.volume,
            "language": args.language,
        }
        if args.audio_file_id:
            audio["file_id"] = args.audio_file_id
        if args.wav_url:
            audio["wav_url"] = args.wav_url
    else:
        if not args.text or not args.audio_man:
            raise ValueError("文本驱动需同时提供 --text 和 --audio-man")
        if len(args.text) > 4000:
            raise ValueError("文本长度不能超过 4000 字符")
        audio = {
            "type": "tts",
            "volume": args.volume,
            "language": args.language,
            "tts": {
                "text": [args.text],
                "speed": args.speed,
                "audio_man": args.audio_man,
                "pitch": args.pitch,
            },
        }

    body = {
        "person": person,
        "audio": audio,
        "bg_color": args.bg_color,
        "screen_width": args.screen_width,
        "screen_height": args.screen_height,
        "model": args.model,
        "backway": args.backway,
        "add_compliance_watermark": args.add_compliance_watermark,
        "compliance_watermark_position": args.compliance_watermark_position,
        "resolution_rate": args.resolution_rate,
    }

    if args.drive_mode:
        body["drive_mode"] = args.drive_mode
    if args.callback:
        body["callback"] = args.callback
    if args.rgba_mode:
        body["is_rgba_mode"] = True
    subtitle_config = build_subtitle_config(args)
    if subtitle_config is not None:
        body["subtitle_config"] = subtitle_config

    if args.bg_file_id or args.bg_src_url:
        bg = {
            "x": args.bg_x,
            "y": args.bg_y,
            "width": args.bg_width,
            "height": args.bg_height,
        }
        if args.bg_file_id:
            bg["file_id"] = args.bg_file_id
        if args.bg_src_url:
            bg["src_url"] = args.bg_src_url
        body["bg"] = bg

    return body


def main():
    parser = argparse.ArgumentParser(description="创建蝉镜视频合成任务")
    parser.add_argument("--person-id", required=True, help="数字人形象 ID（来自 list_figures）")
    parser.add_argument("--text", help="文本驱动时的台词")
    parser.add_argument("--audio-man", help="文本驱动时的声音 ID，默认可用 list_figures 返回的 audio_man_id")
    parser.add_argument("--audio-file-id", help="音频驱动文件 ID（来自 upload_file）")
    parser.add_argument("--wav-url", help="音频驱动的远端音频链接")
    parser.add_argument("--person-x", type=int, default=0, help="人物 x 坐标")
    parser.add_argument("--person-y", type=int, default=0, help="人物 y 坐标")
    parser.add_argument("--person-width", type=int, default=1080, help="人物宽度")
    parser.add_argument("--person-height", type=int, default=1920, help="人物高度")
    parser.add_argument("--figure-type", help="公共数字人形态，如 sit_body / whole_body")
    parser.add_argument("--drive-mode", choices=["random"], help="驱动模式；不传表示正常驱动")
    parser.add_argument("--backway", type=int, choices=[1, 2], default=1, help="人物素材播放顺序")
    parser.add_argument("--rgba-mode", action="store_true", help="生成四通道 webm 视频")
    parser.add_argument("--screen-width", type=int, default=1080, help="画布宽度")
    parser.add_argument("--screen-height", type=int, default=1920, help="画布高度")
    parser.add_argument("--model", type=int, choices=[0, 1], default=0, help="0 基础版，1 高质版")
    parser.add_argument("--resolution-rate", type=int, choices=[0, 1], default=0, help="0 为 1080p，1 为 4K")
    parser.add_argument("--speed", type=float, default=1, help="TTS 语速 0.5-2")
    parser.add_argument("--pitch", type=float, default=1, help="TTS 音调")
    parser.add_argument("--volume", type=int, default=100, help="音量 1-100")
    parser.add_argument("--language", default="cn", help="语言类型，默认 cn")
    parser.add_argument("--bg-color", default="#EDEDED", help="纯色背景，默认 #EDEDED")
    parser.add_argument("--bg-file-id", help="背景素材 file_id（来自 upload_file）")
    parser.add_argument("--bg-src-url", help="背景图片远端链接，仅支持 jpg/png")
    parser.add_argument("--bg-x", type=int, default=0, help="背景 x 坐标")
    parser.add_argument("--bg-y", type=int, default=0, help="背景 y 坐标")
    parser.add_argument("--bg-width", type=int, default=1080, help="背景宽度")
    parser.add_argument("--bg-height", type=int, default=1920, help="背景高度")
    subtitle_group = parser.add_mutually_exclusive_group()
    subtitle_group.add_argument(
        "--subtitle",
        choices=["show", "hide"],
        help="显式设置字幕开关；show 时可继续配合字幕位置和样式参数",
    )
    subtitle_group.add_argument("--hide-subtitle", action="store_true", help="隐藏字幕（兼容旧用法）")
    parser.add_argument("--subtitle-x", type=int, help="字幕区域起始 x 坐标，基于左上角原点")
    parser.add_argument("--subtitle-y", type=int, help="字幕区域起始 y 坐标，基于左上角原点")
    parser.add_argument("--subtitle-width", type=int, help="字幕区域宽度")
    parser.add_argument("--subtitle-height", type=int, help="字幕区域高度")
    parser.add_argument("--subtitle-font-size", type=int, help="字幕字号")
    parser.add_argument("--subtitle-color", help="字幕颜色，格式 #RRGGBB")
    parser.add_argument("--subtitle-stroke-color", help="字幕描边颜色，格式 #RRGGBB")
    parser.add_argument("--subtitle-stroke-width", type=int, help="字幕描边宽度")
    parser.add_argument("--subtitle-font-id", help="字幕字体 ID")
    parser.add_argument(
        "--subtitle-asr-type",
        type=int,
        choices=[0, 1],
        help="字幕时间戳来源：0 自动生成，1 用户输入",
    )
    parser.add_argument("--callback", help="任务完成回调 URL")
    parser.add_argument("--add-compliance-watermark", action="store_true", help="添加 AI 合规水印")
    parser.add_argument(
        "--compliance-watermark-position",
        type=int,
        choices=[0, 1, 2, 3],
        default=0,
        help="合规水印位置：0 左上，1 右上，2 左下，3 右下",
    )
    args = parser.parse_args()

    try:
        body = build_body(args)
    except ValueError as exc:
        print(str(exc), file=sys.stderr)
        sys.exit(1)

    token, err = get_token()
    if err:
        print(err, file=sys.stderr)
        sys.exit(1)

    req = urllib.request.Request(
        f"{API_BASE}/open/v1/create_video",
        data=json.dumps(body).encode("utf-8"),
        headers={"access_token": token, "Content-Type": "application/json"},
        method="POST",
    )
    with urllib.request.urlopen(req, timeout=30) as resp:
        res = json.loads(resp.read().decode("utf-8"))

    if res.get("code") != 0:
        print(res.get("msg", res), file=sys.stderr)
        sys.exit(1)

    video_id = res.get("data")
    if not video_id:
        print("响应无 data", file=sys.stderr)
        sys.exit(1)
    print(video_id)


if __name__ == "__main__":
    main()
