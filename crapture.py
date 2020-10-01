import argparse
import re
import shlex
import threading

from subprocess import check_output
from sys import argv
from time import sleep
from traceback import print_exc
try:
    from shutil import which
except:
    from distutils.spawn import find_executable as which

try:
    from pykeyboard import PyKeyboard
except:
    print('[!] Missing dependency\nRun `pip install -r requirements.txt` to install missing dependencies')
    exit(1)


DELAY = 0.10
INITIAL_DELAY = 1.0
K = PyKeyboard()


class CMD():
    def __init__(self, args):
        self.args = args

    def evaluate(self):
        print("executing", ' '.join(self.args))
        print(str(check_output(self.args)))


def record(script, output):
    if not which("byzanz-record"):
        raise Exception('[!] Missing command: byzanz-record. Please install it to be able to record')
    if not which("xwininfo"):
        raise Exception('[!] Missing command: xwininfo. Please install it to be able to record')
    h = w = x = y = None
    dur = duration(script)
    print('[Select a window to start capture]')
    print('[Capture duration: {0} sec]'.format(dur))
    for line in check_output(['xwininfo']).splitlines():
        if b'Absolute upper-left X' in line:
            x = line.split()[-1]
        elif b'Absolute upper-left Y' in line:
            y = line.split()[-1]
        elif b'Width:' in line:
            w = line.split()[-1]
        elif b'Height:' in line:
            h = line.split()[-1]
    sleep(1)
    threading.Thread(target=send_keys, args=(script,)).start()
    check_output(['byzanz-record', '-x', x, '-y', y, '-w', w, '-h', h, '--delay='+(0.5+INITIAL_DELAY), '-d', str(int(dur)), output])


def send_keys(script):
    sleep(INITIAL_DELAY)
    for i in script:
        if isinstance(i, float):
            sleep(i)
        elif isinstance(i, list):
            K.press_keys(i)
        elif isinstance(i, CMD):
            i.evaluate()
        else:
            for c in i:
                K.type_string(c)
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


def parse_script(script_file):
    with open(script_file) as infile:
        script_text = infile.read().rstrip('\n')
    script = []
    for piece in re.split("({{[^}]+}}|\n)", script_text, re.U | re.M):
        if piece.startswith('{{') and piece.endswith('}}'):
            args = shlex.split(piece[2:-2].strip())
            if not args:
                raise Exception("Missing arguments")
            if args[0] == 'sleep':
                if len(args) != 2:
                    raise Exception("Missing argument for sleep")
                script.append(float(args[1]))
            elif args[0] == 'exec':
                script.append(CMD(args[1:]))
            else:
                script.append(parse_keys(args))
        else:
            if piece == '\n':
                script.append([K.enter_key])
            else:
                script.append(piece)
    return script


def crapture(script_file, output):
    try:
        script = parse_script(script_file)
        record(script, output)
    except Exception as e:
        print('[!] Error', e)
        print_exc()
        exit(2)



def main():
    global DELAY, INITIAL_DELAY
    parser = argparse.ArgumentParser('Crapture - hackish screen capturing')
    parser.add_argument('-d', '--duration', help='print the duration of the script', action="store_true")
    parser.add_argument('-t', '--typing-delay', help='Delay between typing two letters (float, in seconds)', default=DELAY)
    parser.add_argument('-o', '--output', help='Output gif name', default='craptured.gif')
    parser.add_argument('-n', '--norecord', help='Do not record', action="store_true")
    parser.add_argument('-i', '--initial-delay', help='Initial delay before starting capture (float, in seconds)', default=INITIAL_DELAY)
    parser.add_argument('script', help='script of the recording')
    args = parser.parse_args()
    script = args.script
    DELAY = args.typing_delay
    INITIAL_DELAY = args.initial_delay
    if args.duration:
        print('Duration of the script is: {0}s'.format(duration(script)))
    elif args.norecord:
        input("[!] Press enter to start capturing in %f seconds\n" % INITIAL_DELAY)
        send_keys(parse_script(script))
    else:
        crapture(script, args.output)


if __name__ == '__main__':
    main()
