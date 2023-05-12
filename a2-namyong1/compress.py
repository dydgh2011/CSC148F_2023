"""
Assignment 2 starter code
CSC148, Winter 2023

This code is provided solely for the personal and private use of
students taking the CSC148 course at the University of Toronto.
Copying for purposes other than this use is expressly prohibited.
All forms of distribution of this code, whether as given or with
any changes, are expressly prohibited.

All of the files in this directory and all subdirectories are:
Copyright (c) 2022 Bogdan Simion, Dan Zingaro
"""
from __future__ import annotations

import time

from huffman import HuffmanTree
from utils import *


def build_frequency_dict(text: bytes) -> dict[int, int]:
    """ Return a dictionary which maps each of the bytes in <text> to its
    frequency.

    >>> d = build_frequency_dict(bytes([65, 66, 67, 66]))
    >>> d == {65: 1, 66: 2, 67: 1}
    True
    """
    # https://www.programiz.com/python-programming/methods/dictionary/get
    # https://docs.python.org/3.9/library/stdtypes.html
    freq_dict = {}
    for byte in text:
        # using this code, you don't have to worry about key error
        # dict.get returns 0 if there is no key value
        freq_dict[byte] = freq_dict.get(byte, 0) + 1
    return freq_dict


def build_huffman_tree(freq_dict: dict[int, int]) -> HuffmanTree:
    """ Return the Huffman tree corresponding to the frequency dictionary
    <freq_dict>.
    freq_dict = {symbol: freq}

    Precondition: freq_dict is not empty.

    >>> freq = {2: 6, 3: 4}
    >>> t = build_huffman_tree(freq)
    >>> result = HuffmanTree(None, HuffmanTree(3), HuffmanTree(2))
    >>> t == result
    True
    >>> freq = {2: 6, 3: 4, 7: 5}
    >>> t = build_huffman_tree(freq)
    >>> result = HuffmanTree(None, HuffmanTree(2), \
                             HuffmanTree(None, HuffmanTree(3), HuffmanTree(7)))
    >>> t == result
    True
    >>> import random
    >>> symbol = random.randint(0,255)
    >>> freq = {symbol: 6}
    >>> t = build_huffman_tree(freq)
    >>> any_valid_byte_other_than_symbol = (symbol + 1) % 256
    >>> dummy_tree = HuffmanTree(any_valid_byte_other_than_symbol)
    >>> result = HuffmanTree(None, HuffmanTree(symbol), dummy_tree)
    >>> t.left == result.left or t.right == result.left
    True
    """
    # https://www.csestack.org/difference-between-sort-sorted-python-list-performance
    # /#:~:text=Here%2C%20sorted()%20function%20method,
    # or%20function%20you%20are%20using.
    # using sorted() instead of sort() because sorted is faster
    # the data is sorted by frequency values in
    # increasing order at the first place
    data = sorted(freq_dict.items(), key=lambda x: x[1])
    # since we have to pop 2 elements from the list,
    # the length of the data suppose to be greater than 1
    for _ in range(len(data) - 1):
        # s1 and s2 are tuples, s1 <= s2
        s1, s2 = data.pop(0), data.pop(0)
        s = HuffmanTree(None,
                        HuffmanTree(s1[0]) if isinstance(s1[0], int) else s1[0],
                        HuffmanTree(s2[0]) if isinstance(s2[0], int) else s2[0])
        freq_sum = s1[1] + s2[1]
        # instead of using sorted() again, it is much more efficient to
        # just find the index where the value suppose to get in to
        lo, hi = 0, len(data)
        while lo < hi:
            mid = (lo + hi) // 2
            # it is >= because the huffman tree
            # suppose to go after symbols with same frequency
            if freq_sum >= data[mid][1]:
                lo = mid + 1
            else:
                hi = mid
        data.insert(lo, (s, freq_sum))
    if isinstance(data[0][0], HuffmanTree):
        return data[0][0]
    # when there is only one symbol in given file,
    # existing symbol must be the left value and right value can be anything
    # but left value
    d = data[0][0]
    # if d = 0, r = 255, if d = 255, r = 0
    # and if d = 177, r = 178, no overlap
    return HuffmanTree(None, HuffmanTree(d), HuffmanTree(255 - d))


