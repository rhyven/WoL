#!/usr/bin/python3

"""
Warning - You probably shouldn't use this.  It's really hacky, and I've only briefly thrown it together.
"""

__author__ = 'Eric Light'
__copyright__ = "Copyleft 2014, Eric Light"
__license__ = "GPLv3"
__version__ = "2014-12-22 (v0.1)"
__maintainer__ = "Eric Light"
__email__ = "eric@ericlight.com"
__status__ = "Production"

try:
    from flask import Flask
except ImportError:
    exit("You need to install Flask first; try running:  sudo apt-get install python3-flask")

computers = {'Sue': '74:D0:2B:C5:9C:F5', 'Eric': 'F4:6D:04:65:4E:F7', 'Brendon': '14:DA:E9:72:D7:CD',
             'Claire': '60:A4:4C:61:7E:19', 'Gravity': '14:DA:E9:9D:0D:E5', 'Russell': 'F4:6D:04:0C:46:B1',
             'Steve': '74:D0:2B:26:5A:0C', 'Debbie': '08:60:6E:F2:7D:E3', 'Robert': '54:04:A6:A4:69:45',
             'Christine': '74:D4:35:0E:DA:A9', 'Trish': '48:5B:39:21:AE:F6', 'Ben': '74:D4:35:0E:DA:A5',
             'Peter': '10:C3:7B:92:5A:B3', 'Larry': 'D8:50:E6:DB:05:BE', 'ST-Terminal': '48:5B:39:2C:E2:57',
             'George': 'F4:6D:04:65:4E:EE', 'Kyle': '60:A4:4C:62:82:87', 'Paul': 'C8:60:00:9B:6C:29'}

HTML_HEAD = "<!DOCTYPE html><head><title>Wake a Computer</title></head>"
HTML_TAIL = "</body></html>"

app = Flask(__name__)

@app.route("/")
def hello():
    return_msg = HTML_HEAD + "<h1>Click the PC name that you would like to wake.</h1><table>"

    for computer in sorted(computers):
        return_msg += "<tr><td><a href='./%s'>%s</a></td></tr>" % (computer, computer)
    return_msg += "</table>" + HTML_TAIL

    return return_msg


@app.route("/<computername>")
def wake(computername):
    from wol import WakeOnLan
    WakeOnLan(computers[computername])
    return_msg = HTML_HEAD + "<h1>Wake-on-LAN</h1>"
    return_msg += "<p>A Wake-up request has been sent to %s at %s</p>" % (computername, computers[computername])
    return_msg += "<p>It usually takes a few minutes to wake a computer; " \
                  "if it takes more than five minutes, try again.</p>" + HTML_TAIL

    return return_msg

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=81)

