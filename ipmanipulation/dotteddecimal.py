from __future__ import annotations
import sys
import argparse
from typing import Iterator, Tuple

#!/usr/bin/env python3
"""
dotteddecimal.py

Utilities for working with dotted-decimal IPv4 addresses.

Features:
- Validate dotted-decimal IPv4 strings
- Convert between dotted-decimal and 32-bit integer
- Convert between netmask and CIDR prefix
- Compute network and broadcast addresses for a subnet
- Check membership of an IP in a subnet
- Iterate IPs in a range or subnet

Usage (CLI):
    python3.11 dotteddecimal.py --ip 192.168.1.10 --to int
    python3.11 dotteddecimal.py --int 3232235786 --to ip
    python3.11 dotteddecimal.py --mask 255.255.255.0 --to prefix
    python3.11 dotteddecimal.py --prefix 24 --to mask
    python3.11 dotteddecimal.py --subnet 192.168.1.10/24 --net
    python3.11 dotteddecimal.py --start 192.168.1.1 --end 192.168.1.10
"""



def validate_ip(ip: str) -> bool:
        """Return True if ip is a valid dotted-decimal IPv4 address."""
        parts = ip.split('.')
        if len(parts) != 4:
                return False
        for p in parts:
                if not p.isdigit():
                        return False
                if p[0] == '0' and len(p) > 1:  # allow "0" but not "01"
                        # Leading zeros are generally accepted in dotted notation but
                        # can be ambiguous; disallow to keep things explicit.
                        return False
                n = int(p)
                if n < 0 or n > 255:
                        return False
        return True


def ip_to_int(ip: str) -> int:
        """Convert dotted-decimal IP to 32-bit integer. Raises ValueError on bad input."""
        if not validate_ip(ip):
                raise ValueError(f"Invalid IPv4 address: {ip!r}")
        parts = [int(p) for p in ip.split('.')]
        n = (parts[0] << 24) | (parts[1] << 16) | (parts[2] << 8) | parts[3]
        return n


def int_to_ip(n: int) -> str:
        """Convert 32-bit integer to dotted-decimal IP. Raises ValueError for out-of-range."""
        if not (0 <= n <= 0xFFFFFFFF):
                raise ValueError(f"Integer out of IPv4 range: {n}")
        return f"{(n >> 24) & 0xFF}.{(n >> 16) & 0xFF}.{(n >> 8) & 0xFF}.{n & 0xFF}"


def prefix_to_netmask(prefix: int) -> str:
        """Convert CIDR prefix (0-32) to dotted-decimal netmask."""
        if not (0 <= prefix <= 32):
                raise ValueError(f"Prefix must be between 0 and 32: {prefix}")
        mask = (0xFFFFFFFF << (32 - prefix)) & 0xFFFFFFFF
        return int_to_ip(mask)


def netmask_to_prefix(mask: str) -> int:
        """Convert dotted-decimal netmask to CIDR prefix. Raises ValueError if mask is invalid."""
        if not validate_ip(mask):
                raise ValueError(f"Invalid netmask: {mask}")
        m = ip_to_int(mask)
        # Netmask must be contiguous ones followed by zeros.
        if m == 0:
                return 0
        inv = (~m) & 0xFFFFFFFF
        # Check that inv+1 is a power of two (i.e., mask is contiguous)
        if (inv + 1) & inv != 0:
                raise ValueError(f"Non-contiguous netmask: {mask}")
        prefix = m.bit_count()
        return prefix


def split_cidr(cidr: str) -> Tuple[str, int]:
        """Parse 'ip/prefix' and return (ip, prefix)."""
        if '/' not in cidr:
                raise ValueError("CIDR must be in form a.b.c.d/p")
        ip_str, prefix_str = cidr.split('/', 1)
        if not validate_ip(ip_str):
                raise ValueError(f"Invalid IP in CIDR: {ip_str}")
        try:
                prefix = int(prefix_str)
        except ValueError:
                raise ValueError(f"Invalid prefix: {prefix_str}")
        if not (0 <= prefix <= 32):
                raise ValueError(f"Prefix out of range: {prefix}")
        return ip_str, prefix


def network_address(ip: str, prefix: int) -> str:
        """Return network address for given IP and prefix."""
        n = ip_to_int(ip)
        mask = ((0xFFFFFFFF << (32 - prefix)) & 0xFFFFFFFF) if prefix else 0
        net = n & mask
        return int_to_ip(net)


def broadcast_address(ip: str, prefix: int) -> str:
        """Return broadcast address for given IP and prefix."""
        n = ip_to_int(ip)
        mask = ((0xFFFFFFFF << (32 - prefix)) & 0xFFFFFFFF) if prefix else 0
        bc = (n & mask) | (~mask & 0xFFFFFFFF)
        return int_to_ip(bc)


