#!/usr/bin/env python3
import sys
import time
#import json


# Globals
LOG_F = "/root/public/exabgp/bgp_msg"



# main
if __name__ == "__main__":

    while True:
        try:
            # Parse BGP messages
            line = sys.stdin.readline().strip()
#            bgp_msg = json.loads(line)

#            with open(LOG_F, 'w') as f:
#                f.write(line)

            time.sleep(1)

        except KeyboardInterrupt:
            sys.exit(1)

        # most likely a signal during readline
        except IOError:
            sys.exit(1)
