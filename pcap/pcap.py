import argparse
from scapy.all import PcapReader, Ether

#!/usr/bin/env python3
# pcap.py - extract unique MAC addresses from a pcap file using scapy


def extract_macs(pcap_path):
    macs = set()
    with PcapReader(pcap_path) as reader:
        for pkt in reader:
            if pkt is None:
                continue
            if pkt.haslayer(Ether):
                eth = pkt.getlayer(Ether)
                # normalize to lower-case
                macs.add(eth.src.lower())
                macs.add(eth.dst.lower())
    return macs

def main():
    parser = argparse.ArgumentParser(description="Print all MAC addresses seen in a pcap file.")
    parser.add_argument("pcap", help="path to pcap file to analyze")
    args = parser.parse_args()

    macs = extract_macs(args.pcap)
    for m in sorted(macs):
        print(m)
    print(f"\nTotal unique MACs: {len(macs)}")

if __name__ == "__main__":
    main()