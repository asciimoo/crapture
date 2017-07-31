import argparse
import re
import threading

from subprocess import check_output
from sys import argv
from time import sleep

from pykeyboard import PyKeyboard


DELAY = 0.10
K = PyKeyboard()


def record(script, output):
    h = w = x = y = None
    dur = duration(script)
    print('[Select a window to start capture]')
    print('[Capture duration: {0} sec]'.format(dur))
    for line in check_output(['xwininfo']).splitlines():
        if 'Absolute upper-left X' in line:
            x = line.split()[-1]
        elif 'Absolute upper-left Y' in line:
            y = line.split()[-1]
        elif 'Width:' in line:
            w = line.split()[-1]
        elif 'Height:' in line:
            h = line.split()[-1]
    sleep(1)
    threading.Thread(target=send_keys, args=(script,)).start()
    check_output(['byzanz-record', '-x', x, '-y', y, '-w', w, '-h', h, '--delay=2', '-d', str(int(dur)), output])


def send_keys(script):
    sleep(1)
    for i in script:
        if isinstance(i, float):
            sleep(i)
        elif isinstance(i, list):
            K.press_keys(i)
        else:
            for c in i:
                K.tap_key(c)
                sleep(DELAY)


def duration(script):
    dur = 0.0
    for i in script:
        if isinstance(i, float):
            dur += i
        elif isinstance(i, str):
            dur += len(i) * DELAY
    return dur


def parse_keys(keys):
    ret = []
    for key in keys:
        if len(key) == 1:
            ret.append(key)
        else:
            ret.append(getattr(K, '{0}_key'.format(key)))
    return ret


def parse_script(script_text):
    script = []
    for piece in re.split("({{[^}]+}}|\n)", script_text, re.U | re.M):
        if piece.startswith('{{') and piece.endswith('}}'):
            args = piece[2:-2].strip().split()
            if not args:
                raise Exception("missing arguments")
            if args[0] == 'sleep':
                if len(args) < 2:
                    raise Exception("missing argument for sleep")
                script.append(float(args[1]))
            else:
                script.append(parse_keys(args))
        else:
            if piece == '\n':
                script.append([K.enter_key])
            else:
                script.append(piece)
    return script


def crapture(script_file, output):
    with open(script_file) as infile:
        script = parse_script(infile.read().rstrip('\n'))
        record(script, output)


def main():
    global DELAY
    parser = argparse.ArgumentParser('Crapture - hackish screen capturing')
    parser.add_argument('-d', '--duration', help='print the duration of the script', action="store_true")
    parser.add_argument('-t', '--typing-delay', help='Delay between typing two letters', default=DELAY)
    parser.add_argument('-o', '--output', help='Output gif name', default='craptured.gif')
    parser.add_argument('script', help='script of the recording')
    args = parser.parse_args()
    script = args.script
    DELAY = args.typing_delay
    if args.duration:
        print('Duration of the script is: {0}s'.format(duration(script)))
    else:
        crapture(script, args.output)


if __name__ == '__main__':
    main()