def ip_in_subnet(ip: str, cidr: str) -> bool:
        """Return True if ip is inside the subnet specified by cidr (a.b.c.d/p)."""
        ip_str, prefix = split_cidr(cidr)
        return ip_to_int(ip) & (~0 << (32 - prefix) & 0xFFFFFFFF) == ip_to_int(ip_str) & (~0 << (32 - prefix) & 0xFFFFFFFF)


def iter_range(start: str, end: str) -> Iterator[str]:
        """Yield dotted-decimal IPs from start to end inclusive. Raises ValueError if invalid or start>end."""
        if not validate_ip(start):
                raise ValueError(f"Invalid start IP: {start}")
        if not validate_ip(end):
                raise ValueError(f"Invalid end IP: {end}")
        a = ip_to_int(start)
        b = ip_to_int(end)
        if a > b:
                raise ValueError("Start IP must be <= end IP")
        for x in range(a, b + 1):
                yield int_to_ip(x)


def iter_subnet(cidr: str) -> Iterator[str]:
        """Yield all IPs in the subnet. Use with care for large networks."""
        ip_str, prefix = split_cidr(cidr)
        net = ip_to_int(network_address(ip_str, prefix))
        bc = ip_to_int(broadcast_address(ip_str, prefix))
        for x in range(net, bc + 1):
                yield int_to_ip(x)


def _parse_args(argv):
        p = argparse.ArgumentParser(description="Dotted-decimal IPv4 utilities")
        group = p.add_mutually_exclusive_group(required=True)
        group.add_argument("--ip", help="dotted IP to convert (to int or network ops)")
        group.add_argument("--int", type=int, help="32-bit integer to convert to dotted IP")
        group.add_argument("--mask", help="netmask to convert to prefix")
        group.add_argument("--prefix", type=int, help="prefix length to convert to netmask")
        group.add_argument("--subnet", help="CIDR subnet like 192.168.1.0/24")
        group.add_argument("--start", help="start IP for range (use with --end)")
        p.add_argument("--end", help="end IP for range (inclusive)")
        p.add_argument("--to", choices=["int", "ip", "prefix", "mask", "net", "bc", "list"], default="int",
                                     help="operation to perform")
        return p.parse_args(argv)


def main(argv=None):
        argv = sys.argv[1:] if argv is None else argv
        if not argv:
                print("No arguments provided. Use --help for usage information.", file=sys.stderr)
                return 1
        args = _parse_args(argv)

        try:
                if args.int is not None:
                        if args.to != "ip":
                                print("Only --to ip is meaningful with --int", file=sys.stderr)
                        print(int_to_ip(args.int))
                        return

                if args.ip:
                        if args.to == "int":
                                print(ip_to_int(args.ip))
                        elif args.to == "ip":
                                print(args.ip)
                        elif args.to == "net":
                                # require prefix via --prefix or infer from --mask?
                                print("Use --subnet a.b.c.d/p to get network/broadcast", file=sys.stderr)
                        else:
                                print("Unsupported --to for --ip", file=sys.stderr)
                        return

                if args.mask:
                        if args.to == "prefix":
                                print(netmask_to_prefix(args.mask))
                        else:
                                print("Unsupported --to for --mask", file=sys.stderr)
                        return

                if args.prefix is not None:
                        if args.to == "mask":
                                print(prefix_to_netmask(args.prefix))
                        else:
                                print("Unsupported --to for --prefix", file=sys.stderr)
                        return

                if args.subnet:
                        if args.to in ("net", "bc", "list"):
                                ip_str, prefix = split_cidr(args.subnet)
                                if args.to == "net":
                                        print(network_address(ip_str, prefix))
                                elif args.to == "bc":
                                        print(broadcast_address(ip_str, prefix))
                                else:
                                        # list
                                        for i, ip in enumerate(iter_subnet(args.subnet)):
                                                # avoid printing extremely large outputs
                                                if i and i % 10000 == 0:
                                                        print(f"... printed {i} addresses ...", file=sys.stderr)
                                                print(ip)
                        else:
                                print("Unsupported --to for --subnet", file=sys.stderr)
                        return

                if args.start:
                        if not args.end:
                                print("--end is required with --start", file=sys.stderr)
                                return
                        for ip in iter_range(args.start, args.end):
                                print(ip)
                        return

        except ValueError as e:
                print("Error:", e, file=sys.stderr)
                sys.exit(2)


if __name__ == "__main__":
        main()
        sys.exit(0)