def get_codes(tree: HuffmanTree) -> dict[int, str]:
    """ Return a dictionary which maps symbols from the Huffman tree <tree>
    to codes.
    >>> tree = HuffmanTree(None, HuffmanTree(3), HuffmanTree(2))
    >>> d = get_codes(tree)
    >>> d == {3: "0", 2: "1"}
    True
    >>> tree = HuffmanTree(None, HuffmanTree(3), HuffmanTree(2))
    >>> print(get_codes(tree))
    {3: '0', 2: '1'}
    >>> b = b'helloworld'
    >>> s = {i: b.count(i) for i in b}
    >>> f = build_huffman_tree(s)
    >>> c = get_codes(f)
    >>> c == {104: '000', 101: '001', 119: '010', 114: '011', 108: '10', 100: '110', 111: '111'}
    True
    """

    # https://realpython.com/inner-functions-what-are-they-good-for/
    # #:~:text=The%20use%20cases%20of%20Python,
    # also%20create%20closures%20and%20decorators.
    # inner helper function increases the efficiency
    def _get_codes_helper(node: HuffmanTree,
                          code: list[str], codes: dict[int, str]) -> None:
        """
        this method is to travel through the tree and modify dict
        """
        if node.is_leaf():
            # if it is leaf, than it is clear that
            # prefix is filled and it represents the code
            # so join it
            codes[node.symbol] = ''.join(code)
        else:
            # it is post order
            code.append('0')
            _get_codes_helper(node.left, code, codes)
            code.pop()
            code.append('1')
            _get_codes_helper(node.right, code, codes)
            code.pop()

    cods = {}
    _get_codes_helper(tree, [], cods)
    return cods


def number_nodes(tree: HuffmanTree) -> None:
    """ Number internal nodes in <tree> according to postorder traversal. The
    numbering starts at 0.

    >>> left = HuffmanTree(None, HuffmanTree(3), HuffmanTree(2))
    >>> right = HuffmanTree(None, HuffmanTree(9), HuffmanTree(10))
    >>> tree = HuffmanTree(None, left, right)
    >>> number_nodes(tree)
    >>> tree.left.number
    0
    >>> tree.right.number
    1
    >>> tree.number
    2
    """

    def _number_nodes_helper(t: HuffmanTree, count: int) -> int:
        """
        number_nodes helper function
        """
        # also post order
        if t.is_leaf():
            return 0
        else:
            if not t.left.is_leaf():
                count = _number_nodes_helper(t.left, count)
            if not t.right.is_leaf():
                count = _number_nodes_helper(t.right, count)
            t.number = count
            return count + 1

    # the node number starts from 0, not 1
    _number_nodes_helper(tree, 0)


def avg_length(tree: HuffmanTree, freq_dict: dict[int, int]) -> float:
    """ Return the average number of bits required per symbol, to compress the
    text made of the symbols and frequencies in <freq_dict>, using the Huffman
    tree <tree>.

    The average number of bits = the weighted sum of the length of each symbol
    (where the weights are given by the symbol's frequencies), divided by the
    total of all symbol frequencies.

    >>> freq = {3: 2, 2: 7, 9: 1}
    >>> left = HuffmanTree(None, HuffmanTree(3), HuffmanTree(2))
    >>> right = HuffmanTree(9)
    >>> tree = HuffmanTree(None, left, right)
    >>> avg_length(tree, freq)  # (2*2 + 7*2 + 1*1) / (2 + 7 + 1)
    1.9
    """

    def _avg_length_helper(t: HuffmanTree, f: dict[int, int], c: int) -> int:
        """
        avg_length helper function
        it returns the total number of digits
        """
        if t.is_leaf():
            return f[t.symbol] * c
        else:
            result = 0
            result += _avg_length_helper(t.left, f, c + 1)
            result += _avg_length_helper(t.right, f, c + 1)
        return result

    return _avg_length_helper(tree, freq_dict, 0) / sum(freq_dict.values())


def compress_bytes(text: bytes, codes: dict[int, str]) -> bytes:
    """ Return the compressed form of <text>, using the mapping from <codes>
    for each symbol.

    >>> d = {0: "0", 1: "10", 2: "11"}
    >>> text = bytes([1, 2, 1, 0])
    >>> result = compress_bytes(text, d)
    >>> result == bytes([184])
    True
    >>> [byte_to_bits(byte) for byte in result]
    ['10111000']
    >>> text = bytes([1, 2, 1, 0, 2])
    >>> result = compress_bytes(text, d)
    >>> [byte_to_bits(byte) for byte in result]
    ['10111001', '10000000']
    """
    # https://realpython.com/python-bitwise-operators/
    # https://blog.finxter.com/python-bytes-vs-bytearray/
    # using bytes are faster, so you have to change it
    result = bytearray()
    # first create a large line of string with all the bytes
    bits = "".join([codes[i] for i in text])
    buffer = 0
    count = 0
    for bit in bits:
        # stack up the bits
        buffer = (buffer << 1) | (bit == "1")
        count += 1
        # insert byte
        if count == 8:
            result.append(buffer)
            buffer = 0
            count = 0
    # insert the remaining bits
    if count > 0:
        buffer <<= (8 - count)
        result.append(buffer)
    return bytes(result)


