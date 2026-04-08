"""
测试 JSON 渲染引擎
验证各种布局原语能正确渲染到 1-bit e-ink 图像
"""
import json
import os
import sys
from io import BytesIO

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from PIL import Image
from core.json_renderer import render_json_mode, RenderContext, _localized_footer_label, _localized_footer_attribution
from core.config import SCREEN_WIDTH as SCREEN_W, SCREEN_HEIGHT as SCREEN_H


def _make_mode_def(body_blocks, content_type="static", footer=None):
    return {
        "mode_id": "TEST",
        "display_name": "Test",
        "content": {"type": content_type},
        "layout": {
            "status_bar": {"line_width": 1, "dashed": False},
            "body": body_blocks,
            "footer": footer or {"label": "TEST", "attribution_template": ""},
        },
    }


def _make_component_tree_mode_def(body_tree, footer=None):
    return {
        "mode_id": "TREE_TEST",
        "display_name": "Tree Test",
        "content": {"type": "static"},
        "layout": {
            "layout_engine": "component_tree",
            "status_bar": {"line_width": 1, "dashed": False},
            "component_theme": {
                "body_font_size": 12,
                "body_line_gap": 4,
                "section_title_font_size": 12,
                "section_icon_size": 12,
                "section_icon_gap": 16,
                "section_title_gap": 6,
                "section_content_indent": 36,
                "section_content_gap": 4,
            },
            "body": body_tree,
            "footer": footer or {"label": "TREE", "attribution_template": ""},
        },
    }


def test_render_produces_correct_size_image():
    mode_def = _make_mode_def([
        {"type": "centered_text", "field": "text", "font_size": 16, "vertical_center": True}
    ])
    content = {"text": "Hello World"}
    img = render_json_mode(
        mode_def, content,
        date_str="1月1日", weather_str="晴 20°C", battery_pct=85,
    )
    assert isinstance(img, Image.Image)
    assert img.size == (SCREEN_W, SCREEN_H)
    assert img.mode == "1"


def test_render_centered_text():
    mode_def = _make_mode_def([
        {"type": "centered_text", "field": "quote", "font_size": 14, "vertical_center": True}
    ])
    content = {"quote": "测试居中文本"}
    img = render_json_mode(
        mode_def, content,
        date_str="2月18日", weather_str="多云 15°C", battery_pct=90,
    )
    assert img.size == (SCREEN_W, SCREEN_H)


def test_render_text_block():
    mode_def = _make_mode_def([
        {"type": "spacer", "height": 20},
        {"type": "text", "field": "title", "font_size": 16, "align": "center"},
        {"type": "text", "template": "作者: {author}", "font_size": 12, "align": "center"},
    ])
    content = {"title": "静夜思", "author": "李白"}
    img = render_json_mode(
        mode_def, content,
        date_str="2月18日", weather_str="晴", battery_pct=75,
    )
    assert img.size == (SCREEN_W, SCREEN_H)


def test_render_separator():
    mode_def = _make_mode_def([
        {"type": "spacer", "height": 50},
        {"type": "separator", "style": "solid", "margin_x": 24},
        {"type": "spacer", "height": 10},
        {"type": "separator", "style": "dashed", "margin_x": 24},
        {"type": "spacer", "height": 10},
        {"type": "separator", "style": "short", "width": 60},
    ])
    img = render_json_mode(
        _make_mode_def([
            {"type": "spacer", "height": 50},
            {"type": "separator", "style": "solid"},
            {"type": "separator", "style": "dashed"},
            {"type": "separator", "style": "short", "width": 60},
        ]), {},
        date_str="1月1日", weather_str="晴", battery_pct=100,
    )
    assert img.size == (SCREEN_W, SCREEN_H)


def test_render_list_with_dicts():
    mode_def = _make_mode_def([
        {"type": "spacer", "height": 14},
        {
            "type": "list",
            "field": "exercises",
            "max_items": 5,
            "item_template": "{name}",
            "right_field": "reps",
            "font_size": 13,
            "margin_x": 32,
            "numbered": True,
            "item_spacing": 16,
        },
    ])
    content = {
        "exercises": [
            {"name": "深蹲", "reps": "20次"},
            {"name": "俯卧撑", "reps": "15次"},
            {"name": "平板支撑", "reps": "30秒"},
        ]
    }
    img = render_json_mode(
        mode_def, content,
        date_str="2月18日", weather_str="晴", battery_pct=80,
    )
    assert img.size == (SCREEN_W, SCREEN_H)


