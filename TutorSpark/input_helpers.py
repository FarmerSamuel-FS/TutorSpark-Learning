from __future__ import annotations

import sys


ESC = "\x1b"


def is_back_choice(raw: str) -> bool:
    return raw == ESC or raw.strip().lower() == "esc"


def read_menu_choice(prompt: str) -> str:
    """
    Read a menu choice while allowing Esc to return immediately.

    Normal text input still completes with Enter. In non-interactive contexts
    such as tests, this falls back to regular input().
    """
    if not sys.stdin.isatty():
        return input(prompt).strip()

    try:
        import termios
        import tty
    except ImportError:
        return input(prompt).strip()

    sys.stdout.write(prompt)
    sys.stdout.flush()

    buffer: list[str] = []
    fd = sys.stdin.fileno()
    old_settings = termios.tcgetattr(fd)

    try:
        tty.setcbreak(fd)
        while True:
            char = sys.stdin.read(1)

            if char == ESC:
                sys.stdout.write("\n")
                sys.stdout.flush()
                return ESC
            if char in {"\r", "\n"}:
                sys.stdout.write("\n")
                sys.stdout.flush()
                return "".join(buffer).strip()
            if char == "\x03":
                raise KeyboardInterrupt
            if char == "\x04":
                sys.stdout.write("\n")
                sys.stdout.flush()
                return "".join(buffer).strip()
            if char in {"\x7f", "\b"}:
                if buffer:
                    buffer.pop()
                    sys.stdout.write("\b \b")
                    sys.stdout.flush()
                continue
            if char.isprintable():
                buffer.append(char)
                sys.stdout.write(char)
                sys.stdout.flush()
    finally:
        termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
