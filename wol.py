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
separated_mac_regex = "[0-9a-f]{2}([-:])[0-9a-f]{2}(\\1[0-9a-f]{2}){4}$"
unseparated_mac_regex = "[0-9a-f]{12}"

broadcast = ['192.168.1.255', '192.168.0.255']
wol_port = 9
known_computers = {
    'mercury': '00:1C:55:35:12:BF',
    'venus': '00:1d:39:55:5c:df',
    'earth': '00:10:60:15:97:fb',
    'mars': '00:10:DC:34:B2:87'}


'''
    Changelog:
    2014-12-19 (Eric Light):  Added logic & regular expressions to confirm user-provided strings are valid MACs
    2014-12-15 (Eric Light):  Removed manual argument parsing, and changed to ArgumentParser
    2014-12-15 (Eric Light):  Re-wrote to conform with PEP-8 and Python3
    2014-12-15 (San Bergmans):  Original from http://www.sbprojects.com/projects/raspberrypi/wol.php

'''

from struct import pack
import socket
from re import match
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


def parse_arguments(printHelp=False):
    """
    Performs basic startup functions, including checking for root, checking arguments, etc
    """

    parser = ArgumentParser(description="Sends a Wake-On-LAN Packet to a given set of MAC addresses or host names",
                            epilog="A MAC address must be in the form of either a 12-digit hexadecimal string, "
                                   "or a 17-digit hexadecimal string separated by either : or - characters.")
    parser.add_argument('-v', '--verbose', action='count', help="print more detailed progress messages")
    parser.add_argument('--version', action='version', version='WoL version %s' % __version__)
    parser.add_argument('target_macs', nargs='+', help='a space-delimited list of MAC addresses to wake')

    if printHelp:
        parser.print_help()
        exit("\nError:  Poorly-formatted MAC address.")

    return parser.parse_args()


def mac_is_ok(mac_to_check):
    """
    Checks the length and contents of a given string to confirm it is a valid format for a MAC address

    Returns False if the string is not 12 or 17 characters long
    Returns False if a 17-character string does not contain either 5 colons or 5 hyphens
    Returns False if the string does not match the expected regex
    Otherwise, returns True, indicating a valid MAC address

    """

    #Ensure the length of the MAC is correct
    if (len(mac_to_check) != 12) and (len(mac_to_check) != 17):
        print("Provided MAC %s is an incorrect length - %s characters long" % (mac_to_check, len(mac_to_check)))
        return False

    # Check the 17-character case first, because it has the more restrictive regex
    if len(target_mac) == 17:

        # use re.findall to count the colons and hyphens in the given MAC
        from re import findall
        colons = len(findall(":", mac_to_check))
        hyphens = len(findall("-", mac_to_check))

        # A separated MAC must contain either exactly 5 colons and 0 hyphens, OR exactly 5 hyphens and 0 colons
        if not (colons == 5 and hyphens == 0) ^ (hyphens == 5 and colons == 0):
            print("%s incorrectly separated; found %s hyphens and %s colons" % (mac_to_check, hyphens, colons))
            return False

        # Length and separators look okay; now we need to check against the regex
        if not (match(separated_mac_regex, target_mac)):
            print("Failed regex")
            return False

    # Check any 12-character cases.  This is quite simple because we just need the regex to clear
    if len(target_mac) == 12:
        if not (match(unseparated_mac_regex, target_mac)):
            print("Failed regex")
            return False

    # If we get here, mac_to_check has passed all the tests, so it's probably a well-formed MAC address
    return True


if __name__ == "__main__":
    cli_args = parse_arguments()

    # Check each provided argument to ensure it's a correctly-formatted MAC address
    for target_mac in cli_args.target_macs:

        if mac_is_ok(target_mac):
            print("MAC looks OK, waking up %s" % target_mac)
        else:
            parse_arguments(printHelp=True)

        exit()


"""
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
"""