def test_render_list_with_strings():
    mode_def = _make_mode_def([
        {"type": "spacer", "height": 14},
        {
            "type": "list",
            "field": "lines",
            "max_items": 4,
            "item_template": "{_value}",
            "font_size": 16,
            "item_spacing": 24,
            "margin_x": 30,
            "align": "center",
        },
    ])
    content = {"lines": ["床前明月光", "疑是地上霜", "举头望明月", "低头思故乡"]}
    img = render_json_mode(
        mode_def, content,
        date_str="2月18日", weather_str="晴", battery_pct=80,
    )
    assert img.size == (SCREEN_W, SCREEN_H)


def test_render_list_wraps_to_multiple_lines():
    mode_def = _make_mode_def([
        {"type": "spacer", "height": 14},
        {
            "type": "list",
            "field": "items",
            "max_items": 1,
            "item_template": "{title}",
            "font_size": 14,
            "item_spacing": 18,
            "margin_x": 24,
        },
    ])
    content = {
        "items": [
            {
                "title": "This is a very long Hacker News headline that should wrap onto a second line in the list renderer"
            }
        ]
    }
    img = render_json_mode(
        mode_def, content,
        date_str="2月18日", weather_str="晴", battery_pct=80,
    ).convert("L")
    second_line_band = img.crop((24, 32, SCREEN_W - 24, 52))
    assert min(second_line_band.getdata()) < 255


def test_render_section_with_icon():
    mode_def = _make_mode_def([
        {"type": "spacer", "height": 14},
        {
            "type": "section",
            "title": "训练动作",
            "icon": "exercise",
            "children": [
                {"type": "text", "field": "tip", "font_size": 13, "align": "left", "margin_x": 40},
            ],
        },
    ])
    content = {"tip": "运动前记得热身"}
    img = render_json_mode(
        mode_def, content,
        date_str="2月18日", weather_str="晴", battery_pct=80,
    )
    assert img.size == (SCREEN_W, SCREEN_H)


def test_render_vertical_stack():
    mode_def = _make_mode_def([
        {
            "type": "vertical_stack",
            "spacing": 4,
            "children": [
                {"type": "spacer", "height": 14},
                {"type": "text", "field": "a", "font_size": 14, "align": "center"},
                {"type": "separator", "style": "solid"},
                {"type": "text", "field": "b", "font_size": 14, "align": "center"},
            ],
        },
    ])
    content = {"a": "第一段", "b": "第二段"}
    img = render_json_mode(
        mode_def, content,
        date_str="2月18日", weather_str="晴", battery_pct=80,
    )
    assert img.size == (SCREEN_W, SCREEN_H)


def test_render_conditional():
    mode_def = _make_mode_def([
        {"type": "spacer", "height": 14},
        {
            "type": "conditional",
            "field": "count",
            "conditions": [
                {
                    "op": "gt",
                    "value": 5,
                    "children": [
                        {"type": "text", "template": "很多: {count}", "font_size": 14, "align": "center"},
                    ],
                },
            ],
            "fallback_children": [
                {"type": "text", "template": "少量: {count}", "font_size": 14, "align": "center"},
            ],
        },
    ])

    # count = 10 -> "很多"
    img1 = render_json_mode(
        mode_def, {"count": 10},
        date_str="2月18日", weather_str="晴", battery_pct=80,
    )
    assert img1.size == (SCREEN_W, SCREEN_H)

    # count = 3 -> fallback "少量"
    img2 = render_json_mode(
        mode_def, {"count": 3},
        date_str="2月18日", weather_str="晴", battery_pct=80,
    )
    assert img2.size == (SCREEN_W, SCREEN_H)


def test_render_icon_text():
    mode_def = _make_mode_def([
        {"type": "spacer", "height": 40},
        {"type": "icon_text", "icon": "book", "text": "推荐阅读", "font_size": 14, "margin_x": 24},
    ])
    img = render_json_mode(
        mode_def, {},
        date_str="2月18日", weather_str="晴", battery_pct=80,
    )
    assert img.size == (SCREEN_W, SCREEN_H)


def test_render_with_footer_template():
    mode_def = _make_mode_def(
        [{"type": "centered_text", "field": "quote", "font_size": 16}],
        footer={"label": "CUSTOM", "attribution_template": "— {author}", "dashed": True},
    )
    content = {"quote": "Test", "author": "Author"}
    img = render_json_mode(
        mode_def, content,
        date_str="2月18日", weather_str="晴", battery_pct=80,
    )
    assert img.size == (SCREEN_W, SCREEN_H)


