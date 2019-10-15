"""
Inspired by
https://gitlab.com/smiley1983/halite3-match-manager/blob/master/keyboard_detection.py

#TODO: test on Windows
"""
import sys
import os

if os.name == 'nt':
    import msvcrt
else:
    import termios
    from select import select


class KeyboardStop(Exception):
    pass


class KeyboardMonitor:
    """
    Use in a with statement to enable the appropriate terminal mode to detect keyboard presses
    without blocking for input.  The resulting function can be called any number of times
    until a keypress is detected.  Sample code:

    ```
    with KeyboardMonitor() as key_pressed:
        while key_pressed() != 'q':
            sys.stdout.write('.')
            sys.stdout.flush()
            sleep(0.5)
    ```

    NOTE: Special return values can be seen in KeyboardMonitor.translate.keys()

    Upon exiting the with code block, the terminal is reverted to its calling (normal) state.
    The sys.stdout.flush() is important when in the keyboard detection mode; otherwise, text
    output won't be seen.
    """
    translate = {
        'TAB':b'\t', 'ESC':b'\x1b',
        'F1':b'\x1bOP', 'F2':b'\x1bOQ',
        'F3':b'\x1bOR', 'F4':b'\x1bOS',
        'F5':b'\x1b[15~', 'F6':b'\x1b[17~',
        'F7':b'\x1b[18~', 'F8':b'\x1b[19~',
        'F9':b'\x1b[20~', 'F10':b'\x1b[21~',
        'F11':b'\x1b[23~\x1b', 'F12':b'\x1b[24~\x08',
    }
    rev_trans = {v:k for k,v in translate.items()}

    def __enter__(self):
        if os.name == 'nt':
            return self.query_keyboard

        # save the terminal settings
        self.fd = sys.stdin.fileno()
        self.new_term = termios.tcgetattr(self.fd)
        self.old_term = termios.tcgetattr(self.fd)

        # new terminal setting unbuffered
        self.new_term[3] = (self.new_term[3] & ~termios.ICANON & ~termios.ECHO)

        # switch to unbuffered terminal
        termios.tcsetattr(self.fd, termios.TCSAFLUSH, self.new_term)

        return self.query_keyboard

    def __exit__(self, type, value, traceback):
        if os.name == 'nt':
            return

        # swith to normal terminal
        termios.tcsetattr(self.fd, termios.TCSAFLUSH, self.old_term)

    def query_keyboard(self):
        key = '' if os.name == 'nt' else bytes(0)

        while True:  # read all input bytes
            read = None
            if os.name == 'nt':
                read = msvcrt.getch().decode('utf-8') or None
            else:
                dr, dw, de = select([sys.stdin], [], [], 0)
                if dr:
                    read = os.read(sys.stdin.fileno(), 1)
            if read is None:  # no more input
                break
            key += read  # concatenate input bytes

        if key == b'':  # no keys pressed
            rv = 'None'
        elif key in self.rev_trans.keys():  # special return value
            rv = self.rev_trans[key]
        elif key != b'':  # non empty (likely just a standard key)
            try:
                rv = key.decode('utf-8')
            except AttributeError as e:
                rv = str(key)
        else:
            raise TypeError(f"key `{key}` of type `{type(key)}` is not supported")
        # print('key:', key, 'rv:', rv)
        return rv or 'None'


if __name__ == '__main__':
    from time import sleep

    with KeyboardMonitor() as key_pressed:
        print('press `q`')
        while not key_pressed() == 'q':
            sys.stdout.write('.')
            sys.stdout.flush()
            sleep(0.5)

    with KeyboardMonitor() as key_pressed:
        print('press `[` or `<`')
        while not key_pressed() in '[<':
            sys.stdout.write('.')
            sys.stdout.flush()
            sleep(0.5)

    with KeyboardMonitor() as key_pressed:
        print('press `TAB`')
        with KeyboardMonitor() as kp:
            while kp() != 'TAB':
                sys.stdout.write('T')
                sys.stdout.flush()
                sleep(0.5)
        print('press `ESC`')
        while kp() != 'ESC':
            sys.stdout.write('X')
            sys.stdout.flush()
            sleep(0.5)

    print('done')
