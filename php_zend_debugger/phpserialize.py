from io import BytesIO

class Decoder:

    def decode_value(self, val, encoding='UTF-8'):
        self.offset = 0
        self.value = val.encode(encoding=encoding)
        self.length = len(self.value)
        self.marked_offset = 0
        return self.decode()


    def decode(self):
        t = self.read_type()

        if t == b'i':
            return self.decode_int()
        elif t == b'd':
            return self.decode_double()
        elif t == b's':
            return self.decode_string()
        elif t == b'b':
            return self.decode_bool()
        elif t == b'r':
            return self.decode_resource()
        elif t == b'a':
            return self.decode_array()
        elif t == b'O':
            return self.decode_object()
        elif t == b'N':
            return None

        return 'UNKNOWN TYPE' + str(t)

    def decode_int(self):
        return self.read_int()

    def decode_double(self):
        return float(self.read_token())

    def decode_string(self):
        return self.read_string()

    def decode_bool(self):
        return True if self.read_token() == b'1' else False

    def decode_resource(self):
        resource_number = self.read_int()
        self.read_int()

        value = self.read_token()

        return "RESOURCE (%d) of type (%s)" % (resource_number, value)

    def decode_array(self):
        object_length = self.read_int()
        original_length = object_length

        if self.is_last_end():
            object_length = 0

        result = []

        numeric_keys = True
        last_value = -1

        for i in range(object_length):
            t = self.read_type()

            is_int = False
            if t == b'i':
                name = self.read_int()
                is_int = True
            else:
                name = self.read_string()

            value = self.decode()

            result.append((name, value))

            if numeric_keys and (not is_int or (name - 1 != last_value)):
                numeric_keys = False
            else:
                last_value = name

        if numeric_keys:
            return [val for (key,val) in result]
        else:
            res = {}
            for (key, value) in result:
                res[key] = value

            return res

    def decode_object(self):
        class_name = self.read_string()
        object_length = self.read_int()

        if self.is_last_end():
            object_length = 0

        result = {}

        for i in range(object_length):
            t = self.read_type()
            if t == b'i':
                name = self.read_int()
            else:
                name = self.read_string()

            value = self.decode()

            result[name] = value

        return { 'OBJECT_TYPE': class_name, 'attributes': result}

    def read_type(self):
        first = True

        while first or (ch in [b';', b':', b'{', b'}']):
            first = False
            if self.eof():
                # EOF
                return b' '

            ch = self.read()

        return ch

    def read_token(self):
        result = b''
        first = True
        while first or (ch in [b';', b':']):
            first = False
            ch = self.read()

        while not ch in [b';', b':']:
            result += ch
            ch = self.read()

        return result.decode(encoding='UTF-8')

    def read_string(self):
        length = self.read_int()
        ch = self.read()
        while ch != b'"':
            ch = self.read()

        result = self.read_many(length)
        # Read "
        self.read()

        return result.decode(encoding='UTF-8')

    def read_int(self):
        result = 0
        is_negative = False

        digits = [b'0', b'1', b'2', b'3', b'4', b'5', b'6', b'7', b'8', b'9']

        first = True
        while first or (not ch in digits):
            first = False
            ch = self.read()
            if ch == b'-':
                is_negative = True

        first = True

        while first or (ch in digits):
            first = False
            result *= 10
            result += int(ch)
            self.mark()
            ch = self.read()

        if is_negative:
            result *= -1

        return result

    def is_last_end(self):
        self.reset()
        ch = self.read()
        return ch == b';'

        return result

    def eof(self):
        return self.offset == self.length

    def read(self):
        if self.eof():
            raise Exception("Unexpected end of input")
        val = self.value[self.offset:self.offset+1]
        self.offset += 1
        return val

    def read_many(self, amount):
        result = b''

        while amount > 0:
            result += self.read()
            amount -= 1

        return result

    def mark(self):
        self.marked_offset = self.offset

    def reset(self):
        self.offset = self.marked_offset
