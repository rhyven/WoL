#!/usr/bin/python3

__author__ = 'Eric Light'
__copyright__ = "Copyleft 2014, Eric Light"
__license__ = "GPLv3"
__version__ = "2014-12-15 (v0.9)"
__maintainer__ = "Eric Light"
__credits__ = "Original written by San Bergmans, www.sbprojects.com"
__email__ = "eric@ericlight.com"
__status__ = "Production"



# wol
#
# Wake on LAN
#
# Use:
# wol computer1
# wol computer1 computer2
# wol 00:11:22:33:44:55
#
# Configuration variables
broadcast = ['192.168.1.255', '192.168.0.255']
wol_port = 9
known_computers = {
    'mercury': '00:1C:55:35:12:BF',
    'venus': '00:1d:39:55:5c:df',
    'earth': '00:10:60:15:97:fb',
    'mars': '00:10:DC:34:B2:87'}


'''
    Changelog:
    2014-12-15 (Eric Light):  Removed manual argument parsing, and changed to ArgumentParser
    2014-12-15 (Eric Light):  Re-wrote to conform with PEP-8 and Python3
    2014-12-15 (San Bergmans):  Original from http://www.sbprojects.com/projects/raspberrypi/wol.php

'''

from struct import pack
import socket
from sys import argv
from argparse import ArgumentParser


def wake_on_lan(ethernet_address):

    # Construct 6 byte hardware address
    add_oct = ethernet_address.split(':')
    if len(add_oct) != 6:
        print("\n*** Illegal MAC address\n")
        print("MAC should be written as 00:11:22:33:44:55\n")
        return

    hwa = pack('BBBBBB', int(add_oct[0], 16),
               int(add_oct[1], 16),
               int(add_oct[2], 16),
               int(add_oct[3], 16),
               int(add_oct[4], 16),
               int(add_oct[5], 16))

    # Build magic packet

    msg = '\xff' * 6 + hwa * 16

    # Send packet to broadcast address using UDP port 9

    soc = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    soc.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
    for i in broadcast:
        soc.sendto(msg, (i, wol_port))
    soc.close()


def parse_arguments():
    """
    Performs basic startup functions, including checking for root, checking arguments, etc
    """

    parser = ArgumentParser(description="Sends a Wake-On-LAN Packet to a given set of MAC addresses or host names")
    parser.add_argument('-v', '--verbose', action='count', help="print more detailed progress messages")
    parser.add_argument('--version', action='version', version='WoL version %s' % __version__)
    parser.add_argument('target_macs', nargs='+', help='a space-delimited list of MAC addresses to wake')

    return parser.parse_args()


if __name__ == "__main__":
    cli_args = parse_arguments()

if len(argv) == 1:
    print("\n*** No computer given to power up\n")
    print("Use: 'wol computername' or 'wol 00:11:22:33:44:55'")

else:
    for i in argv:
        if i[0] != '/':
            if ":" in i:
                # Wake up using MAC address
                wake_on_lan(i)
            else:
                # Wake up known computers
                if i in known_computers:
                    wake_on_lan(known_computers[i])
                else:
                    print("\n*** Unknown computer " + i + "\n")
                    quit()

    if len(argv) == 2:
        print("\nDone! The computer should be up and running in a short while.")
    else:
        print("\nDone! The computers should be up and running in a short while.")
    print()
