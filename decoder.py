"""Hyve decoder/encoder
2019-01-08 v1.0 by Cees Timmerman
"""
import io, os, sys

def decode_pair(encoded_pair, result=None):
    """Starting with an empty result bytestring, read the encoded pair sequence (with
    length n) from the left (i = 0) to the right. For each pair read, if pi = 0, append
    qi to the output stream. Otherwise, pi > 0. Read the last pi characters appended
    to the result string and take the first (from the left) qi characters.
    For example, the following sequence:

    (0, 61), (1, 1), (0, 62), (3, 2), (3, 3)
    would result in the bytestring 61 61 62 61 61 62 61 61 (represented here in
    hexadecimal)
    """
    if result is None: result = []
    p, q = encoded_pair
    if p == 0:
        result.append(q)
    elif p > 0:
        result.extend(result[-p:][:q])
    
    return result

def encode(byte_str):
    result = []
    i = 0
    while i < len(byte_str):
        b = byte_str[i]
        # New byte? Add it.
        try: p = byte_str[:i].index(b)
        except ValueError:
            result.extend((0, b))
            i += 1
            continue
        # Seen byte? Encode seen part.
        length = 1
        while length < i-1 and i+length < len(byte_str) \
            and byte_str[p:p+length] == byte_str[i-p:i+length]:
                length += 1
        result.extend((i-p, length))
        i += length
    return bytes(result)

def encode_simple(byte_str):
    result = []
    for b in byte_str:
        result.extend((0, b))
    return bytes(result)

def decode_byte_stream(incoming):
    result = []
    while True:
        pair = incoming.read(2)
        if len(pair) == 0: break
        try:
            result = decode_pair(pair, result)
        except:
            result += bytes([0x3F])  # b'?'
    return bytes(result)

def decode(byte_str):
    return decode_byte_stream(io.BytesIO(byte_str))

def main(incoming=sys.stdin):
    # Print decoded incoming bytes
    result = decode_byte_stream(incoming)
    print(result)
    # Now output to stderr the re-encoded result
    if os.environ.get('USE_TRIVIAL_IMPLEMENTATION'):
        encoded = encode_simple(result)
    else:
        encoded = encode(result)
    print(encoded, file=sys.stderr)

def test():
    """Run these using: python -m doctest decoder.py
    >>> decode(bytes([0x0, 0x61, 0x1, 0x1, 0x0, 0x62, 0x3, 0x2, 0x3, 0x3]))
    b'aabaabaa'
    >>> decode(bytes([0x00, 0x20, 0x00, 0x2A, 0x02, 0x01, 0xFF]))
    b' * ?'
    >>> decode(encode(b'aabaabaa'))
    b'aabaabaa'
    >>> decode(encode(b'banana'))
    b'banana'
    >>> decode(encode(b'bananas'))
    b'bananas'
    >>> decode(encode_simple(b'badass'))
    b'badass'
    >>> decode(encode(b'Tai Tbo'))
    b'Tai Tbo'
    """

if __name__ == "__main__":
    #import doctest; doctest.testmod()
    main()