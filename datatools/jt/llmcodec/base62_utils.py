BASE62 = b"0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ"
RADIX = 62


def to_base62(n: int) -> str:
    if n == 0:
        return "0"
    res = []
    while n > 0:
        res.append(BASE62[n % RADIX])
        n //= RADIX
    res.reverse()
    return bytes(res).decode("ascii")


def base62_len(n: int) -> int:
    if n == 0:
        return 1
    length = 0
    while n > 0:
        length += 1
        n //= RADIX
    return length
