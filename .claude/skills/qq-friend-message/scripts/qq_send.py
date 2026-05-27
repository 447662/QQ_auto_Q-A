#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Windows QQ friend message GUI automation.

This script controls the local QQ desktop client. The default `fill` command
opens a chat and fills the message box without sending.
"""

from __future__ import annotations

import argparse
import importlib.util
import os
import platform
import subprocess
import sys
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable, Optional


QQ_TITLE_KEYWORDS = ("QQ", "腾讯QQ", "TIM")
QQ_PROCESS_NAMES = ("qq", "tim")
NON_CHAT_TITLE_KEYWORDS = ("设置", "安全", "验证", "登录", "文件", "图片查看", "截图")
INSTALL_HINT = "pip install pywinauto pyperclip"


class QQAutomationError(RuntimeError):
    pass


def log(message: str) -> None:
    print(message, flush=True)


def fail(message: str, code: int = 1) -> int:
    print("错误: " + message, file=sys.stderr, flush=True)
    return code


def has_module(name: str) -> bool:
    return importlib.util.find_spec(name) is not None


def ensure_windows() -> None:
    if platform.system().lower() != "windows":
        raise QQAutomationError("本工具只支持 Windows 本机 QQ 客户端。")


def ensure_dependencies() -> None:
    missing = [name for name in ("pywinauto", "pyperclip") if not has_module(name)]
    if missing:
        raise QQAutomationError(
            "缺少依赖: {}。请先安装: {}".format(", ".join(missing), INSTALL_HINT)
        )


def import_runtime_deps():
    ensure_dependencies()
    from pywinauto import Desktop, Application, keyboard  # type: ignore
    import pyperclip  # type: ignore

    return Desktop, Application, keyboard, pyperclip


def set_file_clipboard(file_path: Path) -> None:
    path = str(file_path.resolve())
    escaped_path = path.replace("'", "''")
    script = """