def test_component_tree_layout_renders():
    mode_def = _make_component_tree_mode_def(
        {
            "type": "column",
            "padding_x": 18,
            "padding_y": 8,
            "gap": 10,
            "children": [
                {
                    "type": "section_box",
                    "title": "头条",
                    "icon": "global",
                    "children": [
                        {
                            "type": "repeat",
                            "field": "items",
                            "limit": 2,
                            "gap": 6,
                            "item": {
                                "type": "row",
                                "gap": 8,
                                "align": "end",
                                "children": [
                                    {"type": "text", "field": "title", "grow": 1, "max_lines": 2},
                                    {"type": "text", "field": "score", "font": "inter_medium", "font_size": 11, "align": "right"},
                                ],
                            },
                        }
                    ],
                }
            ],
        }
    )
    content = {
        "items": [
            {"title": "Long title that should wrap across lines in the new layout engine", "score": 120},
            {"title": "Second item", "score": 98},
        ]
    }
    img = render_json_mode(
        mode_def, content,
        date_str="2月18日", weather_str="晴", battery_pct=80,
    )
    assert img.size == (SCREEN_W, SCREEN_H)


def test_component_tree_repeat_wraps_text():
    mode_def = _make_component_tree_mode_def(
        {
            "type": "column",
            "padding_x": 18,
            "padding_y": 8,
            "children": [
                {
                    "type": "section_box",
                    "title": "HN",
                    "icon": "global",
                    "children": [
                        {
                            "type": "repeat",
                            "field": "items",
                            "limit": 1,
                            "item": {
                                "type": "row",
                                "gap": 8,
                                "align": "end",
                                "children": [
                                    {"type": "text", "field": "title", "grow": 1, "max_lines": 2},
                                    {"type": "text", "field": "score", "align": "right", "max_lines": 1},
                                ],
                            },
                        }
                    ],
                }
            ],
        }
    )
    content = {
        "items": [
            {"title": "This is a very long story title that should wrap inside the component tree layout row", "score": 321}
        ]
    }
    img = render_json_mode(
        mode_def, content,
        date_str="2月18日", weather_str="晴", battery_pct=80,
    ).convert("L")
    second_line_band = img.crop((54, 52, SCREEN_W - 60, 76))
    assert min(second_line_band.getdata()) < 255


def test_render_image_block_preserves_palette_colors():
    src = Image.new("RGB", (4, 2), "white")
    src.putpixel((0, 0), (200, 0, 0))
    src.putpixel((1, 0), (232, 176, 0))
    src.putpixel((2, 0), (0, 0, 0))
    buf = BytesIO()
    src.save(buf, format="PNG")
    mode_def = _make_mode_def([
        {"type": "image", "field": "image_url", "width": 40, "height": 20, "x": 100, "y": 80}
    ])
    content = {
        "image_url": "prefetched://artwall",
        "_prefetched_image_url": buf.getvalue(),
    }
    img = render_json_mode(
        mode_def, content,
        date_str="2月18日", weather_str="晴", battery_pct=80,
        colors=4,
    )
    assert img.mode == "P"
    palette_indexes = set(img.crop((100, 80, 140, 100)).getdata())
    assert 3 in palette_indexes
    assert 2 in palette_indexes


def test_builtin_footer_localization():
    assert _localized_footer_label("COUNTDOWN", "COUNTDOWN", "zh") == "倒计时"
    assert _localized_footer_label("COUNTDOWN", "Countdown", "en") == "Countdown"
    assert _localized_footer_attribution("COUNTDOWN", "— Remember", "zh") == "— 静待那天"
    assert _localized_footer_attribution("COUNTDOWN", "— Remember", "en") == "— Remember"


def test_render_with_dashed_status_bar():
    mode_def = {
        "mode_id": "ZEN_TEST",
        "display_name": "Zen Test",
        "content": {"type": "static"},
        "layout": {
            "status_bar": {"line_width": 1, "dashed": True},
            "body": [
                {"type": "centered_text", "field": "word", "font": "noto_serif_regular", "font_size": 48, "vertical_center": True}
            ],
            "footer": {"label": "ZEN", "attribution_template": "— ...", "dashed": True},
        },
    }
    content = {"word": "静"}
    img = render_json_mode(
        mode_def, content,
        date_str="2月18日", weather_str="晴", battery_pct=80,
    )
    assert img.size == (SCREEN_W, SCREEN_H)


