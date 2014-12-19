#!/usr/bin/python3

__author__ = 'Eric Light'
__copyright__ = "Copyleft 2014, Eric Light"
__license__ = "GPLv3"
__version__ = "2014-12-19 (v0.9)"
__maintainer__ = "Eric Light"
__credits__ = "Original written by San Bergmans, www.sbprojects.com"
__email__ = "eric@ericlight.com"
__status__ = "Production"


MAC_REGEX = "[0-9a-f]{12}"
BROADCAST = ['192.168.111.255']
UDP_PORT = 9

# TODO - Load BROADCAST with appropriate broadcast addresses for all IP addresses on the current computer
# TODO - Make broadcast IP's specified at command-line work
'''
    Changelog:
    2014-12-19 (Eric Light):  Split structure out into functions; added commenting
    2014-12-19 (Eric Light):  Removed 'known computers' functionality, merged broadcast functionality back in
    2014-12-19 (Eric Light):  Added logic & regular expressions to confirm user-provided strings are valid MACs
    2014-12-15 (Eric Light):  Removed manual argument parsing, and changed to ArgumentParser
    2014-12-15 (Eric Light):  Re-wrote to comply with PEP-8 and Python3
    2014-12-15 (San Bergmans):  Original from http://www.sbprojects.com/projects/raspberrypi/wol.php

'''

from argparse import ArgumentParser


def build_magic_packet(ethernet_address):
    """
    Constructs the magic packet to wake the target machine.

    A magic packet consists of six \xff bytes, followed by sixteen repetitions of the target mac address.

    Returns the magic packet for the target machine, prepared for sending
    """


    # Split ethernet_address into a list of 6x bytes
    from struct import pack

    # The following terrible line does the following:
    # - Splits the ethernet_address string out into a list of six byte-like strings
    # - Packs these byte-like strings into a list of actual bytes
    # - Joins this list of bytes together into a single byte string, with the format b'\xnn...'
    hardware_address = b''.join([pack('B', int(i,16)) for i in [ethernet_address[i:i+2] for i in range(0, len(ethernet_address), 2)]])

    # Return magic packet
    return b'\xff' * 6 + hardware_address * 16


def send_wol_message(wol_message):
    """
    Sends the magic packet to every broadcast address in the BROADCAST list, using socket.sendto()
    """


    # Send packet to broadcast address using UDP port 9
    import socket

    # Set up the network socket
    soc = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    soc.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)

    # Sent the magic packet via every item in the BROADCAST list
    for source_ip in BROADCAST:
        soc.sendto(wol_message, (source_ip, UDP_PORT))
    soc.close()


def parse_arguments():
    """
    Parses arguments, returns version if appropriate, otherwise returns a list of arguments
    """

    parser = ArgumentParser(description="Sends a Wake-On-LAN Packet to a given set of MAC addresses or host names",
                            epilog="A MAC address must be in the form of either a 12-digit hexadecimal string, "
                                   "or a 17-digit hexadecimal string separated by either : or - characters.")
    parser.add_argument('-v', '--verbose', action='count', help="print more detailed progress messages")
    parser.add_argument('--version', action='version', version='WoL version %s' % __version__)
    parser.add_argument('-b', dest='broadcast', help='specify a broadcast address. '
                                                     'Defaults to %(default)s', default=BROADCAST)
    parser.add_argument('target_macs', nargs='+', help='a space-delimited list of MAC addresses to wake')

    return parser.parse_args()


def mac_is_ok(mac_to_check):
    """
    Checks the length and contents of a given string to confirm it is a valid format for a MAC address

    Expects to receive a hexadecimal string, 12 characters long, with no separators (e.g. colons or hyphens)

    Returns False if the string is not 12 characters long
    Returns False if the string does not match the expected regex
    Otherwise, returns True, indicating a valid MAC address

    """

    #Ensure the length of the MAC is correct
    if len(mac_to_check) != 12:
        print("Provided MAC %s is an incorrect length - %s characters long" % (mac_to_check, len(mac_to_check)))
        return False

    # Check MAC against regex
    from re import match
    if not (match(MAC_REGEX, mac_to_check)):
        print("Failed regex")
        return False

    # If we get here, mac_to_check is a 12-digit hexadecimal number, so it's probably a well-formed MAC address
    return True


def remove_separators(mac):
    """
    Takes a MAC address, and returns the same string without separator characters : or -
    """

    mac = mac.replace(":", "")
    mac = mac.replace("-", "")
    return mac


if __name__ == "__main__":
    cli_args = parse_arguments()
    #TODO - parse cli_args.broadcast here

    # Check each provided argument to ensure it's a correctly-formatted MAC address
    for target_mac in cli_args.target_macs:

        # Strip out separators : or -, and convert to lower case
        stripped_mac = remove_separators(target_mac.lower())

        # Check the MAC against a regular expression (MAC_REGEX) to confirm that it's actually a valid format
        if mac_is_ok(stripped_mac):
            print("Sending magic packet to %s." % stripped_mac)
            # Construct the magic packet with the MAC address
            magic_packet = build_magic_packet(stripped_mac)

            # Push the magic packet out onto the broadcast IP
            send_wol_message(magic_packet)

        else:
            print("%s does not look like a valid MAC address; skipping." % target_mac)