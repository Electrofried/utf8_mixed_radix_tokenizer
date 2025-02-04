"""
utf8_mixed_radix_tokenizer.py

A UTF‑8–based mixed‑radix tokenizer that converts Unicode text into a list of integers
using the mixed‑radix encoding of UTF‑8, and can reverse the process to recover the text.
"""

class UTF8MixedRadixTokenizer:
    def __init__(self):
        # You can add initialization parameters if needed.
        pass

    def tokenize(self, text: str) -> list[int]:
        """
        Tokenizes a Unicode string into a list of integers using its UTF‑8 mixed‑radix representation.
        Each Unicode character is encoded in UTF‑8 and its data bits are extracted and combined into an integer.

        Args:
            text (str): The input Unicode string.

        Returns:
            List[int]: A list of integers representing each token.
        """
        tokens = []
        for char in text:
            encoded = char.encode('utf-8')
            if len(encoded) == 1:
                # 1-byte encoding: 0xxx xxxx → 7 data bits
                token = encoded[0] & 0x7F  # mask off the header (0x7F == 0b01111111)
            elif len(encoded) == 2:
                # 2-byte encoding: 110xxxxx, 10xxxxxx → 5 bits and 6 bits → 11 bits total
                token = ((encoded[0] & 0x1F) << 6) | (encoded[1] & 0x3F)
            elif len(encoded) == 3:
                # 3-byte encoding: 1110xxxx, 10xxxxxx, 10xxxxxx → 4 + 6 + 6 = 16 bits
                token = ((encoded[0] & 0x0F) << 12) | ((encoded[1] & 0x3F) << 6) | (encoded[2] & 0x3F)
            elif len(encoded) == 4:
                # 4-byte encoding: 11110xxx, 10xxxxxx, 10xxxxxx, 10xxxxxx → 3 + 6 + 6 + 6 = 21 bits
                token = ((encoded[0] & 0x07) << 18) | ((encoded[1] & 0x3F) << 12) | ((encoded[2] & 0x3F) << 6) | (encoded[3] & 0x3F)
            else:
                raise ValueError(f"Unexpected UTF‑8 byte length {len(encoded)} for character {char!r}")
            tokens.append(token)
        return tokens

    def detokenize(self, tokens: list[int]) -> str:
        """
        Converts a list of mixed‑radix token integers back to a Unicode string by reconstructing
        the original UTF‑8 byte sequences and decoding them.

        Args:
            tokens (List[int]): A list of token integers.

        Returns:
            str: The reconstructed Unicode string.
        """
        chars = []
        for token in tokens:
            if token < 0x80:
                # 1-byte token (0 to 127)
                b = bytes([token])
            elif token < 0x800:
                # 2-byte token (0x80 to 0x7FF)
                b = bytes([
                    0xC0 | (token >> 6),          # 110xxxxx
                    0x80 | (token & 0x3F)           # 10xxxxxx
                ])
            elif token < 0x10000:
                # 3-byte token (0x800 to 0xFFFF)
                b = bytes([
                    0xE0 | (token >> 12),                      # 1110xxxx
                    0x80 | ((token >> 6) & 0x3F),                # 10xxxxxx
                    0x80 | (token & 0x3F)                        # 10xxxxxx
                ])
            elif token < 0x110000:
                # 4-byte token (0x10000 to 0x10FFFF)
                b = bytes([
                    0xF0 | (token >> 18),                          # 11110xxx
                    0x80 | ((token >> 12) & 0x3F),                   # 10xxxxxx
                    0x80 | ((token >> 6) & 0x3F),                    # 10xxxxxx
                    0x80 | (token & 0x3F)                            # 10xxxxxx
                ])
            else:
                raise ValueError(f"Token {token} is out of Unicode range")
            try:
                chars.append(b.decode('utf-8'))
            except UnicodeDecodeError as e:
                raise ValueError(f"Failed to decode bytes {b} from token {token}: {e}") from e
        return ''.join(chars)


# If run as a script, perform a simple test.
if __name__ == '__main__':
    # Example text containing various Unicode characters (ASCII, CJK, Emoji, etc.)
    sample_text = "Hello, 世界! 👋"
    print("Original text:", sample_text)

    tokenizer = UTF8MixedRadixTokenizer()
    tokens = tokenizer.tokenize(sample_text)
    print("Tokenized (mixed-radix integers):", tokens)

    recovered_text = tokenizer.detokenize(tokens)
    print("Recovered text:", recovered_text)
