
class ByteHelper:
    def int_to_bytes(self, int_value: int) -> bytes:
        return int_value.to_bytes((int_value.bit_length() + 7) // 8, 'big')

    def byte(self, number, i):
        return (number & (0xff << (i * 8))) >> (i * 8)

    def bytes_to_int(self, bytes_value: bytes) -> int:
        return int.from_bytes(bytes_value, "big")