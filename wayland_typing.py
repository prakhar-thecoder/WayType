import time
from evdev import UInput, ecodes as e

import config

CHAR_MAP = {
    'a': e.KEY_A, 'b': e.KEY_B, 'c': e.KEY_C, 'd': e.KEY_D, 'e': e.KEY_E,
    'f': e.KEY_F, 'g': e.KEY_G, 'h': e.KEY_H, 'i': e.KEY_I, 'j': e.KEY_J,
    'k': e.KEY_K, 'l': e.KEY_L, 'm': e.KEY_M, 'n': e.KEY_N, 'o': e.KEY_O,
    'p': e.KEY_P, 'q': e.KEY_Q, 'r': e.KEY_R, 's': e.KEY_S, 't': e.KEY_T,
    'u': e.KEY_U, 'v': e.KEY_V, 'w': e.KEY_W, 'x': e.KEY_X, 'y': e.KEY_Y,
    'z': e.KEY_Z,
    '1': e.KEY_1, '2': e.KEY_2, '3': e.KEY_3, '4': e.KEY_4, '5': e.KEY_5,
    '6': e.KEY_6, '7': e.KEY_7, '8': e.KEY_8, '9': e.KEY_9, '0': e.KEY_0,
    ' ': e.KEY_SPACE, '\t': e.KEY_TAB, '\n': e.KEY_ENTER,
    ',': e.KEY_COMMA, '.': e.KEY_DOT, '/': e.KEY_SLASH, ';': e.KEY_SEMICOLON,
    "'": e.KEY_APOSTROPHE, '[': e.KEY_LEFTBRACE, ']': e.KEY_RIGHTBRACE,
    '\\': e.KEY_BACKSLASH, '-': e.KEY_MINUS, '=': e.KEY_EQUAL, '`': e.KEY_GRAVE
}

SHIFT_MAP = {
    'A': e.KEY_A, 'B': e.KEY_B, 'C': e.KEY_C, 'D': e.KEY_D, 'E': e.KEY_E,
    'F': e.KEY_F, 'G': e.KEY_G, 'H': e.KEY_H, 'I': e.KEY_I, 'J': e.KEY_J,
    'K': e.KEY_K, 'L': e.KEY_L, 'M': e.KEY_M, 'N': e.KEY_N, 'O': e.KEY_O,
    'P': e.KEY_P, 'Q': e.KEY_Q, 'R': e.KEY_R, 'S': e.KEY_S, 'T': e.KEY_T,
    'U': e.KEY_U, 'V': e.KEY_V, 'W': e.KEY_W, 'X': e.KEY_X, 'Y': e.KEY_Y,
    'Z': e.KEY_Z,
    '!': e.KEY_1, '@': e.KEY_2, '#': e.KEY_3, '$': e.KEY_4, '%': e.KEY_5,
    '^': e.KEY_6, '&': e.KEY_7, '*': e.KEY_8, '(': e.KEY_9, ')': e.KEY_0,
    '_': e.KEY_MINUS, '+': e.KEY_EQUAL, '{': e.KEY_LEFTBRACE, '}': e.KEY_RIGHTBRACE,
    '|': e.KEY_BACKSLASH, ':': e.KEY_SEMICOLON, '"': e.KEY_APOSTROPHE,
    '<': e.KEY_COMMA, '>': e.KEY_DOT, '?': e.KEY_SLASH, '~': e.KEY_GRAVE
}

def type_text(text: str) -> None:
    if not text:
        return

    delay = config.TYPING_DELAY_MS / 1000.0

    try:
        with UInput() as ui:
            # Short pause to let window context settle if needed
            time.sleep(0.1)
            for char in text:
                if char in CHAR_MAP:
                    keycode = CHAR_MAP[char]
                    ui.write(e.EV_KEY, keycode, 1)  # press
                    ui.write(e.EV_KEY, keycode, 0)  # release
                    ui.syn()
                elif char in SHIFT_MAP:
                    keycode = SHIFT_MAP[char]
                    ui.write(e.EV_KEY, e.KEY_LEFTSHIFT, 1)
                    ui.write(e.EV_KEY, keycode, 1)
                    ui.syn()

                    time.sleep(0.005)

                    ui.write(e.EV_KEY, keycode, 0)
                    ui.syn()

                    time.sleep(0.005)

                    ui.write(e.EV_KEY, e.KEY_LEFTSHIFT, 0)
                    ui.syn()
                else:
                    # Ignore unknown characters or type a space?
                    pass
                if delay > 0:
                    time.sleep(delay)
    except Exception as exc:
        print(f"[Typing] Failed to type text: {exc}", flush=True)


if __name__ == "__main__":
    type_text("Hello Mike, how are you?")
