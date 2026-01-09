"""
Huffman Encoding & Decoding
Single-file Python implementation for a course project.

Features:
- Read an input text file (UTF-8)
- Build Huffman tree using a priority queue (heapq)
- Generate codeword dictionary (char -> bitstring)
- Encode input into compressed binary file (.huff)
- Decode a compressed .huff file back to original text
- Show code table, compression stats, and example encode/decode

Usage (command-line):
    # To encode
    python Huffman_Encoding_Decoding_Project.py encode input.txt output.huff

    # To decode
    python Huffman_Encoding_Decoding_Project.py decode input.huff output.txt

Notes:
- The .huff binary format used here is simple and educational:
  [header length (4 bytes)][header JSON bytes][payload bytes]
  header contains: {
      "codes": {char: bitstring},
      "padding": <0-7 number of padding bits added at end>
  }
- This implementation stores codes in the header to simplify decoding. In real systems,
  canonical Huffman codes or a tree serialization is preferred for space efficiency.

Complexity:
- Building frequency map: O(n)
- Building heap and tree: O(k log k) where k = number of unique symbols
- Encoding: O(n)

Author: Course Student (template by assistant)
"""

import sys
import heapq
import json
from collections import defaultdict

class Node:
    def __init__(self, freq, symbol=None, left=None, right=None):
        self.freq = freq
        self.symbol = symbol
        self.left = left
        self.right = right

    # heapq requires objects to be comparable; we'll compare by freq and tie-breaker id()
    def __lt__(self, other):
        if self.freq == other.freq:
            return id(self) < id(other)
        return self.freq < other.freq


def build_frequency_map(text):
    freq = defaultdict(int)
    for ch in text:
        freq[ch] += 1
    return freq


def build_huffman_tree(freq_map):
    heap = []
    for sym, f in freq_map.items():
        heapq.heappush(heap, Node(f, symbol=sym))

    # Edge case: only one unique symbol
    if len(heap) == 1:
        sole = heapq.heappop(heap)
        # create a dummy parent so we have two-child tree
        parent = Node(sole.freq, left=sole, right=Node(0, symbol=""))
        heapq.heappush(heap, parent)

    while len(heap) > 1:
        a = heapq.heappop(heap)
        b = heapq.heappop(heap)
        parent = Node(a.freq + b.freq, left=a, right=b)
        heapq.heappush(heap, parent)

    return heap[0] if heap else None


def generate_codes(root):
    codes = {}
    def dfs(node, path):
        if node is None:
            return
        if node.symbol is not None and (node.left is None and node.right is None):
            # leaf
            codes[node.symbol] = path or '0'  # if only one symbol, give code '0'
            return
        dfs(node.left, path + '0')
        dfs(node.right, path + '1')
    dfs(root, '')
    return codes


def encode_text(text, codes):
    bits = []
    for ch in text:
        bits.append(codes[ch])
    return ''.join(bits)


def bits_to_bytes(bitstring):
    # pad to multiple of 8
    padding = (8 - len(bitstring) % 8) % 8
    bitstring_padded = bitstring + ('0' * padding)
    b = bytearray()
    for i in range(0, len(bitstring_padded), 8):
        byte = bitstring_padded[i:i+8]
        b.append(int(byte, 2))
    return bytes(b), padding


def bytes_to_bits(b):
    bits = []
    for byte in b:
        bits.append(f'{byte:08b}')
    return ''.join(bits)


def write_huff_file(outfile, codes, payload_bytes, padding):
    header = {
        'codes': {k: v for k, v in codes.items()},
        'padding': padding
    }
    header_json = json.dumps(header, ensure_ascii=False).encode('utf-8')
    header_len = len(header_json)
    # write 4-byte header length (big-endian)
    with open(outfile, 'wb') as f:
        f.write(header_len.to_bytes(4, byteorder='big'))
        f.write(header_json)
        f.write(payload_bytes)


def read_huff_file(infile):
    with open(infile, 'rb') as f:
        header_len_bytes = f.read(4)
        if len(header_len_bytes) < 4:
            raise ValueError('Not a valid .huff file (missing header length)')
        header_len = int.from_bytes(header_len_bytes, byteorder='big')
        header_json = f.read(header_len)
        header = json.loads(header_json.decode('utf-8'))
        payload = f.read()
    return header, payload


def decode_bits_to_text(bits, codes, padding):
    # remove padding bits at end
    if padding:
        bits = bits[:-padding]
    # build reverse map
    rev = {v: k for k, v in codes.items()}
    out_chars = []
    cur = ''
    for bit in bits:
        cur += bit
        if cur in rev:
            out_chars.append(rev[cur])
            cur = ''
    if cur != '':
        # leftover bits -- indicates data or header corruption
        raise ValueError('Decoding error: leftover bits after decoding')
    return ''.join(out_chars)


def compress_file(input_path, output_path):
    with open(input_path, 'r', encoding='utf-8') as f:
        text = f.read()

    freq_map = build_frequency_map(text)
    root = build_huffman_tree(freq_map)
    codes = generate_codes(root)

    bitstring = encode_text(text, codes)
    payload_bytes, padding = bits_to_bytes(bitstring)
    write_huff_file(output_path, codes, payload_bytes, padding)

    orig_size = len(text.encode('utf-8'))
    comp_size = 4 + len(json.dumps({'codes': codes, 'padding': padding}, ensure_ascii=False).encode('utf-8')) + len(payload_bytes)

    print('Compression complete')
    print(f'Unique symbols: {len(codes)}')
    print(f'Original size (bytes): {orig_size}')
    print(f'Compressed size (bytes): {comp_size}')
    ratio = comp_size / orig_size if orig_size else 0
    print(f'Compression ratio: {ratio:.3f}')
    print('Code table (symbol -> code):')
    for k, v in sorted(codes.items(), key=lambda x: (len(x[1]), x[0])):
        # show printable repr of symbol
        print(f"{repr(k)} -> {v}")


def decompress_file(input_path, output_path):
    header, payload = read_huff_file(input_path)
    codes = header['codes']
    padding = header.get('padding', 0)
    bits = bytes_to_bits(payload)
    text = decode_bits_to_text(bits, codes, padding)
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(text)
    print('Decompression complete')
    print(f'Wrote {len(text)} characters to {output_path}')


if __name__ == '__main__':
    if len(sys.argv) < 4:
        print('Usage:')
        print('  python Huffman_Encoding_Decoding_Project.py encode input.txt output.huff')
        print('  python Huffman_Encoding_Decoding_Project.py decode input.huff output.txt')
        sys.exit(1)

    mode = sys.argv[1].lower()
    inp = sys.argv[2]
    outp = sys.argv[3]

    if mode == 'encode':
        compress_file(inp, outp)
    elif mode == 'decode':
        decompress_file(inp, outp)
    else:
        print('Unknown mode:', mode)
        sys.exit(1)
