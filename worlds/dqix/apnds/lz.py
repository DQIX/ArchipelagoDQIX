# apnds/lz.py
#
# Copyright (C) 2025-2026 James Petersen <m@jamespetersen.ca>
# Licensed under MIT. See LICENSE

from typing import Optional, Tuple

def decompress(data: bytes) -> bytes:
    """
    Decompress LZ10-compressed data.

    :param data: The data to be decompressed
    :return: The decompressed data.
    :raises ValueError: If the data is not valid LZ10-compressed data.
    """
    if len(data) < 4:
        raise ValueError('cannot decompress less than 4 bytes of data')

    if data[0] != 0x10:
        raise ValueError('expected first byte of data to be decompressed to be 0x10')

    ret = bytearray(int.from_bytes(data[1:4], 'little'))

    src_pos = 4
    dest_pos = 0

    while True:
        if src_pos >= len(data):
            raise ValueError('data could not be decompressed properly')
        flags = data[src_pos]
        src_pos += 1
        for _ in range(8):
            if flags & 0x80 != 0:
                block_size = (data[src_pos] >> 4) + 3
                block_distance = (((data[src_pos] & 0xF) << 8) | data[src_pos + 1]) + 1

                src_pos += 2

                block_pos = dest_pos - block_distance
                if block_pos < 0:
                    raise ValueError('data could not be decompressed properly')

                for i in range(block_size):
                    ret[dest_pos] = ret[block_pos + i]
                    dest_pos += 1
            else:
                if src_pos >= len(data) or dest_pos >= len(ret):
                    raise ValueError('data could not be decompressed properly')
                ret[dest_pos] = data[src_pos]
                src_pos += 1
                dest_pos += 1

            if dest_pos == len(ret):
                return bytes(ret)
            flags <<= 1

def decompress_code(code: bytes, compressed_top: int) -> Tuple[bytes, bytes]:
    """
    Decompress some code, given the top of the compressed code structure.
    This function will return the full decompressed code, as well as the data that is
    overwritten by the compressed code.

    :param code: The code to be decompressed.
    :param compressed_top: The offset within ``code`` at which the end of the compressed data lies.
                           Often, this will be the end of the data.
    :return: The decompressed data, and the remainder after the end of the compressed data, which is overwritten during decompression.
    """
    # this code is reverse-engineered from the decompression function
    # present in the C runtime of many DS games.
    rem = code[compressed_top:]

    src_bot = compressed_top - int.from_bytes(code[compressed_top - 8:compressed_top - 5], 'little')
    src_top = compressed_top - code[compressed_top - 5]
    dest = compressed_top + int.from_bytes(code[compressed_top - 4:compressed_top], 'little')

    c = bytearray(code) + bytearray(max(dest - len(code), 0))
    while src_bot < src_top:
        src_top -= 1
        flags = c[src_top]
        for _ in range(8):
            if flags & 0x80:
                src_top -= 1
                l = c[src_top]
                src_top -= 1
                i = ((c[src_top] | l << 8) & 0xFFF) + 2
                for _ in range(l + 0x20, -1, -0x10):
                    c[dest - 1] = c[dest + i]
                    dest -= 1
            else:
                src_top -= 1
                dest -= 1
                c[dest] = c[src_top]
            flags <<= 1
            if src_bot >= src_top:
                break

    return (bytes(c), rem)

