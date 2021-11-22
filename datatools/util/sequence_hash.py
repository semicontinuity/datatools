"""
Sequence hash.
Similar to SimHash, but with the following improvements:
- Contribution of each token to the vector is weighted
- Token vector contributes to the two sets of hash bits:
  - in the first set, token contribution is additionally weighted with "closeness" to the beginning of the string
  - in the second set, token contribution is additionally weighted with "closeness" to the end of the string
  This allows to retain some information about position of the token in the string,
  and handle token strings not like just bags of words.
"""
from typing import *

import mmh3

ZERO_HASH = b'\00' * 32     # 32 bytes = 256 bits


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
    """ Returns N-bit hash """
    vector_offset = 0
    result_offset = 0
    bits = len(vector)
    result = bytearray(bits // 8)
    for offset in range(bits // 8):
        mask = 1
        hash_byte = 0

        for bit in range(8):
            hash_byte |= mask if vector[vector_offset] > 0 else 0
            mask <<= 1
            vector_offset += 1

        result[result_offset] = hash_byte
        result_offset += 1

    return result


def centroid(hashes: Iterable[AnyStr], size_bits=256) -> AnyStr:
    vector = [0] * size_bits
    for h_bytes in hashes:
        add_hash_to_vector(h_bytes, vector, 0)
    return binarize_vector_to_hash(vector)


def seq_sim_vector(
        tokenized_string: Sequence[AnyStr],
        token_weight: Callable[[AnyStr], float] = lambda token: 1) -> List[int]:
    """ Returns 256-entry int vector """
    length = len(tokenized_string)
    if length == 0:
        return [0] * 16 * 16
    elif length == 1:
        vector = [0] * 16 * 16
        hash_bytes0 = mmh3.hash_bytes(tokenized_string[0])
        token_weight0 = token_weight(tokenized_string[0])
        add_hash_to_vector(hash_bytes0, vector, 0, token_weight0)
        add_hash_to_vector(hash_bytes0, vector, 128, token_weight0)
        return vector
    elif length == 3:
        # Special case: if common approach is used, then hash of the middle element is ignored:
        # first element hash has weight 2, middle element hash has weight 1, thus, first element always dominates.
        # Thus, as an exception, put all elements with the same weight.
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
        return vector
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
        return vector


def seq_sim_hash(
        tokenized_string: Sequence[AnyStr],
        token_weight: Callable[[AnyStr], float] = lambda token: 1) -> AnyStr:
    """ Returns 32-byte hash """
    length = len(tokenized_string)
    if length == 0:
        return ZERO_HASH
    elif length == 1:
        return mmh3.hash_bytes(tokenized_string[0]) * 2
    else:
        return binarize_vector_to_hash(seq_sim_vector(tokenized_string, token_weight))
