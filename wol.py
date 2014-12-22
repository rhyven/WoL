#!/usr/bin/python3

__author__ = 'Eric Light'
__copyright__ = "Copyleft 2014, Eric Light"
__license__ = "GPLv3"
__version__ = "2014-12-20 (v0.9b)"
__maintainer__ = "Eric Light"
__credits__ = "Original written by San Bergmans, www.sbprojects.com\n"
__credits__ += "Ron Collinson <notthinking at gmail dot com>"
__email__ = "eric@ericlight.com"
__status__ = "Production"


MAC_REGEX = "[0-9a-f]{12}"
BROADCAST = ['192.168.111.255']
UDP_PORT = 9

# TODO - Load BROADCAST with appropriate broadcast addresses for all IP addresses on the current computer
# TODO - Make broadcast IP's specified at command-line work
'''
    Changelog:
    2014-12-22 (Eric Light):  Made it into a class, so it can be imported and used elsewhere.
    2014-12-20 (Eric Light):  Updated build_magic_packet to remove ugly hack and replace with Ron Collinson's method
    2014-12-19 (Eric Light):  Split structure out into functions; added commenting
    2014-12-19 (Eric Light):  Removed 'known computers' functionality, merged broadcast functionality back in
    2014-12-19 (Eric Light):  Added logic & regular expressions to confirm user-provided strings are valid MACs
    2014-12-15 (Eric Light):  Removed manual argument parsing, and changed to ArgumentParser
    2014-12-15 (Eric Light):  Re-wrote to comply with PEP-8 and Python3
    2014-12-15 (San Bergmans):  Original from http://www.sbprojects.com/projects/raspberrypi/wol.php

'''


class WakeOnLan:

    def __init__(self, target=None):
        if not target is None:
            print("Waking MAC %s" % target)
            target = self.remove_separators(target)
            if self.mac_is_ok(target):
                print("Target %s seems to be ok; sending magic packet." % target)
                self.send_wol_message(target)
                print("Wake on Lan packet sent to %s" % target)
            else:
                raise ValueError("Validation of the MAC address failed; it doesn't appear to be a valid MAC.")

    def send_wol_message(self, ethernet_address):
        """
        Constructs and broadcasts the magic packet, to wake the target machine.

        A magic packet consists of six \xff bytes, followed by sixteen repetitions of the target mac address.

        """

        # Convert the ethernet_address string into a byte array  (thanks, Ron Collinson!)
        magic_packet = b'\xff' * 6 + bytes(bytearray.fromhex(ethernet_address)) * 16

        # Set up the network socket
        import socket
        soc = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        soc.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)

        # Send the magic packet via every item in the BROADCAST list
        for source_ip in BROADCAST:
            soc.sendto(magic_packet, (source_ip, UDP_PORT))
        soc.close()

    def mac_is_ok(self, mac_to_check):
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

    def remove_separators(self, mac):
        """
        Takes a MAC address, and returns the same string without separator characters : or -
        """

        mac = mac.replace(":", "")
        mac = mac.replace("-", "")
        return mac.lower()


if __name__ == "__main__":

    def parse_arguments():
        """
        Parses arguments, returns version if appropriate, otherwise returns a list of arguments
        """

        from argparse import ArgumentParser

        parser = ArgumentParser(description="Sends a Wake-On-LAN Packet to a given set of MAC addresses or host names",
                                epilog="A MAC address must be in the form of either a 12-digit hexadecimal string, "
                                       "or a 17-digit hexadecimal string separated by either : or - characters.")
        parser.add_argument('-v', '--verbose', action='count', help="print more detailed progress messages")
        parser.add_argument('--version', action='version', version='WoL version %s' % __version__)
        parser.add_argument('-b', dest='broadcast', help='specify a broadcast address. '
                                                         'Defaults to %(default)s', default=BROADCAST)
        parser.add_argument('target_macs', nargs='+', help='a space-delimited list of MAC addresses to wake')

        return parser.parse_args()

    cli_args = parse_arguments()

    app = WakeOnLan()
    #TODO - parse cli_args.broadcast here

    # Check each provided argument to ensure it's a correctly-formatted MAC address
    for target_mac in cli_args.target_macs:

        # Strip out separators : or -, and convert to lower case
        stripped_mac = app.remove_separators(target_mac)

        # Check the MAC against a regular expression (MAC_REGEX) to confirm that it's actually a valid format
        if app.mac_is_ok(stripped_mac):
            print("Sending magic packet to %s." % stripped_mac)
            # Construct the magic packet with the MAC address, and push the magic packet out onto the broadcast IP
            app.send_wol_message(stripped_mac)

        else:
            print("%s does not look like a valid MAC address; skipping." % target_mac)