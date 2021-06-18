from typing import *

import gmpy2
import mmh3

ZERO_HASH = b'\00\00\00\00\00\00\00\00\00\00\00\00\00\00\00\00'

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


def add_hash_to_vector(h_bytes: AnyStr, vector: List[float], vector_offset: int, weight: float = 1):
    for h_byte in h_bytes:
        mask = 1
        for bit in range(8):
            vector[vector_offset] += weight if h_byte & mask != 0 else -weight
            mask <<= 1
            vector_offset += 1


def add_hash_tuple_to_vector(h_tuple: Tuple[int, int], vector: List[float], weight: float = 1):
    add_int_hash_to_vector(h_tuple[0], vector, 0, weight)
    add_int_hash_to_vector(h_tuple[1], vector, 64, weight)


def add_int_hash_to_vector(int_hash, vector, offset, weight):
    mask = 1
    for bit in range(64):
        vector[offset] += weight if int_hash & mask != 0 else -weight
        mask <<= 1
        offset += 1


def binarize_vector_to_hash(vector: List[float]) -> AnyStr:
    """ Returns 16-byte hash """
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


def binarize_vector_part_to_int_hash(vector: List[float], vector_offset: int) -> int:
    result: int = 0
    mask = 1

    for bit_offset in range(64):
        result |= mask if vector[vector_offset] > 0 else 0
        mask <<= 1
        vector_offset += 1

    return result


def binarize_vector_to_hash_tuple(vector: List[float]) -> Tuple[int, int]:
    return binarize_vector_part_to_int_hash(vector, 0), binarize_vector_part_to_int_hash(vector, 64)


def mean_squared_hamming_distance(centroid_hash: AnyStr, hashes: Iterable[AnyStr]):
    result: int = 0
    n: int = 0
    for h_bytes in hashes:
        d = hamming_distance(centroid_hash, h_bytes)
        result += d * d
        n += 1
    return 0 if n == 0 else result / n


def centroid(hashes: Iterable[AnyStr]) -> AnyStr:
    vector = [0] * 16 * 8
    for h_bytes in hashes:
        add_hash_to_vector(h_bytes, vector, 0)
    return binarize_vector_to_hash(vector)


def centroid_for_int_hashes(hashes: Iterable[int]) -> int:
    vector = [0] * 64
    for int_hash in hashes:
        add_int_hash_to_vector(int_hash, vector, 0, 1)
    return binarize_vector_part_to_int_hash(vector, 0)


def seq_sim_hash(
        tokenized_string: Sequence[AnyStr],
        token_weight: Callable[[AnyStr], float] = lambda token: 1) -> Tuple[AnyStr, AnyStr]:
    """ Returns 2x 16-byte hashes """
    length = len(tokenized_string)
    if length == 0:
        return ZERO_HASH, ZERO_HASH
    elif length == 1:
        hash_bytes = mmh3.hash_bytes(tokenized_string[0])
        return hash_bytes, hash_bytes
    elif length == 3:
        # Special case: if common approach is used, then hash of the middle element is ignored:
        # first element hash has weight 2, middle element hash has weight 1, thus, first element always dominates.
        # Thus, as an exception, put all elements with the same weight.
        # vector1 = [0] * 16 * 8
        vector = [0] * 16 * 16
        hash_bytes0 = mmh3.hash_bytes(tokenized_string[0])
        token_weight0 = token_weight(tokenized_string[0])
        hash_bytes1 = mmh3.hash_bytes(tokenized_string[1])
        token_weight1 = token_weight(tokenized_string[1])
        hash_bytes2 = mmh3.hash_bytes(tokenized_string[2])
        token_weight2 = token_weight(tokenized_string[2])
        add_hash_to_vector(hash_bytes0, vector, 0, token_weight0)
        add_hash_to_vector(hash_bytes1, vector, 0, token_weight1)
        add_hash_to_vector(hash_bytes1, vector, 128, token_weight1)
        add_hash_to_vector(hash_bytes2, vector, 128, token_weight2)
        return binarize_vector_to_hash(vector[0:128]), binarize_vector_to_hash(vector[128:256])
    else:
        vector = [0] * 16 * 16
        for i in range(length):
            token = tokenized_string[i]
            hash_bytes = mmh3.hash_bytes(token)
            weight = token_weight(token)
            count_after = length - 1 - i
            if count_after > 0:
                add_hash_to_vector(hash_bytes, vector, 0, count_after * weight)
            count_before = i
            if count_before > 0:
                add_hash_to_vector(hash_bytes, vector, 128, count_before * weight)
        return binarize_vector_to_hash(vector[0:128]), binarize_vector_to_hash(vector[0:128])