def tree_to_bytes(tree: HuffmanTree) -> bytes:
    """
    Return a bytes representation of the Huffman tree <tree>.
    The representation should be based on the postorder traversal of the tree's
    internal nodes, starting from 0.

    Precondition: <tree> has its nodes numbered.

    >>> tree = HuffmanTree(None, HuffmanTree(3, None, None), \
    HuffmanTree(2, None, None))
    >>> number_nodes(tree)
    >>> list(tree_to_bytes(tree))
    [0, 3, 0, 2]
    >>> left = HuffmanTree(None, HuffmanTree(3, None, None), \
    HuffmanTree(2, None, None))
    >>> right = HuffmanTree(5)
    >>> tree = HuffmanTree(None, left, right)
    >>> number_nodes(tree)
    >>> list(tree_to_bytes(tree))
    [0, 3, 0, 2, 1, 0, 0, 5]
    >>> tree = build_huffman_tree(build_frequency_dict(b"helloworld"))
    >>> number_nodes(tree)
    >>> list(tree_to_bytes(tree))\
            #doctest: +NORMALIZE_WHITESPACE
    [0, 104, 0, 101, 0, 119, 0, 114, 1, 0, 1, 1, 0, 100, 0, 111, 0, 108,\
    1, 3, 1, 2, 1, 4]
    """
    # post order
    if not tree.is_leaf():
        result = b''
        if not tree.left.is_leaf():
            result += tree_to_bytes(tree.left)
        if not tree.right.is_leaf():
            result += tree_to_bytes(tree.right)
        b_1 = bytes([1]) if not tree.left.is_leaf() else bytes([0])
        b_2 = bytes([tree.left.number]) \
            if not tree.left.is_leaf() else bytes([tree.left.symbol])
        b_3 = bytes([1]) if not tree.right.is_leaf() else bytes([0])
        b_4 = bytes([tree.right.number]) \
            if not tree.right.is_leaf() else bytes([tree.right.symbol])
        result += (b_1 + b_2 + b_3 + b_4)
        return result
    else:
        return b'0'


def compress_file(in_file: str, out_file: str) -> None:
    """ Compress contents of the file <in_file> and store results in <out_file>.
    Both <in_file> and <out_file> are string objects representing the names of
    the input and output files.

    Precondition: The contents of the file <in_file> are not empty.
    """
    with open(in_file, "rb") as f1:
        text = f1.read()
    freq = build_frequency_dict(text)
    tree = build_huffman_tree(freq)
    codes = get_codes(tree)
    number_nodes(tree)
    print("Bits per symbol:", avg_length(tree, freq))
    result = (tree.num_nodes_to_bytes() + tree_to_bytes(tree)
              + int32_to_bytes(len(text)))
    result += compress_bytes(text, codes)
    with open(out_file, "wb") as f2:
        f2.write(result)


def generate_tree_general(node_lst: list[ReadNode],
                          root_index: int) -> HuffmanTree:
    """ Return the Huffman tree corresponding to node_lst[root_index].
    The function assumes nothing about the order of the tree nodes in the list.

    >>> lst = [ReadNode(0, 5, 0, 7), ReadNode(0, 10, 0, 12), \
    ReadNode(1, 1, 1, 0)]
    >>> generate_tree_general(lst, 2)
    HuffmanTree(None, HuffmanTree(None, HuffmanTree(10, None, None), \
HuffmanTree(12, None, None)), \
HuffmanTree(None, HuffmanTree(5, None, None), HuffmanTree(7, None, None)))
    """
    nodes = {}
    for i in range(len(node_lst)):
        nodes[i] = HuffmanTree(None,
                               HuffmanTree(node_lst[i].l_data)
                               if node_lst[i].l_type == 0
                               else nodes[node_lst[i].l_data],
                               HuffmanTree(node_lst[i].r_data)
                               if node_lst[i].r_type == 0
                               else nodes[node_lst[i].r_data])
    return nodes[root_index]


def generate_tree_postorder(node_lst: list[ReadNode],
                            root_index: int) -> HuffmanTree:
    """ Return the Huffman tree corresponding to node_lst[root_index].
    The function assumes that the list represents a tree in postorder.

    >>> lst = [ReadNode(0, 5, 0, 7), ReadNode(0, 10, 0, 12), \
    ReadNode(1, 0, 1, 0)]
    >>> generate_tree_postorder(lst, 2)
    HuffmanTree(None, HuffmanTree(None, HuffmanTree(5, None, None), \
HuffmanTree(7, None, None)), \
HuffmanTree(None, HuffmanTree(10, None, None), HuffmanTree(12, None, None)))
    """
    nodes = {}
    for i in range(len(node_lst)):
        nodes[i] = HuffmanTree(None,
                               HuffmanTree(node_lst[i].l_data)
                               if node_lst[i].l_type == 0
                               else nodes[
                                   i - 2 if node_lst[i].r_type == 1
                                   else i - 1
                               ],
                               HuffmanTree(node_lst[i].r_data)
                               if node_lst[i].r_type == 0
                               else nodes[
                                   i - 1])
    return nodes[root_index]


