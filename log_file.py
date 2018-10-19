import ctypes
import json

HEAD = b'\xA3\x95'
CHUNK_SIZE = 100


SCALARS = {
        'b': ctypes.c_int8,
        'B': ctypes.c_uint8,
        'h': ctypes.c_int16,
        'H': ctypes.c_uint16,
        'i': ctypes.c_int32,
        'I': ctypes.c_uint32,
        'f': ctypes.c_float,
        'd': ctypes.c_double,
        'n': ctypes.c_char * 4,
        'N': ctypes.c_char * 16,
        'Z': ctypes.c_char * 64,
        'c': ctypes.c_int16,
        'C': ctypes.c_uint16,
        'e': ctypes.c_int32,
        'E': ctypes.c_uint32,
        'L': ctypes.c_int32,
        'M': ctypes.c_uint8,
        'q': ctypes.c_int64,
        'Q': ctypes.c_uint64,
}


class DataPoint:
    def __init__(self, name):
        self.name = name
        self.values = {}

    def __repr__(self):
        return "[%s %s]" % (self.name, json.dumps(self.values))


class Format:
    def __init__(self, msg):
        assert(len(msg) == 86)

        self._id = int(msg[0])
        self._length = int(msg[1])
        self._name = msg[2:6].decode("utf-8")
        self._types = msg[6:22].split(b'\x00')[0].decode("utf-8")
        self._labels = msg[22:].split(b'\x00')[0].decode("utf-8").split(",")

        assert(len(self._types) == len(self._labels))

    def create_datapoint(self, msg):
        if len(msg) + 3 != self._length:
            return None

        result = DataPoint(self._name)

        offset = 0
        for t, l in zip(self._types, self._labels):
            val = SCALARS[t].from_buffer(msg, offset)
            offset += ctypes.sizeof(val)

            val = val.value
            if isinstance(val, bytes):
                val = val.decode('utf-8')
            result.values[l] = val

        return result


class LogFile:
    def __init__(self, filename):
        self._filename = filename
        self._formats = {}

    def _yield_messages(self, f):
        buf = bytearray()
        chunk = f.read(CHUNK_SIZE)

        while chunk:
            buf += chunk
            head = buf.find(HEAD, len(HEAD))

            while head != -1:
                msg = buf[:head]
                buf = buf[head:]
                yield msg

                head = buf.find(HEAD, len(HEAD))

            chunk = f.read(CHUNK_SIZE)

    def read(self):
        total_bytes = 0
        print("Reading %s..." % self._filename)
        with open(self._filename, 'rb') as f:
            for msg in self._yield_messages(f):
                total_bytes += len(msg)
                if(len(msg) <= len(HEAD)):
                    print("\tWARNING: Bad message")
                    continue

                msg_id = int(msg[len(HEAD)])
                msg = msg[len(HEAD)+1:]

                if msg_id == 0x80:
                    """
                    Format definition
                    """
                    fmt_id = int(msg[0])
                    self._formats[fmt_id] = Format(msg)
                else:
                    if msg_id not in self._formats:
                        print("\tWARNING: Could not find format %0.2X"
                              % msg_id)
                        continue

                    result = self._formats[msg_id].create_datapoint(msg)
                    if result is None:
                        print("\tWARNING: Bad message")
                    else:
                        yield result

        print("...read %d bytes" % total_bytes)


if __name__ == '__main__':
    import sys

    for dp in LogFile(sys.argv[1]).read():
        print(dp)