def test_render_context_resolve():
    """Test RenderContext.resolve template substitution."""
    from PIL import ImageDraw
    img = Image.new("1", (100, 100), 1)
    draw = ImageDraw.Draw(img)
    ctx = RenderContext(draw=draw, img=img, content={"name": "Alice", "count": 42})

    assert ctx.resolve("Hello {name}!") == "Hello Alice!"
    assert ctx.resolve("{count} items") == "42 items"
    assert ctx.resolve("no placeholders") == "no placeholders"
    assert ctx.resolve("{missing}") == ""


def test_render_stoic_json():
    """End-to-end: render using the builtin STOIC JSON definition."""
    stoic_path = os.path.join(
        os.path.dirname(__file__), "..", "core", "modes", "builtin", "stoic.json"
    )
    with open(stoic_path, "r", encoding="utf-8") as f:
        mode_def = json.load(f)

    content = {
        "quote": "The impediment to action advances action.",
        "author": "Marcus Aurelius",
    }
    img = render_json_mode(
        mode_def, content,
        date_str="2月18日 周二", weather_str="晴 15°C", battery_pct=85,
        weather_code=0, time_str="14:30",
    )
    assert img.size == (SCREEN_W, SCREEN_H)
    assert img.mode == "1"


def test_render_fitness_json():
    """End-to-end: render using the builtin FITNESS JSON definition."""
    fitness_path = os.path.join(
        os.path.dirname(__file__), "..", "core", "modes", "builtin", "fitness.json"
    )
    with open(fitness_path, "r", encoding="utf-8") as f:
        mode_def = json.load(f)

    content = {
        "workout_name": "晨间拉伸",
        "duration": "15分钟",
        "exercises": [
            {"name": "颈部拉伸", "reps": "10次"},
            {"name": "肩部环绕", "reps": "15次"},
            {"name": "腰部扭转", "reps": "20次"},
        ],
        "tip": "运动前充分热身，避免受伤。",
    }
    img = render_json_mode(
        mode_def, content,
        date_str="2月18日 周二", weather_str="多云 12°C", battery_pct=70,
        weather_code=3, time_str="07:00",
    )
    assert img.size == (SCREEN_W, SCREEN_H)


def test_render_poetry_json():
    """End-to-end: render using the builtin POETRY JSON definition."""
    poetry_path = os.path.join(
        os.path.dirname(__file__), "..", "core", "modes", "builtin", "poetry.json"
    )
    with open(poetry_path, "r", encoding="utf-8") as f:
        mode_def = json.load(f)

    content = {
        "title": "静夜思",
        "author": "唐·李白",
        "lines": ["床前明月光", "疑是地上霜", "举头望明月", "低头思故乡"],
        "note": "千古思乡名篇",
    }
    img = render_json_mode(
        mode_def, content,
        date_str="2月18日 周二", weather_str="晴", battery_pct=90,
    )
    assert img.size == (SCREEN_W, SCREEN_H)


def test_render_briefing_component_tree_json():
    briefing_path = os.path.join(
        os.path.dirname(__file__), "..", "core", "modes", "builtin", "briefing.json"
    )
    with open(briefing_path, "r", encoding="utf-8") as f:
        mode_def = json.load(f)

    content = {
        "hn_items": [
            {"title": "Project Glasswing: Securing critical software for the AI era", "score": 1120},
            {"title": "Lunar Flyby", "score": 573},
        ],
        "ph_item": {"name": "Netflix Playground", "tagline": "A world for kids to explore"},
        "ph_name": "Netflix Playground",
        "ph_tagline": "A world for kids to explore along their favorite characters",
        "devto_items": [
            {"title": "Component-based CSS"}
        ],
        "devto_title": "Component-based CSS",
    }
    img = render_json_mode(
        mode_def, content,
        date_str="4月8日 周三", weather_str="21°C", battery_pct=33,
        time_str="4月8日 4时",
    )
    assert img.size == (SCREEN_W, SCREEN_H)


if __name__ == "__main__":
    test_render_produces_correct_size_image()
    test_render_centered_text()
    test_render_text_block()
    test_render_separator()
    test_render_list_with_dicts()
    test_render_list_with_strings()
    test_render_section_with_icon()
    test_render_vertical_stack()
    test_render_conditional()
    test_render_icon_text()
    test_render_with_footer_template()
    test_render_with_dashed_status_bar()
    test_render_context_resolve()
    test_render_stoic_json()
    test_render_fitness_json()
    test_render_poetry_json()
    print("✓ All JSON renderer tests passed")
