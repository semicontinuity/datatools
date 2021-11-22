# can use gmpy2 for bit counts in uint64
from typing import *


# use int.bit_count() from python 3.10+
BIT_COUNTS = (b'\x00\x01\x01\x02\x01\x02\x02\x03\x01\x02\x02\x03\x02\x03\x03\x04'
              b'\x01\x02\x02\x03\x02\x03\x03\x04\x02\x03\x03\x04\x03\x04\x04\x05'
              b'\x01\x02\x02\x03\x02\x03\x03\x04\x02\x03\x03\x04\x03\x04\x04\x05'
              b'\x02\x03\x03\x04\x03\x04\x04\x05\x03\x04\x04\x05\x04\x05\x05\x06'
              b'\x01\x02\x02\x03\x02\x03\x03\x04\x02\x03\x03\x04\x03\x04\x04\x05'
              b'\x02\x03\x03\x04\x03\x04\x04\x05\x03\x04\x04\x05\x04\x05\x05\x06'
              b'\x02\x03\x03\x04\x03\x04\x04\x05\x03\x04\x04\x05\x04\x05\x05\x06'
              b'\x03\x04\x04\x05\x04\x05\x05\x06\x04\x05\x05\x06\x05\x06\x06\x07'
              b'\x01\x02\x02\x03\x02\x03\x03\x04\x02\x03\x03\x04\x03\x04\x04\x05'
              b'\x02\x03\x03\x04\x03\x04\x04\x05\x03\x04\x04\x05\x04\x05\x05\x06'
              b'\x02\x03\x03\x04\x03\x04\x04\x05\x03\x04\x04\x05\x04\x05\x05\x06'
              b'\x03\x04\x04\x05\x04\x05\x05\x06\x04\x05\x05\x06\x05\x06\x06\x07'
              b'\x02\x03\x03\x04\x03\x04\x04\x05\x03\x04\x04\x05\x04\x05\x05\x06'
              b'\x03\x04\x04\x05\x04\x05\x05\x06\x04\x05\x05\x06\x05\x06\x06\x07'
              b'\x03\x04\x04\x05\x04\x05\x05\x06\x04\x05\x05\x06\x05\x06\x06\x07'
              b'\x04\x05\x05\x06\x05\x06\x06\x07\x05\x06\x06\x07\x06\x07\x07\x08')


def mean_squared_hamming_distance(centroid_hash: AnyStr, hashes: Iterable[AnyStr]):
    result: int = 0
    n: int = 0
    for hash_bytes in hashes:
        d = hamming_distance(centroid_hash, hash_bytes)
        result += d * d
        n += 1
    return 0 if n == 0 else result / n


def hamming_distance(hash_string1: AnyStr, hash_string2: AnyStr) -> int:
    result = 0
    for i in range(len(hash_string1)):
        result += BIT_COUNTS[hash_string1[i] ^ hash_string2[i]]
    return result