def compress(data: bytes, min_distance: int = 2, forward_iteration: bool = True, pad: bool = True) -> bytes:
    """
    Compress LZ10-compressed data.

    :param min_distance: The minimum distance to look for blocks.
    :param forward_iteration: Whether to iterate forward or backwards for blocks.
    :param pad: Whether to pad the output, so that it lies on a 4-byte boundary.
    :return: The compressed data.
    :raises ValueError: If the data to be compressed is empty.
    """
    if len(data) == 0:
        raise ValueError('cannot compress zero bytes')

    worst_case_dest_size = (7 + len(data) + ((len(data) + 7) // 8)) & ~3

    ret = bytearray(worst_case_dest_size)

    ret[0] = 0x10
    ret[1:4] = int.to_bytes(len(data), 3, 'little')

    src_pos = 0
    dest_pos = 4

    if forward_iteration:
        def find_best_block(src: bytes, src_pos: int) -> Tuple[int, int]:
            best_block_size = 0
            best_block_distance = 0
            block_start = max(0, src_pos - 0x1000)
            
            while block_start != src_pos:
                block_size = 0

                while block_size < 18 and src_pos + block_size < len(src) and src[block_start + block_size] == src[src_pos + block_size]:
                    block_size += 1

                if block_size > best_block_size and src_pos - block_start >= min_distance:
                    best_block_distance = src_pos - block_start
                    best_block_size = block_size

                    if block_size == 18:
                        break

                block_start += 1

            return (best_block_distance, best_block_size)
    else:
        def find_best_block(src: bytes, src_pos: int) -> Tuple[int, int]:
            best_block_size = 0
            best_block_distance = 0
            block_distance = min_distance

            while block_distance <= src_pos and block_distance <= 0x1000:
                block_start = src_pos - block_distance
                block_size = 0

                while block_size < 18 and src_pos + block_size < len(src) and src[block_start + block_size] == src[src_pos + block_size]:
                    block_size += 1

                if block_size > best_block_size:
                    best_block_distance = block_distance
                    best_block_size = block_size

                    if block_size == 18:
                        break

                block_distance += 1

            return (best_block_distance, best_block_size)

    while True:
        flags_pos = dest_pos
        dest_pos += 1
        ret[flags_pos] = 0

        for i in range(8):
            best_block_distance, best_block_size = find_best_block(data, src_pos)

            if best_block_size >= 3:
                ret[flags_pos] |= (0x80 >> i)
                src_pos += best_block_size
                best_block_size -= 3
                best_block_distance -= 1
                ret[dest_pos] = ((best_block_size << 4) | (best_block_distance >> 8)) & 0xFF
                ret[dest_pos + 1] = best_block_distance & 0xFF
                dest_pos += 2
            else:
                ret[dest_pos] = data[src_pos]
                dest_pos += 1
                src_pos += 1

            if src_pos == len(data):
                if pad:
                    rem = dest_pos & 3
                    if rem != 0:
                        for i in range(4 - rem):
                            ret[dest_pos] = 0
                            dest_pos += 1

                return bytes(ret[:dest_pos])

def compress_code(code: bytes) -> Optional[bytes]:
    """
    Given some code, compress it according to the modified LZ10
    algorithm used for code compression.

    :param code: The code to be compressed.
    :return: The compressed code, if its size would be smaller than the original code.
    """

    def find_best_block(needle: bytes, haystack: bytes) -> Tuple[int, int]:
        if len(needle) < 3:
            return (0, 0)
        search_len = 3
        ret_index = ret_len = 0
        i = haystack.find(needle[-search_len:])
        while i != -1:
            k = i + search_len - 1
            l = min(k + 1, len(needle))
            for j in range(search_len, l):
                if needle[-j - 1] != haystack[k - j]:
                    break
            else:
                j = l
            ret_index = k
            ret_len = j
            search_len = ret_len + 1
            if search_len > len(needle):
                break
            i = haystack.find(needle[-search_len:], i)
        return (ret_len, ret_index)

    compressed = bytearray(len(code))
    src_pos = dst_pos = len(code)
    while True:
        if src_pos < 1:
            break
        if dst_pos < 1:
            return None
        flag = 0
        flag_pos = dst_pos = dst_pos - 1
        for _ in range(8):
            flag <<= 1
            if 0 >= src_pos:
                continue
            match_len, match_idx = find_best_block(code[max(0, src_pos - 0x12):src_pos], code[src_pos:src_pos + 0x1002])
            if match_len < 3:
                if dst_pos < 1:
                    return None
                dst_pos -= 1
                src_pos -= 1
                compressed[dst_pos] = code[src_pos]
            else:
                if dst_pos < 2:
                    return None
                src_pos -= match_len
                match_idx -= 2
                compressed[dst_pos - 1] = ((match_len - 3) << 4) | (match_idx >> 8)
                dst_pos -= 2
                compressed[dst_pos] = match_idx & 0xFF
                flag |= 1
        compressed[flag_pos] = flag

    compressed = compressed[dst_pos:]
    compressed_size = len(code) - dst_pos

    i = compressed_size
    orig_pos = len(code)
    def iterate_overwrite() -> Optional[Tuple[int, int]]:
        nonlocal orig_pos
        nonlocal i

        if orig_pos < 1:
            return (0, 0)
        i -= 1
        flag = compressed[i]
        for _ in range(8):
            if orig_pos <= 0:
                break
            if flag & 0x80 == 0:
                i -= 1
                orig_pos -= 1
            else:
                b = (compressed[i - 1] >> 4) + 3
                i -= 2
                orig_pos -= b
                if orig_pos < i:
                    return (orig_pos, i)
            flag <<= 1
        return None
    while True:
        ret = iterate_overwrite()
        if ret is not None:
            prefix_len, compressed_prefix_len = ret
            break

    before_padding = compressed_size - compressed_prefix_len + prefix_len
    after_padding = (before_padding + 3) & ~3
    total_len = after_padding + 8
    if total_len >= len(code):
        return None
    return b''.join((
        code[:prefix_len],
        compressed[compressed_prefix_len:],
        b'\xFF' * (after_padding - before_padding),
        (total_len - prefix_len).to_bytes(3, 'little'),
        (total_len - before_padding).to_bytes(1, 'little'),
        (len(code) - total_len).to_bytes(4, 'little'),
    ))

__all__: list[str] = ['decompress', 'decompress_code', 'compress', 'compress_code']
