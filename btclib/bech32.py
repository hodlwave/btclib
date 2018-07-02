#!/usr/bin/env python3

'''Bech32 encoding

'''

from typing import Union, Optional

# used digits
__digits = b'qpzry9x8gf2tvdw0s3jn54khce6mua7l'
__base = len(__digits)
__hrp_char_set = set("""!"#$%&'()*+,-./0123456789:;<=>?@ABCDEFGHIJKLMNOPQRSTUVWXYZ[\\]^_`abcdefghijklmnopqrstuvwxyz{|}""")

def bech32_polymod(values):
  GEN = [0x3b6a57b2, 0x26508e6d, 0x1ea119fa, 0x3d4233dd, 0x2a1462b3]
  chk = 1
  for v in values:
    b = (chk >> 25)
    chk = (chk & 0x1ffffff) << 5 ^ v
    for i in range(5):
      chk ^= GEN[i] if ((b >> i) & 1) else 0
  return chk

def bech32_hrp_expand(s):
  return [ord(x) >> 5 for x in s] + [0] + [ord(x) & 31 for x in s]

def bech32_verify_checksum(hrp, data):
  return bech32_polymod(bech32_hrp_expand(hrp) + data) == 1

def bech32_create_checksum(hrp, data):
  values = bech32_hrp_expand(hrp) + data
  polymod = bech32_polymod(values + [0,0,0,0,0,0]) ^ 1
  return [(polymod >> 5 * (5 - i)) & 31 for i in range(6)]

def check_hrp(hrp: bytes) -> None:
    if hrp is None or len(hrp) == 0:
        raise ValueError("human-readable part must contain at least one character")
    if len(hrp) > 83:
        raise ValueError("human-readable part must contain 83 characters at most")
    if set(hrp) > __hrp_char_set:
        raise ValueError("human-readable part must contain US-ASCII characters in the range [33-126]")

def to_bytes(v: Union[str, bytes]) -> bytes:
    '''Return bytes from bytes or string'''
    if isinstance(v, str): v = v.encode('ascii')
    if not isinstance(v, bytes):
        raise TypeError(
            "a bytes-like object is required (also str), not '%s'" %
            type(v).__name__)
    return v

def bech32encode_check(v: Union[str, bytes], hrp: bytes = b'bc') -> bytes:
    '''Encode bytes (or string) using Bech32 with checksum'''

    v = to_bytes(v)
    result = bech32encode(v)
    result = result + bech32_create_checksum(hrp, v)

    if len(result) < 6: raise ValueError("too short")
    return result

def bech32encode(v: Union[str, bytes], hrp: bytes = b'bc') -> bytes:
    '''Encode bytes (or string) using Bech32'''

    v = to_bytes(v)
    check_hrp(hrp)

    # preserve leading-0s
    # leading-0s become Bech32 leading-qs
    nPad = len(v)
    v = v.lstrip(b'\0')
    vlen = len(v)
    nPad -= vlen
    result = __digits[0:1] * nPad

    if vlen:
        i = int.from_bytes(v, 'big')
        result = result + bech32encode_int(i)

    return hrp + b'1' + result

def bech32encode_int(i: int) -> bytes:
    '''Encode an integer using Bech32'''
    if i == 0: return __digits[0:1]
    result = b""
    while i > 0:
        i, idx = divmod(i, __base)
        result = __digits[idx:idx+1] + result
    return result

def bech32decode_check(v: Union[str, bytes], output_size: Optional[int] = None) -> bytes:
    '''Decode Bech32 encoded bytes (or string); also verify checksum and required output length'''

    v = to_bytes(v)

    # no mixed case strings
    # convert to lowercase

    pos_1 = v.find(b'1')
    if pos_1 == -1:
        raise ValueError("No '1' separator")
    hrp = v[:pos_1]
    v = v[pos_1+1:]
    if len(v) < 6: raise ValueError("too short")

    check_hrp(v[:pos_1])
    bech32_verify_checksum(hrp, v)

    result = bech32decode(v[:-6], output_size)
    return result

def bech32decode(v: Union[str, bytes], output_size: Optional[int] = None) -> bytes:
    '''Decode Bech32 encoded bytes (or string) and verify required output length'''

    v = to_bytes(v)
    pos_1 = v.find(b'1')
    if pos_1 == -1:
        raise ValueError("No '1' separator")
    check_hrp(v[:pos_1])
    v = v[pos_1+1:]

    # preserve leading-0s
    # Bech32 leading-qs become leading-0s
    nPad = len(v)
    v = v.lstrip(__digits[0:1])
    vlen = len(v)
    nPad -= vlen
    result = b'\0' * nPad

    if vlen:
        i = bech32decode_int(v)
        nbytes = (i.bit_length() + 7) // 8
        result = result + i.to_bytes(nbytes, 'big')

    if output_size is not None and len(result) != output_size:
        raise ValueError(
            "Invalid decoded byte length: %s (%s was required instead)" %
            (len(result), output_size))
    return result

def bech32decode_int(v: bytes) -> int:
    '''Decode Bech32 encoded bytes as integer'''

    i = 0
    for char in v:
        i *= __base
        i += __digits.index(char)
    return i