def decompress_bytes(tree: HuffmanTree, text: bytes, size: int) -> bytes:
    """ Use Huffman tree <tree> to decompress <size> bytes from <text>.

    >>> tree = build_huffman_tree(build_frequency_dict(b'helloworld'))
    >>> number_nodes(tree)
    >>> decompress_bytes(tree, \
             compress_bytes(b'helloworld', get_codes(tree)), len(b'helloworld'))
    b'helloworld'
    """
    bits = []
    for i in text:
        bits.extend(byte_to_bits(i))
    result = bytearray()
    i = 0
    while i < len(bits) and len(result) < size:
        node = tree
        while not node.is_leaf():
            node = node.left if bits[i] == "0" else node.right
            i += 1
        result.append(node.symbol)
    return bytes(result)


def decompress_file(in_file: str, out_file: str) -> None:
    """ Decompress contents of <in_file> and store results in <out_file>.
    Both <in_file> and <out_file> are string objects representing the names of
    the input and output files.

    Precondition: The contents of the file <in_file> are not empty.
    """
    with open(in_file, "rb") as f:
        num_nodes = f.read(1)[0]
        buf = f.read(num_nodes * 4)
        node_lst = bytes_to_nodes(buf)
        # use generate_tree_general or generate_tree_postorder here
        tree = generate_tree_general(node_lst, num_nodes - 1)
        size = bytes_to_int(f.read(4))
        with open(out_file, "wb") as g:
            text = f.read()
            g.write(decompress_bytes(tree, text, size))


def improve_tree(tree: HuffmanTree, freq_dict: dict[int, int]) -> None:
    """ Improve the tree <tree> as much as possible, without changing its shape,
    by swapping nodes. The improvements are with respect to the dictionary of
    symbol frequencies <freq_dict>.

    >>> left = HuffmanTree(None, HuffmanTree(99, None, None), \
    HuffmanTree(100, None, None))
    >>> right = HuffmanTree(None, HuffmanTree(101, None, None), \
    HuffmanTree(None, HuffmanTree(97, None, None), HuffmanTree(98, None, None)))
    >>> tree = HuffmanTree(None, left, right)
    >>> freq = {97: 26, 98: 23, 99: 20, 100: 16, 101: 15}
    >>> avg_length(tree, freq)
    2.49
    >>> improve_tree(tree, freq)
    >>> avg_length(tree, freq)
    2.31
    """

    def _improve_tree_insertion(t: HuffmanTree, ls: list, index: int) -> int:
        """
        improve_tree_insertion
        """
        if t.is_leaf():
            t.symbol = ls[index]
            return index + 1
        else:
            index = _improve_tree_insertion(t.left, ls, index)
            index = _improve_tree_insertion(t.right, ls, index)
            return index

    def _improve_tree_leaves(t: HuffmanTree) -> list:
        """
        improve_tree_leaves
        """
        if t.is_leaf():
            return [t.symbol]
        else:
            result = []
            result.extend(_improve_tree_leaves(t.left))
            result.extend(_improve_tree_leaves(t.right))
            return result

    leaves = _improve_tree_leaves(tree)
    leaves.sort(key=lambda x: freq_dict[x], reverse=True)
    _improve_tree_insertion(tree, leaves, 0)


if __name__ == "__main__":

    import doctest

    doctest.testmod()

    import python_ta

    python_ta.check_all(config={
        'allowed-io': ['compress_file', 'decompress_file'],
        'allowed-import-modules': [
            'python_ta', 'doctest', 'typing', '__future__',
            'time', 'utils', 'huffman', 'random'
        ],
        'disable': ['W0401']
    })

    mode = input(
        "Press c to compress, d to decompress, or other key to exit: ")
    if mode == "c":
        fname = input("File to compress: ")
        start = time.time()
        compress_file(fname, fname + ".huf")
        print(f"Compressed {fname} in {time.time() - start} seconds.")
    elif mode == "d":
        fname = input("File to decompress: ")
        start = time.time()
        decompress_file(fname, fname + ".orig")
        print(f"Decompressed {fname} in {time.time() - start} seconds.")
