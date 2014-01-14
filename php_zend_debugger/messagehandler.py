import struct

class MessageHandler:
    messages = {
        2005: {
            'id': 'MSG_SESS_START',
            'format': [
                ('protocol_id', '!i'),
                ('filename', 's'),
                ('uri', 's'),
                ('query', 's'),
                ('mode', 's')
            ]
        },
        2002: {
            'id': 'MSG_SCRIPT_END',
            'format': [
                ('status', '!i')
            ]
        },
        2003: {
            'id': 'MSG_READY',
            'format': [
                ('filename', 's'),
                ('lineno', '!i')
            ]
        },
        2004: {
            'id': 'MSG_OUTPUT',
            'format': [
                ('text', 's')
            ]
        },
        2008: {
            'id': 'MSG_HEADER_OUTPUT',
            'format': [
                ('text', 's')
            ]
        },
        2009: {
            'id': 'MSG_START_PROCESS_FILE',
            'format': [
                ('filename', 's')
            ]
        },
        2006: {
            'id': 'MSG_PHP_ERROR',
            'format': [
                ('type', '!i'),
                ('filename', 's'),
                ('lineno', '!i'),
                ('error', 's')
            ]
        },
        2007: {
            'id': 'MSG_ERROR',
            'format': [
                ('message', 's')
            ]
        },
        # Request messages
        1: {
            'id': 'MSG_START',
            'format': [
                ('req_id', '!i')
            ]
        },
        2: {
            'id': 'MSG_STOP',
            'format': [
                ('req_id', '!i')
            ]
        },
        3: {
            'id': 'MSG_SESS_CLOSE',
            'format': []
        },
        4: {
            'id': 'MSG_SET_OPTIONS',
            'format': [
                ('req_id', '!i'),
                ('options', '!i')
            ]
        },
        11: {
            'id': 'MSG_STEP_INTO',
            'format': [
                ('req_id', '!i')
            ]
        },
        12: {
            'id': 'MSG_STEP_OVER',
            'format': [
                ('req_id', '!i')
            ]
        },
        13: {
            'id': 'MSG_STEP_OUT',
            'format': [
                ('req_id', '!i')
            ]
        },
        14: {
            'id': 'MSG_GO',
            'format': [
                ('req_id', '!i')
            ]
        },
        21: {
            'id': 'MSG_ADD_BREAKPOINT',
            'format': [
                ('req_id', '!i'),
                ('type', '!h'),
                ('lifetime', '!h'),
                ('file', 's'),
                ('lineno', '!i')
            ]
        },
        22: {
            'id': 'MSG_DEL_BREAKPOINT',
            'format': [
                ('req_id', '!i'),
                ('bp_id', '!i')
            ]
        },
        23: {
            'id': 'MSG_DEL_ALL_BREAKPOINTS',
            'format': [
                ('req_id', '!i')
            ]
        },
        31: {
            'id': 'MSG_EVAL',
            'format': [
                ('req_id', '!i'),
                ('expr', 's')
            ]
        },
        32: {
            'id': 'MSG_GET_VAR',
            'format': [
                ('req_id', '!i'),
                ('var_expression', 's'),
                ('depth', '!i'),
                ('path', ['s'])
            ]
        },
        33: {
            'id': 'MSG_ASSIGN_VAR',
            'format': [
                ('req_id', '!i'),
                ('var_expression', 's'),
                ('val_expression', 's'),
                ('depth', '!i'),
                ('path', ['s'])
            ]
        },
        34: {
            'id': 'MSG_GET_CALL_STACK',
            'format': [
                ('req_id', '!i')
            ]
        },
        35: {
            'id': 'MSG_GET_STACK_VAR',
            'format': [
                ('req_id', '!i'),
                ('stack_depth', '!i'),
                ('var_name', 's'),
                ('depth', '!i'),
                ('path', ['s'])
            ]
        },
        10000: {
            'id': 'MSG_SET_PROTOCOL',
            'format': [
                ('req_id', '!i'),
                ('protocol_id', '!i')
            ]
        },
        2010: {
            'id': 'MSG_CONTINUE_PROCESS_FILE',
            'format': []
        },
        # Response messages
        1000: {
            'id': 'MSG_DONT_UNDERSTAND_R',
            'format': [
                ('req_id', '!i'),
                ('type', '!i')
            ]
        },
        1001: {
            'id': 'MSG_START_R',
            'format': [
                ('req_id', '!i'),
                ('status', '!i')
            ]
        },
        1002: {
            'id': 'MSG_STOP_R',
            'format': [
                ('req_id', '!i'),
                ('status', '!i')
            ]
        },
        1003: {
            'id': 'MSG_SESS_CLOSE_R',
            'format': [
                ('req_id', '!i'),
                ('status', '!i')
            ]
        },
        1004: {
            'id': 'MSG_SET_OPTIONS_R',
            'format': [
                ('req_id', '!i'),
                ('status', '!i')
            ]
        },
        1011: {
            'id': 'MSG_STEP_INTO_R',
            'format': [
                ('req_id', '!i'),
                ('status', '!i')
            ]
        },
        1012: {
            'id': 'MSG_STEP_OVER_R',
            'format': [
                ('req_id', '!i'),
                ('status', '!i')
            ]
        },
        1013: {
            'id': 'MSG_STEP_OUT_R',
            'format': [
                ('req_id', '!i'),
                ('status', '!i')
            ]
        },
        1014: {
            'id': 'MSG_GO_R',
            'format': [
                ('req_id', '!i'),
                ('status', '!i')
            ]
        },
        1021: {
            'id': 'MSG_ADD_BREAKPOINT_R',
            'format': [
                ('req_id', '!i'),
                ('status', '!i'),
                ('breakpoint_id', '!i')
            ]
        },
        1022: {
            'id': 'MSG_DEL_BREAKPOINT_R',
            'format': [
                ('req_id', '!i'),
                ('status', '!i')
            ]
        },
        1023: {
            'id': 'MSG_DEL_BREAKPOINTS_R',
            'format': [
                ('req_id', '!i'),
                ('status', '!i')
            ]
        },
        1031: {
            'id': 'MSG_EVAL_R',
            'format': [
                ('req_id', '!i'),
                ('status', '!i'),
                ('result', 's')
            ]
        },
        1032: {
            'id': 'MSG_GET_VAR_R',
            'format': [
                ('req_id', '!i'),
                ('status', '!i'),
                ('variable', 's')
            ]
        },
        1033: {
            'id': 'MSG_ASSIGN_VAR_R',
            'format': [
                ('req_id', '!i'),
                ('status', '!i')
            ]
        },
        1034: {
            'id': 'MSG_GET_CALLSTACK_R',
            'format': [
                ('req_id', '!i'),
                ('callstack', [
                    [
                        ('caller_filename', 's'),
                        ('caller_lineno', '!i'),
                        ('caller_function', 's'),
                        ('called_filename', 's'),
                        ('called_lineno', '!i'),
                        ('called_function', 's'),
                        ('params', [
                            [
                                ('name', 's'),
                                ('value', 's')
                            ]
                        ])
                    ]
                ])
            ]
        },
        11000: {
            'id': 'MSG_SET_PROTOCOL_R',
            'format': [
                ('req_id', '!i'),
                ('protocol_id', '!i')
            ]
        },
        1035: {
            'id': 'MSG_GET_STACK_VAR_R',
            'format': [
                ('req_id', '!i'),
                ('status', '!i'),
                ('variable', 's')
            ]
        }
    }

    message_ids = {
        'MSG_SESS_START': 2005,
        'MSG_SCRIPT_END': 2002,
        'MSG_READY': 2003,
        'MSG_OUTPUT': 2004,
        'MSG_START_PROCESS_FILE': 2009,
        'MSG_HEADER_OUTPUT': 2008,
        'MSG_PHP_ERROR': 2006,
        'MSG_ERROR': 2007,
        'MSG_START': 1,
        'MSG_STOP': 2,
        'MSG_SESS_CLOSE': 3,
        'MSG_SET_OPTIONS': 4,
        'MSG_STEP_INTO': 11,
        'MSG_STEP_OVER': 12,
        'MSG_STEP_OUT': 13,
        'MSG_GO': 14,
        'MSG_ADD_BREAKPOINT': 21,
        'MSG_DEL_BREAKPOINT': 22,
        'MSG_DEL_ALL_BREAKPOINTS': 23,
        'MSG_EVAL': 31,
        'MSG_GET_VAR': 32,
        'MSG_ASSIGN_VAR': 33,
        'MSG_GET_CALL_STACK': 34,
        'MSG_GET_STACK_VAR': 35,
        'MSG_SET_PROTOCOL': 10000,
        'MSG_CONTINUE_PROCESS_FILE': 2010,
        'MSG_DONT_UNDERSTAND_R': 1000,
        'MSG_START_R': 1001,
        'MSG_STOP_R': 1002,
        'MSG_SESS_CLOSE_R': 1003,
        'MSG_SET_OPTIONS_R': 1004,
        'MSG_STEP_INTO_R': 1011,
        'MSG_STEP_OVER_R': 1012,
        'MSG_STEP_OUT_R': 1013,
        'MSG_GO_R': 1014,
        'MSG_ADD_BREAKPOINT_R': 1021,
        'MSG_DEL_BREAKPOINT_R': 1022,
        'MSG_DEL_BREAKPOINTS_R': 1023,
        'MSG_EVAL_R': 1031,
        'MSG_GET_VAR_R': 1032,
        'MSG_ASSIGN_VAR_R': 1033,
        'MSG_GET_CALLSTACK_R': 1034,
        'MSG_SET_PROTOCOL_R': 11000,
        'MSG_GET_STACK_VAR_R': 1035
    }

    @staticmethod
    def read(value, format, offset):
        result, = struct.unpack_from(format, value, offset)
        return result

    @staticmethod
    def read_message(value):
        message_id = MessageHandler.read(value, '!h', 0)

        if not (message_id in MessageHandler.messages):
            raise Exception(
                'Could not find message with id: ' +
                str(message_id)
            )

        msg = MessageHandler.messages[message_id]

        if msg['id'] != 'MSG_ADD_BREAKPOINT':
            result, offset = MessageHandler.read_format(
                value, msg['format'], 2
            )
            result['id'] = msg['id']
        else:
            offset = 2
            result = {}
            result['id'] = msg['id']
            result['req_id'], offset = MessageHandler.read_format_string(
                value, '!i', offset
            )
            result['type'], offset = MessageHandler.read_format_string(
                value, '!h', offset
            )
            result['lifetime'], offset = MessageHandler.read_format_string(
                value, '!h', offset
            )
            if result['type'] & 2 == 2:
                condition, offset = MessageHandler.read_format_string(
                    value, 's', offset
                )
                result['condition'] = condition
                if result['type'] & 1 != 1:
                    return result

            result['file'], offset = MessageHandler.read_format_string(
                value, 's', offset
            )
            if result['type'] & 1 == 1:
                result['lineno'], offset = MessageHandler.read_format_string(
                    value, '!i', offset
                )

        return result

    @staticmethod
    def encode_message(message):
        if not 'id' in message:
            raise Exception("id key not found in message")
        id = message['id']
        if not id in MessageHandler.message_ids:
            raise Exception("Coud not find id for " + id)

        id = MessageHandler.message_ids[id]
        msg = MessageHandler.messages[id]
        result = struct.pack('!h', id)
        result += MessageHandler.encode_format(message, msg['format'])

        length = struct.pack('!i', len(result))

        return length + result

    @staticmethod
    def read_format_string(value, format, offset):
        if format == 's':
            str_length = MessageHandler.read(value, '!i', offset)
            return MessageHandler.read(
                value, str(str_length) + 's', offset+4
            ).decode(encoding='UTF-8'), offset+4+str_length
        else:
            return MessageHandler.read(
                value, format, offset
            ), offset+struct.calcsize(format)

    @staticmethod
    def encode_format_string(value, format):
        if format == 's':
            bytes_string = value.encode(encoding='UTF-8')
            length = struct.pack('!i', len(bytes_string))
            return length + bytes_string
        else:
            return struct.pack(format, value)

    @staticmethod
    def read_format(value, format, offset):
        if MessageHandler.is_string(format):
            return MessageHandler.read_format_string(value, format, offset)
        # at this point format will always be a list
        elif len(format) == 0:
            return {}, offset
        elif type(format[0]) == tuple:
            return MessageHandler.read_format_tuple(value, format, offset)
        else:
            return MessageHandler.read_format_array(value, format, offset)

    @staticmethod
    def encode_format(value, format):
        if MessageHandler.is_string(format):
            return MessageHandler.encode_format_string(value, format)
        # at this point format will always be a list
        elif len(format) == 0:
            return b''
        elif type(format[0]) == tuple:
            return MessageHandler.encode_format_tuple(value, format)
        else:
            return MessageHandler.encode_format_array(value, format[0])

    @staticmethod
    def read_format_tuple(value, format, offset):
        result = {}
        for key, value_format in format:
            result[key], offset = MessageHandler.read_format(
                value, value_format, offset
            )

        return result, offset

    @staticmethod
    def encode_format_tuple(value, format):
        result = b''
        for key, value_format in format:
            result += MessageHandler.encode_format(value[key], value_format)

        return result

    @staticmethod
    def read_format_array(value, format, offset):
        # format should here be an array
        array_length, offset = MessageHandler.read_format_string(
            value, '!i', offset
        )
        result = []
        i = 0
        while i < array_length:
            r, offset = MessageHandler.read_format(value, format[0], offset)
            result.append(r)
            i += 1

        return result, offset

    @staticmethod
    def encode_format_array(value, format):
        array_length = len(value)
        result = struct.pack('!i', array_length)
        i = 0
        while i < array_length:
            result += MessageHandler.encode_format(value[i], format)
        return result

    @staticmethod
    def is_string(x):
        try:
            return isinstance(x, str)
        except:
            return isinstance(x, basestring)

    @staticmethod
    def hexdump(src, length=16):
        FILTER = ''.join(
            [(len(repr(chr(x))) == 3) and chr(x) or '.' for x in range(256)]
        )
        lines = []
        for c in xrange(0, len(src), length):
            chars = src[c:c+length]
            hex = ' '.join(["%02x" % ord(x) for x in chars])
            printable = ''.join(
                [
                    "%s" %
                        ((ord(x) <= 127 and FILTER[ord(x)]) or '.')
                    for x in chars
                ]
            )
            lines.append("%04x  %-*s  %s\n" % (c, length*3, hex, printable))
        print(''.join(lines))
