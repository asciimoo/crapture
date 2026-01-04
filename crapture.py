import argparse
import re
import shlex
import threading

from subprocess import check_output, Popen
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
INITIAL_DELAY = 1
DURATION = 0.0
K = PyKeyboard()


class CMD():
    def __init__(self, args, method):
        self.args = args
        self.method = method

    def evaluate(self):
        for i, arg in enumerate(self.args):
            if arg == '$$DURATION':
                self.args[i] = str(DURATION)
        print("executing", ' '.join(self.args))
        if self.method == 'exec':
            print(str(check_output(self.args)))
        if self.method == 'fork':
            Popen(self.args)


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
    cmd = ['byzanz-record', '-x', x, '-y', y, '-w', w, '-h', h, '--delay='+str(1+int(INITIAL_DELAY)), '-d', str(int(dur)), output]
    print("Executing", ' '.join(map(lambda x: x.decode("utf-8") if type(x) == bytes else x, cmd)))
    check_output(cmd)


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
            key = key.replace("ctrl", "control")
            ret.append(getattr(K, '{0}_key'.format(key)))
    return ret


def parse_script(script_file):
    with open(script_file) as infile:
        script_text = infile.read().rstrip('\n')
    script = []
    for piece in re.split("({{[^}]+}}|\n)", script_text, flags=re.U | re.M):
        if piece.startswith('{{') and piece.endswith('}}'):
            args = shlex.split(piece[2:-2].strip())
            if not args:
                raise Exception("missing arguments")
            if args[0] == 'sleep':
                if len(args) != 2:
                    raise Exception("missing argument for sleep")
                script.append(float(args[1]))
            elif args[0] in ('exec', 'fork'):
                script.append(CMD(args[1:], args[0]))
            else:
                try:
                    script.append(parse_keys(args))
                except:
                    print('[!] Failed to parse %r' % piece)
                    exit(3)
        else:
            if piece == '\n':
                script.append([K.enter_key])
            else:
                script.append(piece)
    return script


def crapture(script, output):
    try:
        record(script, output)
    except Exception as e:
        print('[!] Error', e)
        print_exc()
        exit(2)



def main():
    global DELAY, INITIAL_DELAY, DURATION
    parser = argparse.ArgumentParser('Crapture - hackish screen capturing')
    parser.add_argument('-d', '--duration', help='print the duration of the script', action="store_true")
    parser.add_argument('-t', '--typing-delay', help='Delay between typing two letters (float, in seconds)', default=DELAY, type=float)
    parser.add_argument('-o', '--output', help='Output gif name', default='craptured.gif')
    parser.add_argument('-n', '--norecord', help='Do not record', action="store_true")
    parser.add_argument('-i', '--initial-delay', help='Initial delay before starting capture (int, in seconds)', default=INITIAL_DELAY, type=int)
    parser.add_argument('script', help='script of the recording')
    args = parser.parse_args()
    script = parse_script(args.script)
    DELAY = args.typing_delay
    INITIAL_DELAY = int(args.initial_delay)
    DURATION = duration(script)
    print(DURATION)
    if args.duration:
        print('Duration of the script is: {0}s'.format(DURATION))
    elif args.norecord:
        input("[!] Press enter to start capturing in %f seconds\n" % INITIAL_DELAY)
        send_keys(script)
    else:
        crapture(script, args.output)


if __name__ == '__main__':
    main()
