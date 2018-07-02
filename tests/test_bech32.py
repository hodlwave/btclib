#!/usr/bin/env python3

import unittest
from btclib.bech32 import bech32encode, bech32decode, \
                          bech32encode_int, bech32decode_int

class TestBech32CheckEncoding(unittest.TestCase):
    def test_bech32_empty(self):
     
        self.assertEqual(bech32encode(b''), b'bc1')
        self.assertEqual(bech32decode(b'bc1'), b'')
        self.assertEqual(bech32decode(bech32encode(b'')), b'')
        self.assertEqual(bech32encode(bech32decode(b'bc1')), b'bc1')

        self.assertEqual(bech32encode(''), b'bc1')
        self.assertEqual(bech32decode('bc1'), b'')
        self.assertEqual(bech32decode(bech32encode('')), b'')
        self.assertEqual(bech32encode(bech32decode('bc1')), b'bc1')


    def test_bech32_integers(self):
        digits = b'qpzry9x8gf2tvdw0s3jn54khce6mua7l'
        for i in range(len(digits)):
            char = digits[i:i+1]
            self.assertEqual(bech32decode_int(char), i)
            self.assertEqual(bech32encode_int(i), char)
        number = 0x443214c74254b635cf84653a56d7c675be77df
        self.assertEqual(bech32decode_int(digits), number)
        self.assertEqual(bech32encode_int(number), digits[1:])            

if __name__ == "__main__":
    # execute only if run as a script
    unittest.main()
