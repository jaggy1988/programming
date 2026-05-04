def convert_to_binary(ip_address):
    octets = ip_address.split('.')
    # Convert each octet to an 8-bit binary string and concatenate them together
    # The [2:] slice is used to remove the '0b' prefix that Python adds to binary literals, and zfill(8) ensures that each octet is represented as an 8-bit binary number (e.g., "1" becomes "00000001").
    # For example, "192" becomes "11000000", "168" becomes "10101000", "1" becomes "00000001", and "1" becomes "00000001". When concatenated, the result is "11000000101010000000000100000001".
    # This method ensures that the binary representation of the IP address is always 32 bits long, which is important for accurate representation and further manipulation (e.g., subnetting, CIDR calculations).
    # The function is designed to handle any valid IPv4 address and will produce a consistent 32-bit binary string output, regardless of the presence of leading zeros in the octets.
    binary_ip = ''.join([bin(int(octet))[2:].zfill(8) for octet in octets])
    # Pad the binary IP with leading zeros to ensure it's 32 bits. This is important for cases where the IP address has leading zeros in its octets (e.g., "192.168.1.1" -> "11000000101010000000000100000001")
    return binary_ip
print(convert_to_binary("192.168.1.1"))