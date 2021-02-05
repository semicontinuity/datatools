from math import sqrt
from typing import *

import mmh3


def add_hash_to_vector(h_bytes: AnyStr, vector: List[float], weight: float = 1):
    i = 0
    for h_byte in h_bytes:
        mask = 1
        for bit in range(8):
            vector[i] += weight if h_byte & mask != 0 else -weight
            mask <<= 1
            i += 1


def binarize_vector_to_hash(vector: List[float]) -> AnyStr:
    vector_offset = 0
    result_offset = 0
    result = bytearray(16)
    for offset in range(16):
        mask = 1
        hash_byte = 0

        for bit in range(8):
            hash_byte |= mask if vector[vector_offset] > 0 else 0
            mask <<= 1
            vector_offset += 1

        result[result_offset] = hash_byte
        result_offset += 1

    return result


def mean_squared_hamming_distance(centroid_hash: AnyStr, hashes: Iterable[AnyStr]):
    result: int = 0
    n: int = 0
    for h_bytes in hashes:
        d = hamming_distance(centroid_hash, h_bytes)
        result += d * d
        n += 1
    return 0 if n == 0 else result / n


def centroid(hashes: Iterable[AnyStr]):
    vector = [0] * 16 * 8
    for h_bytes in hashes:
        add_hash_to_vector(h_bytes, vector)
    return binarize_vector_to_hash(vector)


def seq_sim_hash(tokenized_string: Sequence[AnyStr], token_weight: Callable[[AnyStr], float] = lambda token: 1):
    length = len(tokenized_string)
    if length == 0:
        return mmh3.hash_bytes('')
    elif length == 1:
        hash_bytes = mmh3.hash_bytes('')
        return hash_bytes, hash_bytes
    elif length == 3:
        # Special case: if common approach is used, then hash of the middle element is ignored:
        # first element hash has weight 2, middle element hash has weight 1, thus, first element always dominates.
        # Thus, as an exception, put all elements with the same weight.
        vector1 = [0] * 16 * 8
        vector2 = [0] * 16 * 8
        hash_bytes0 = mmh3.hash_bytes(tokenized_string[0])
        token_weight0 = token_weight(tokenized_string[0])
        hash_bytes1 = mmh3.hash_bytes(tokenized_string[1])
        token_weight1 = token_weight(tokenized_string[1])
        hash_bytes2 = mmh3.hash_bytes(tokenized_string[2])
        token_weight2 = token_weight(tokenized_string[2])
        add_hash_to_vector(hash_bytes0, vector1, token_weight0)
        add_hash_to_vector(hash_bytes1, vector1, token_weight1)
        add_hash_to_vector(hash_bytes1, vector2, token_weight1)
        add_hash_to_vector(hash_bytes2, vector2, token_weight2)
        return binarize_vector_to_hash(vector1), binarize_vector_to_hash(vector2)
    else:
        vector1 = [0] * 16 * 8
        vector2 = [0] * 16 * 8
        for i in range(length):
            token = tokenized_string[i]
            hash_bytes = mmh3.hash_bytes(token)
            weight = token_weight(token)
            count_after = length - 1 - i
            if count_after > 0:
                add_hash_to_vector(hash_bytes, vector1, count_after * weight)
            count_before = i
            if count_before > 0:
                add_hash_to_vector(hash_bytes, vector2, count_before * weight)
        return binarize_vector_to_hash(vector1), binarize_vector_to_hash(vector2)


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


def hamming_distance(s1: AnyStr, s2: AnyStr):
    result = 0
    for i in range(len(s1)):
        result += BIT_COUNTS[s1[i] ^ s2[i]]
    return result


def seq_sim_hash_hamming_distance(s1: Tuple[AnyStr, AnyStr], s2: Tuple[AnyStr, AnyStr]):
    return hamming_distance(s1[0], s2[0]) + hamming_distance(s1[1], s2[1])