Add-Type -AssemblyName System.Windows.Forms
$path = '{}'
$collection = New-Object System.Collections.Specialized.StringCollection
[void]$collection.Add($path)
[System.Windows.Forms.Clipboard]::SetFileDropList($collection)
""".format(escaped_path)
    completed = subprocess.run(
        ["powershell", "-NoProfile", "-Command", script],
        check=False,
        capture_output=True,
        text=True,
    )
    if completed.returncode != 0:
        detail = (completed.stderr or completed.stdout or "").strip()
        raise QQAutomationError("设置文件剪贴板失败: {}".format(detail or completed.returncode))


@dataclass
class QQWindow:
    handle: int
    title: str
    process_id: int


def normalize_text(value: str) -> str:
    return "".join(value.split()).lower()


def looks_like_qq_window(title: str) -> bool:
    clean = title.strip()
    if not clean:
        return False
    if any(keyword.lower() in clean.lower() for keyword in NON_CHAT_TITLE_KEYWORDS):
        return False
    return any(keyword.lower() in clean.lower() for keyword in QQ_TITLE_KEYWORDS)


def list_candidate_windows(Desktop) -> list[QQWindow]:
    windows: list[QQWindow] = []
    for backend in ("uia", "win32"):
        try:
            desktop = Desktop(backend=backend)
            backend_windows = desktop.windows(visible_only=False)
        except Exception:
            continue
        for win in backend_windows:
            title = win.window_text().strip()
            try:
                process_id = int(win.process_id())
                rect = win.rectangle()
            except Exception:
                continue
            if rect.width() < 300 or rect.height() < 300 or rect.left < -1000 or rect.top < -1000:
                continue
            process_name = ""
            if process_id:
                try:
                    process_name = subprocess.run(
                        ["powershell", "-NoProfile", "-Command", "(Get-Process -Id {} -ErrorAction Stop).ProcessName".format(process_id)],
                        check=False,
                        capture_output=True,
                        text=True,
                    ).stdout.strip().lower()
                except Exception:
                    process_name = ""
            if process_name not in QQ_PROCESS_NAMES:
                continue
            if any(existing.handle == int(win.handle) for existing in windows):
                continue
            windows.append(QQWindow(handle=int(win.handle), title=title or process_name.upper(), process_id=process_id))
    return windows


def pick_window(windows: Iterable[QQWindow], title_hint: Optional[str]) -> QQWindow:
    candidates = list(windows)
    if title_hint:
        hinted = [window for window in candidates if title_hint.lower() in window.title.lower()]
        if hinted:
            return hinted[0]
    if not candidates:
        raise QQAutomationError("没有找到已运行且可识别的 QQ/TIM 窗口，请先打开并登录 QQ。")
    def score(window: QQWindow) -> int:
        value = 0
        if window.title == "QQ":
            value += 10
        if window.title:
            value += 2
        return value
    return sorted(candidates, key=score, reverse=True)[0]


def connect_window(Desktop, Application, title_hint: Optional[str]):
    window_info = pick_window(list_candidate_windows(Desktop), title_hint)
    for backend in ("uia", "win32"):
        try:
            app = Application(backend=backend).connect(handle=window_info.handle)
            window = app.window(handle=window_info.handle)
            return window_info, window
        except Exception:
            continue
    raise QQAutomationError("无法连接 QQ 窗口。")


def activate_window(window) -> None:
    try:
        if window.is_minimized():
            window.restore()
    except Exception:
        pass
    window.set_focus()
    time.sleep(0.4)


def set_clipboard(pyperclip, text: str) -> str:
    try:
        previous = pyperclip.paste()
    except Exception:
        previous = ""
    pyperclip.copy(text)
    return previous


def restore_clipboard(pyperclip, previous: str) -> None:
    try:
        pyperclip.copy(previous)
    except Exception:
        pass


def send_hotkey(keyboard, keys: str, pause: float = 0.25) -> None:
    keyboard.send_keys(keys)
    time.sleep(pause)


def control_type(control) -> str:
    try:
        return str(control.element_info.control_type)
    except Exception:
        return ""


def find_search_edit(window):
    try:
        win_rect = window.rectangle()
        descendants = window.descendants()
    except Exception:
        return None
    candidates = []
    for child in descendants:
        if control_type(child) != "Edit":
            continue
        try:
            rect = child.rectangle()
        except Exception:
            continue
        if rect.left < win_rect.left + 520 and rect.top < win_rect.top + 220 and rect.width() > 80:
            candidates.append((rect.top, rect.left, child))
    if not candidates:
        return None
    candidates.sort(key=lambda item: (item[0], item[1]))
    return candidates[0][2]


def focus_search_edit(window) -> bool:
    target = find_search_edit(window)
    if target is None:
        return False
    try:
        target.click_input()
    except Exception:
        target.set_focus()
    time.sleep(0.3)
    return True


def set_search_text(window, keyboard, pyperclip, nickname: str, search_pause: float) -> None:
    target = find_search_edit(window)
    if target is None:
        send_hotkey(keyboard, "^f", 0.25)
        previous = set_clipboard(pyperclip, nickname)
        try:
            send_hotkey(keyboard, "^a", 0.1)
            send_hotkey(keyboard, "^v", search_pause)
        finally:
            restore_clipboard(pyperclip, previous)
        return
    try:
        target.click_input()
    except Exception:
        target.set_focus()
    time.sleep(0.2)
    try:
        target.set_edit_text(nickname)
        time.sleep(search_pause)
        return
    except Exception:
        pass
    previous = set_clipboard(pyperclip, nickname)
    try:
        send_hotkey(keyboard, "^a", 0.1)
        send_hotkey(keyboard, "^v", search_pause)
    finally:
        restore_clipboard(pyperclip, previous)


def search_and_open_chat(window, keyboard, pyperclip, nickname: str, search_pause: float) -> None:
    activate_window(window)
    set_search_text(window, keyboard, pyperclip, nickname, search_pause)
    send_hotkey(keyboard, "{ENTER}", 0.9)


def find_texts(control, limit: int = 160) -> list[str]:
    texts: list[str] = []
    try:
        descendants = control.descendants()
    except Exception:
        descendants = []
    for child in descendants[:limit]:
        try:
            text = child.window_text().strip()
        except Exception:
            continue
        if text and text not in texts:
            texts.append(text)
    return texts


def confirm_chat_target(window, nickname: str, strict: bool) -> bool:
    expected = normalize_text(nickname)
    if not expected:
        return False

    title = ""
    try:
        title = window.window_text().strip()
    except Exception:
        title = ""

    if expected in normalize_text(title):
        return True

    texts = find_texts(window, limit=220)
    if any(expected in normalize_text(text) for text in texts):
        return True

    if strict:
        return False
    log("警告: 无法从窗口标题或控件文本确认当前会话名，已按非严格模式继续。")
    return True


def fill_message(window, keyboard, pyperclip, message: str, restore_clip: bool) -> None:
    activate_window(window)
    previous = set_clipboard(pyperclip, message)
    try:
        send_hotkey(keyboard, "^v", 0.4)
    finally:
        if restore_clip:
            restore_clipboard(pyperclip, previous)


def attach_file(window, keyboard, file_path: Path) -> None:
    activate_window(window)
    set_file_clipboard(file_path)
    clicked_input = False
    try:
        win_rect = window.rectangle()
        descendants = window.descendants()
        groups = []
        for child in descendants:
            if control_type(child) not in ("Group", "Edit", "Document"):
                continue
            try:
                rect = child.rectangle()
            except Exception:
                continue
            if rect.left > win_rect.left + 420 and rect.top > win_rect.bottom - 300 and rect.bottom < win_rect.bottom - 40:
                groups.append((rect.top, rect.left, child))
        if groups:
            groups.sort(key=lambda item: (item[0], item[1]))
            groups[-1][2].click_input()
            clicked_input = True
    except Exception:
        clicked_input = False
    if not clicked_input:
        send_hotkey(keyboard, "^{END}", 0.2)
    send_hotkey(keyboard, "^v", 1.2)


def validate_message(message: str) -> None:
    if not message or not message.strip():
        raise QQAutomationError("消息内容不能为空。")


def wait_before_send(seconds: int) -> None:
    for remaining in range(seconds, 0, -1):
        log("{} 秒后发送，按 Ctrl+C 可取消。".format(remaining))
        time.sleep(1)


def click_send_button(window) -> bool:
    try:
        win_rect = window.rectangle()
        descendants = window.descendants()
    except Exception:
        return False
    candidates = []
    for child in descendants:
        if control_type(child) != "Button":
            continue
        try:
            title = child.window_text().strip()
            rect = child.rectangle()
        except Exception:
            continue
        if title and ("发送" in title or "����" in title) and rect.left > win_rect.right - 280 and rect.top > win_rect.bottom - 140:
            candidates.append((rect.top, rect.left, child))
    if not candidates:
        return False
    candidates.sort(key=lambda item: (item[0], item[1]))
    candidates[-1][2].click_input()
    time.sleep(0.6)
    return True


def click_file_confirm_button(Desktop) -> bool:
    try:
        desktop = Desktop(backend="uia")
        windows = desktop.windows()
    except Exception:
        return False
    for dialog in windows:
        try:
            title = dialog.window_text().strip()
            descendants = dialog.descendants()
        except Exception:
            continue
        if title and "发送给" not in title and "����" not in title:
            joined = " ".join([title] + [child.window_text().strip() for child in descendants[:40] if child.window_text().strip()])
            if "发送给" not in joined and "����" not in joined:
                continue
        buttons = []
        for child in descendants:
            if control_type(child) != "Button":
                continue
            try:
                text = child.window_text().strip()
                rect = child.rectangle()
            except Exception:
                continue
            if text and ("发送" in text or "����" in text):
                buttons.append((rect.top, rect.left, child))
        if buttons:
            buttons.sort(key=lambda item: (item[0], item[1]))
            buttons[-1][2].click_input()
            time.sleep(0.8)
            return True
    return False


def trigger_send(window, keyboard, send_keys: str, Desktop=None, confirm_file_dialog: bool = False) -> None:
    if click_send_button(window):
        log("已点击 QQ 发送按钮。")
    else:
        send_hotkey(keyboard, send_keys, 0.5)
        log("未找到发送按钮，已触发发送快捷键。")
    if confirm_file_dialog and Desktop is not None:
        if click_file_confirm_button(Desktop):
            log("已点击文件发送确认按钮。")
        else:
            log("未找到文件发送确认弹窗按钮，请检查 QQ 是否仍在等待确认。")


def command_check(args: argparse.Namespace) -> int:
    try:
        ensure_windows()
        Desktop, Application, _keyboard, _pyperclip = import_runtime_deps()
        windows = list_candidate_windows(Desktop)
        log("Windows: OK")
        log("依赖: OK")
        if not windows:
            return fail("没有找到 QQ/TIM 窗口，请先打开并登录 QQ。")
        log("找到 {} 个候选 QQ/TIM 窗口:".format(len(windows)))
        for index, window in enumerate(windows, 1):
            log("  {}. {} (pid={}, handle={})".format(index, window.title, window.process_id, window.handle))
        if not args.no_connect:
            picked, connected = connect_window(Desktop, Application, args.title_hint)
            activate_window(connected)
            log("已连接并激活: {}".format(picked.title))
        return 0
    except QQAutomationError as exc:
        return fail(str(exc))
    except Exception as exc:
        return fail("检查失败: {}".format(exc))


def command_inspect(args: argparse.Namespace) -> int:
    try:
        ensure_windows()
        Desktop, Application, _keyboard, _pyperclip = import_runtime_deps()
        picked, window = connect_window(Desktop, Application, args.title_hint)
        activate_window(window)
        log("窗口: {} (pid={}, handle={})".format(picked.title, picked.process_id, picked.handle))
        log("控件树摘要:")
        window.print_control_identifiers(depth=args.depth, filename=None)
        return 0
    except QQAutomationError as exc:
        return fail(str(exc))
    except Exception as exc:
        return fail("检查控件树失败: {}".format(exc))


def open_and_fill(args: argparse.Namespace, should_send: bool) -> int:
    try:
        ensure_windows()
        validate_message(args.message)
        Desktop, Application, keyboard, pyperclip = import_runtime_deps()
        picked, window = connect_window(Desktop, Application, args.title_hint)
        log("已连接 QQ 窗口: {}".format(picked.title))
        if not args.skip_search:
            search_and_open_chat(window, keyboard, pyperclip, args.nickname, args.search_pause)
        else:
            activate_window(window)
        if not confirm_chat_target(window, args.nickname, strict=not args.allow_unverified_chat):
            raise QQAutomationError("无法确认当前会话是目标好友，已停止，未填入/发送消息。")
        fill_message(window, keyboard, pyperclip, args.message, restore_clip=not args.keep_clipboard)
        log("已将消息填入目标会话输入框，未发送。")
        if not should_send:
            return 0
        expected_confirm = "发送给{}".format(args.nickname)
        if args.confirm_text != expected_confirm:
            raise QQAutomationError(
                "确认文本不匹配。若确定发送，请传入 --confirm-text \"{}\"。消息仍停留在输入框，未发送。".format(expected_confirm)
            )
        if args.countdown > 0:
            wait_before_send(args.countdown)
        trigger_send(window, keyboard, args.send_keys)
        log("已触发发送动作。")
        return 0
    except KeyboardInterrupt:
        return fail("已取消发送。")
    except QQAutomationError as exc:
        return fail(str(exc))
    except Exception as exc:
        return fail("执行失败: {}".format(exc))


def command_fill(args: argparse.Namespace) -> int:
    return open_and_fill(args, should_send=False)


def command_send(args: argparse.Namespace) -> int:
    return open_and_fill(args, should_send=True)


def command_send_file(args: argparse.Namespace) -> int:
    try:
        ensure_windows()
        file_path = Path(args.file).expanduser()
        if not file_path.exists() or not file_path.is_file():
            raise QQAutomationError("文件不存在或不是普通文件: {}".format(file_path))
        Desktop, Application, keyboard, pyperclip = import_runtime_deps()
        picked, window = connect_window(Desktop, Application, args.title_hint)
        log("已连接 QQ 窗口: {}".format(picked.title))
        if not args.skip_search:
            search_and_open_chat(window, keyboard, pyperclip, args.nickname, args.search_pause)
        else:
            activate_window(window)
        if not confirm_chat_target(window, args.nickname, strict=not args.allow_unverified_chat):
            raise QQAutomationError("无法确认当前会话是目标好友，已停止，未发送文件。")
        attach_file(window, keyboard, file_path)
        expected_confirm = "发送文件给{}".format(args.nickname)
        if args.confirm_text != expected_confirm:
            raise QQAutomationError(
                "确认文本不匹配。若确定发送文件，请传入 --confirm-text \"{}\"。文件可能已贴入会话，尚未触发发送。".format(expected_confirm)
            )
        if args.countdown > 0:
            wait_before_send(args.countdown)
        trigger_send(window, keyboard, args.send_keys, Desktop=Desktop, confirm_file_dialog=True)
        log("已触发文件发送动作。")
        return 0
    except KeyboardInterrupt:
        return fail("已取消发送文件。")
    except QQAutomationError as exc:
        return fail(str(exc))
    except Exception as exc:
        return fail("发送文件失败: {}".format(exc))


def add_common_message_args(parser: argparse.ArgumentParser) -> None:
    parser.add_argument("--nickname", required=True, help="QQ 好友昵称或备注名，建议使用唯一备注名")
    parser.add_argument("--message", required=True, help="要填入/发送的消息文本")
    parser.add_argument("--title-hint", help="QQ 窗口标题提示，多个 QQ/TIM 窗口时用于筛选")
    parser.add_argument("--search-pause", type=float, default=1.0, help="搜索后等待秒数，默认 1.0")
    parser.add_argument("--allow-unverified-chat", action="store_true", help="无法确认会话名时仍继续，不建议发送模式使用")
    parser.add_argument("--keep-clipboard", action="store_true", help="执行后保留消息在剪贴板中")
    parser.add_argument("--skip-search", action="store_true", help="跳过搜索，直接使用当前已打开的 QQ 会话")


def add_common_target_args(parser: argparse.ArgumentParser) -> None:
    parser.add_argument("--nickname", required=True, help="QQ 好友昵称或备注名，建议使用唯一备注名")
    parser.add_argument("--title-hint", help="QQ 窗口标题提示，多个 QQ/TIM 窗口时用于筛选")
    parser.add_argument("--search-pause", type=float, default=1.0, help="搜索后等待秒数，默认 1.0")
    parser.add_argument("--allow-unverified-chat", action="store_true", help="无法确认会话名时仍继续，不建议发送模式使用")
    parser.add_argument("--skip-search", action="store_true", help="跳过搜索，直接使用当前已打开的 QQ 会话")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Windows QQ 普通好友消息 GUI 自动化。默认使用 fill 只填入不发送。"
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    check_parser = subparsers.add_parser("check", help="检查环境、依赖和 QQ 窗口")
    check_parser.add_argument("--title-hint", help="QQ 窗口标题提示")
    check_parser.add_argument("--no-connect", action="store_true", help="只列出窗口，不连接激活")
    check_parser.set_defaults(func=command_check)

    inspect_parser = subparsers.add_parser("inspect", help="打印 QQ 控件树摘要")
    inspect_parser.add_argument("--title-hint", help="QQ 窗口标题提示")
    inspect_parser.add_argument("--depth", type=int, default=3, help="控件树深度，默认 3")
    inspect_parser.set_defaults(func=command_inspect)

    fill_parser = subparsers.add_parser("fill", help="打开好友会话并填入消息，不发送")
    add_common_message_args(fill_parser)
    fill_parser.set_defaults(func=command_fill)

    send_parser = subparsers.add_parser("send", help="打开好友会话、填入消息并在确认后发送")
    add_common_message_args(send_parser)
    send_parser.add_argument("--confirm-text", required=True, help="必须等于：发送给<昵称>")
    send_parser.add_argument("--countdown", type=int, default=3, help="发送前倒计时秒数，默认 3")
    send_parser.add_argument("--send-keys", default="{ENTER}", help="发送快捷键，默认 Enter；如需 Ctrl+Enter 可用 ^{ENTER}")
    send_parser.set_defaults(func=command_send)

    send_file_parser = subparsers.add_parser("send-file", help="打开好友会话、粘贴文件并在确认后发送")
    add_common_target_args(send_file_parser)
    send_file_parser.add_argument("--file", required=True, help="要发送的本地文件路径")
    send_file_parser.add_argument("--confirm-text", required=True, help="必须等于：发送文件给<昵称>")
    send_file_parser.add_argument("--countdown", type=int, default=3, help="发送前倒计时秒数，默认 3")
    send_file_parser.add_argument("--send-keys", default="{ENTER}", help="发送快捷键，默认 Enter；如需 Ctrl+Enter 可用 ^{ENTER}")
    send_file_parser.set_defaults(func=command_send_file)

    return parser


def main(argv: Optional[list[str]] = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    return int(args.func(args))


if __name__ == "__main__":
    raise SystemExit(main())