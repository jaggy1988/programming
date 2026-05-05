import sys
import ipaddress
from typing import Optional, Tuple, Any

#!/usr/bin/env python3
"""
lpm.py - simple Longest Prefix Match for IPv4 prefixes.

Usage:
    - Create an IPTrie and insert prefixes (CIDR) with optional values.
    - Call lookup(ip) to get the best matching network and associated value.

Command-line:
    python lpm.py prefixes.txt
    where prefixes.txt contains lines like:
        10.0.0.0/8    netA
        10.1.0.0/16   netB

Then type IPs on stdin (one per line) to query matches.
"""



class _Node:
        __slots__ = ("child0", "child1", "value", "network")

        def __init__(self):
                self.child0: Optional["_Node"] = None
                self.child1: Optional["_Node"] = None
                self.value: Any = None
                self.network: Optional[ipaddress.IPv4Network] = None


class IPTrie:
        def __init__(self):
                self.root = _Node()

        def insert(self, cidr: str, value: Any = None) -> None:
                """
                Insert a CIDR prefix (e.g. "192.168.0.0/16") with an optional value.
                If value is omitted, the prefix string itself will be stored.
                """
                net = ipaddress.ip_network(cidr, strict=False)
                if net.version != 4:
                        raise ValueError("only IPv4 is supported")
                bits = _int_to_bits(int(net.network_address), 32)
                node = self.root
                for i in range(net.prefixlen):
                        if bits[i] == "0":
                                if node.child0 is None:
                                        node.child0 = _Node()
                                node = node.child0
                        else:
                                if node.child1 is None:
                                        node.child1 = _Node()
                                node = node.child1
                node.value = value if value is not None else cidr
                node.network = net

        def lookup(self, ip: str) -> Tuple[Optional[ipaddress.IPv4Network], Any]:
                """
                Return (network, value) of the longest prefix that matches the IP.
                If no match, returns (None, None).
                """
                addr = ipaddress.ip_address(ip)
                if addr.version != 4:
                        raise ValueError("only IPv4 is supported")
                bits = _int_to_bits(int(addr), 32)
                node = self.root
                last_value_node: Optional[_Node] = None
                for b in bits:
                        if node.value is not None:
                                last_value_node = node
                        node = node.child1 if b == "1" else node.child0
                        if node is None:
                                break
                if node is not None and node.value is not None:
                        last_value_node = node
                if last_value_node is None:
                        return None, None
                return last_value_node.network, last_value_node.value


def _int_to_bits(x: int, bits: int) -> str:
        return bin(x)[2:].zfill(bits)


def _load_prefix_file(path: str) -> IPTrie:
        trie = IPTrie()
        with open(path, "r", encoding="utf-8") as fh:
                for lineno, line in enumerate(fh, start=1):
                        line = line.strip()
                        if not line or line.startswith("#"):
                                continue
                        parts = line.split()
                        cidr = parts[0]
                        val = parts[1] if len(parts) > 1 else None
                        try:
                                trie.insert(cidr, val)
                        except Exception as e:
                                raise RuntimeError(f"{path}:{lineno}: {e}")
        return trie


def _main():
        if len(sys.argv) != 2:
                print("Usage: python lpm.py prefixes.txt", file=sys.stderr)
                sys.exit(2)
        trie = _load_prefix_file(sys.argv[1])
        try:
                for line in sys.stdin:
                        ip = line.strip()
                        if not ip:
                                continue
                        try:
                                net, val = trie.lookup(ip)
                        except Exception as e:
                                print(f"{ip} -> error: {e}")
                                continue
                        if net is None:
                                print(f"{ip} -> no match")
                        else:
                                print(f"{ip} -> {net.with_prefixlen}  ({val})")
        except KeyboardInterrupt:
                pass


if __name__ == "__main__":
        _main()