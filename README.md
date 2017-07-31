# Crapture

A hackish automated window recorder.


## Features

 - Screenplay driven. You don't have to worry about typing errors, timings or reproducibility
 - Optimized gif output


## Example screenplay

```jinja
echo 'Hello world!'
{{ sleep 3 }}cmatrix
{{ sleep 4 }}q{{ sleep 1 }}echo 'Goodbyz{{ sleep 0.2 }}{{ backspace }}e plane{{ sleep 0.5 }}{{ control w }}world!'
{{ sleep 4 }}
```

![Example screencast](docs/images/screencast.gif)

GIF size: 143K


## Usage

```
$ python crapture.py your.screenplay -o x.gif
[Select a window to start capture]
...
```

Crapture requires a screenplay file as input which describes the recording. This file is
a simple text file with the following additions:
 - `{{ sleep N }}`: sleep N seconds (integers and floats are accepted)
 - `{{ list of keys }}`: press keys combinations. (Example: `{{ control l }}` clears screen in terminal)

Any other string will be typed letter by letter to the target window.


## Requirements

 - byzanz desktop recorder (https://linux.die.net/man/1/byzanz-record)
 - xwinfo command
 - python


## Setup

```
git clone https://github.com/asciimoo/scrapture
cd scrapture
virtualenv env
source env/bin/activate
pip install -r requirements.txt
```