def seq_sim_hash_tuple(
        tokenized_string: Sequence[AnyStr],
        token_weight: Callable[[AnyStr], float] = lambda token: 1) -> Tuple[Tuple[int, int], Tuple[int, int]]:
    length = len(tokenized_string)
    if length == 0:
        return (0, 0), (0, 0)
    elif length == 1:
        hash_tuple: Tuple[int, int] = mmh3.hash64(tokenized_string[0])
        return hash_tuple, hash_tuple
    elif length == 3:
        # Special case: if common approach is used, then hash of the middle element is ignored:
        # first element hash has weight 2, middle element hash has weight 1, thus, first element always dominates.
        # Thus, as an exception, put all elements with the same weight.
        vector1 = [0] * 16 * 8
        vector2 = [0] * 16 * 8
        hash_tuple0 = mmh3.hash64(tokenized_string[0])
        token_weight0 = token_weight(tokenized_string[0])
        hash_tuple1 = mmh3.hash64(tokenized_string[1])
        token_weight1 = token_weight(tokenized_string[1])
        hash_tuple2 = mmh3.hash64(tokenized_string[2])
        token_weight2 = token_weight(tokenized_string[2])
        add_hash_tuple_to_vector(hash_tuple0, vector1, token_weight0)
        add_hash_tuple_to_vector(hash_tuple1, vector1, token_weight1)
        add_hash_tuple_to_vector(hash_tuple1, vector2, token_weight1)
        add_hash_tuple_to_vector(hash_tuple2, vector2, token_weight2)
        return binarize_vector_to_hash_tuple(vector1), binarize_vector_to_hash_tuple(vector2)
    else:
        vector1 = [0] * 16 * 8
        vector2 = [0] * 16 * 8
        for i in range(length):
            token = tokenized_string[i]
            hash_tuple: Tuple[int, int] = mmh3.hash64(token)
            weight = token_weight(token)
            count_after = length - 1 - i
            if count_after > 0:
                add_hash_tuple_to_vector(hash_tuple, vector1, count_after * weight)
            count_before = i
            if count_before > 0:
                add_hash_tuple_to_vector(hash_tuple, vector2, count_before * weight)
        return binarize_vector_to_hash_tuple(vector1), binarize_vector_to_hash_tuple(vector2)


def hamming_distance(hash_string1: AnyStr, hash_string2: AnyStr) -> int:
    result = 0
    for i in range(len(hash_string1)):
        result += BIT_COUNTS[hash_string1[i] ^ hash_string2[i]]
    return result


def seq_sim_hash_hamming_distance(hash_string_tuple1: Tuple[AnyStr, AnyStr], hash_string_tuple2: Tuple[AnyStr, AnyStr]) -> int:
    return hamming_distance(hash_string_tuple1[0], hash_string_tuple2[0]) + \
           hamming_distance(hash_string_tuple1[1], hash_string_tuple2[1])


def hamming_distance_for_tuple_hash(hash_tuple1: Tuple[int, int], hash_tuple2: Tuple[int, int]) -> int:
    result = 0
    result += gmpy2.popcount(hash_tuple1[0] ^ hash_tuple2[0])
    result += gmpy2.popcount(hash_tuple1[1] ^ hash_tuple2[2])
    return result


def seq_sim_tuple_hash_hamming_distance(
        seq_hash_tuple1: Tuple[Tuple[int, int], Tuple[int, int]],
        seq_hash_tuple2: Tuple[Tuple[int, int], Tuple[int, int]]) -> int:
    return hamming_distance_for_tuple_hash(seq_hash_tuple1[0], seq_hash_tuple2[0]) + \
           hamming_distance_for_tuple_hash(seq_hash_tuple1[1], seq_hash_tuple2[1])
