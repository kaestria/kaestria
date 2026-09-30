import re
import struct
import hashlib
from typing import Any
OPCODE_VAR_STR = 0x10
OPCODE_VAR_INT = 0x11
OPCODE_VAR_BOOL = 0x12
OPCODE_SET = 0x13
OPCODE_PRINT = 0x20
OPCODE_PRINTLN = 0x21
OPCODE_IF = 0x30
OPCODE_ELIF = 0x31
OPCODE_ELSE = 0x32
OPCODE_ENDIF = 0x33
OPCODE_WHILE = 0x34
OPCODE_ENDWHILE = 0x35
OPCODE_BREAK = 0x36
OPCODE_CONTINUE = 0x37
OPCODE_SIGNAL = 0x38
OPCODE_EMIT = 0x39
OPCODE_TRY = 0x3A
OPCODE_CATCH = 0x3B
OPCODE_ENDTRY = 0x3C
OPCODE_THROW = 0x3D
OPCODE_ERRGET = 0x3E
OPCODE_FUNC = 0x40
OPCODE_ENDFUNC = 0x41
OPCODE_CALL = 0x42
OPCODE_RETURN = 0x43
OPCODE_ROUND = 0x44
OPCODE_FLOOR = 0x45
OPCODE_CEIL = 0x46
OPCODE_SQRT = 0x47
OPCODE_POW = 0x48
OPCODE_ABS = 0x49
OPCODE_ISODD = 0x4A
OPCODE_ISEVEN = 0x4B
OPCODE_PARAM = 0x4C
OPCODE_CALLP = 0x4D
OPCODE_ADD = 0x50
OPCODE_SUB = 0x51
OPCODE_MUL = 0x52
OPCODE_DIV = 0x53
OPCODE_MOD = 0x54
OPCODE_ISINT = 0x55
OPCODE_INTPARSE = 0x56
OPCODE_INTSTR = 0x57
OPCODE_INTCLAMP = 0x58
OPCODE_FDIV = 0x59
OPCODE_MIN = 0x5A
OPCODE_MAX = 0x5B
OPCODE_EQ = 0x60
OPCODE_NEQ = 0x61
OPCODE_LT = 0x62
OPCODE_GT = 0x63
OPCODE_LTE = 0x64
OPCODE_GTE = 0x65
OPCODE_AND = 0x66
OPCODE_OR = 0x67
OPCODE_NOT = 0x68
OPCODE_STRIS = 0x69
OPCODE_STRFIND = 0x6A
OPCODE_STRREPLACE = 0x6B
OPCODE_STRTRIM = 0x6C
OPCODE_STRSTARTS = 0x6D
OPCODE_STRENDS = 0x6E
OPCODE_STRREV = 0x6F
OPCODE_CONCAT = 0x70
OPCODE_STRLEN = 0x71
OPCODE_SUBSTR = 0x72
OPCODE_UPPER = 0x73
OPCODE_LOWER = 0x74
OPCODE_SPLIT = 0x75
OPCODE_STRJOIN = 0x76
OPCODE_STRCHAR = 0x77
OPCODE_STRPAD = 0x78
OPCODE_STRREPEAT = 0x79
OPCODE_STRCOUNT = 0x7A
OPCODE_STRCMP = 0x7B
OPCODE_STRSLICE = 0x7C
OPCODE_LIST = 0x80
OPCODE_LISTGET = 0x81
OPCODE_LISTLEN = 0x82
OPCODE_LISTAPPEND = 0x83
OPCODE_LISTSET = 0x84
OPCODE_LISTREMOVE = 0x85
OPCODE_LISTCONTAINS = 0x86
OPCODE_LISTJOIN = 0x87
OPCODE_ARRCREATE = 0x88
OPCODE_SORT = 0x89
OPCODE_REVERSE = 0x8A
OPCODE_SLICE = 0x8B
OPCODE_INDEXOF = 0x8C
OPCODE_UNIQUE = 0x8D
OPCODE_RANGE = 0x8E
OPCODE_FOPEN = 0x90
OPCODE_FREAD = 0x91
OPCODE_FWRITE = 0x92
OPCODE_FAPPEND = 0x93
OPCODE_FDELETE = 0x94
OPCODE_FEXISTS = 0x95
OPCODE_MKDIR = 0x96
OPCODE_FREADLINE = 0x97
OPCODE_FWRITELINE = 0x98
OPCODE_FLEN = 0x99
OPCODE_PATHJOIN = 0x9A
OPCODE_PATHBASE = 0x9B
OPCODE_PATHDIR = 0x9C
OPCODE_PATHEXISTS = 0x9D
OPCODE_FLIST = 0x9E
OPCODE_FCOPY = 0x9F
OPCODE_HTTPGET = 0xA0
OPCODE_HTTPPOST = 0xA1
OPCODE_HTTPDOWN = 0xA2
OPCODE_JSONPARSE = 0xA3
OPCODE_JSONSTR = 0xA4
OPCODE_JSONGET = 0xA5
OPCODE_JSONSET = 0xA6
OPCODE_HTTPFILE = 0xA7
OPCODE_NETINFO = 0xA8
OPCODE_ZIP = 0xA9
OPCODE_UNZIP = 0xAA
OPCODE_FMOVE = 0xAB
OPCODE_FSTAT = 0xAC
OPCODE_FTOUCH = 0xAD
OPCODE_URLENCODE = 0xAE
OPCODE_URLDECODE = 0xAF
OPCODE_SOCKCONN = 0xB0
OPCODE_SOCKSEND = 0xB1
OPCODE_SOCKRECV = 0xB2
OPCODE_SOCKCLOSE = 0xB3
OPCODE_OSNAME = 0xB4
OPCODE_OSARCH = 0xB5
OPCODE_OSLANG = 0xB6
OPCODE_OSHOST = 0xB7
OPCODE_HTTPSTATUS = 0xB8
OPCODE_HTTPTIMEOUT = 0xB9
OPCODE_HTTPGETH = 0xBA
OPCODE_HTTPPOSTH = 0xBB
OPCODE_SERVERBIND = 0xC0
OPCODE_SERVERLSTN = 0xC1
OPCODE_SERVERACCPT = 0xC2
OPCODE_SERVERSEND = 0xC3
OPCODE_SERVERRECV = 0xC4
OPCODE_SERVERCLS = 0xC5
OPCODE_DATE = 0xC6
OPCODE_DATEDMY = 0xC7
OPCODE_WEEKDAY = 0xC8
OPCODE_DAYOFYEAR = 0xC9
OPCODE_MONTH = 0xCA
OPCODE_YEAR = 0xCB
OPCODE_DAY = 0xCC
OPCODE_TIME = 0xCD
OPCODE_HOUR = 0xCE
OPCODE_MINUTE = 0xCF
OPCODE_ARGS = 0xD0
OPCODE_ARGGET = 0xD1
OPCODE_ARGLEN = 0xD2
OPCODE_SECOND = 0xD3
OPCODE_TIMESTAMP = 0xD4
OPCODE_SLEEP = 0xD5
OPCODE_FPS = 0xD6
OPCODE_TICK = 0xD7
OPCODE_SCHEDULE = 0xD8
OPCODE_IMPORT = 0xE0
OPCODE_RANDINT = 0xE1
OPCODE_RANDSTR = 0xE2
OPCODE_RANDCHOICE = 0xE3
OPCODE_UUID = 0xE4
OPCODE_HASH = 0xE5
OPCODE_HASHSHA256 = 0xE6
OPCODE_HASHMD5 = 0xE7
OPCODE_ENCRYPT = 0xE8
OPCODE_DECRYPT = 0xE9
OPCODE_SHELLEXEC = 0xF0
OPCODE_EXIT = 0xFF
MNEMONIC_MAP = {
    "STR": OPCODE_VAR_STR,
    "INT": OPCODE_VAR_INT,
    "BOOL": OPCODE_VAR_BOOL,
    "SET": OPCODE_SET,
    "PRINT": OPCODE_PRINT,
    "PRINTLN": OPCODE_PRINTLN,
    "IF": OPCODE_IF,
    "ELIF": OPCODE_ELIF,
    "ELSE": OPCODE_ELSE,
    "ENDIF": OPCODE_ENDIF,
    "WHILE": OPCODE_WHILE,
    "ENDWHILE": OPCODE_ENDWHILE,
    "BREAK": OPCODE_BREAK,
    "CONTINUE": OPCODE_CONTINUE,
    "SIGNAL": OPCODE_SIGNAL,
    "EMIT": OPCODE_EMIT,
    "FUNC": OPCODE_FUNC,
    "ENDFUNC": OPCODE_ENDFUNC,
    "CALL": OPCODE_CALL,
    "RETURN": OPCODE_RETURN,
    "ROUND": OPCODE_ROUND,
    "FLOOR": OPCODE_FLOOR,
    "CEIL": OPCODE_CEIL,
    "SQRT": OPCODE_SQRT,
    "POW": OPCODE_POW,
    "ABS": OPCODE_ABS,
    "ISODD": OPCODE_ISODD,
    "ISEVEN": OPCODE_ISEVEN,
    "ADD": OPCODE_ADD,
    "SUB": OPCODE_SUB,
    "MUL": OPCODE_MUL,
    "DIV": OPCODE_DIV,
    "MOD": OPCODE_MOD,
    "ISINT": OPCODE_ISINT,
    "INTPARSE": OPCODE_INTPARSE,
    "INTSTR": OPCODE_INTSTR,
    "INTCLAMP": OPCODE_INTCLAMP,
    "EQ": OPCODE_EQ,
    "NEQ": OPCODE_NEQ,
    "LT": OPCODE_LT,
    "GT": OPCODE_GT,
    "LTE": OPCODE_LTE,
    "GTE": OPCODE_GTE,
    "AND": OPCODE_AND,
    "OR": OPCODE_OR,
    "NOT": OPCODE_NOT,
    "STRIS": OPCODE_STRIS,
    "STRFIND": OPCODE_STRFIND,
    "STRREPLACE": OPCODE_STRREPLACE,
    "STRTRIM": OPCODE_STRTRIM,
    "STRSTARTS": OPCODE_STRSTARTS,
    "STRENDS": OPCODE_STRENDS,
    "STRREV": OPCODE_STRREV,
    "CONCAT": OPCODE_CONCAT,
    "STRLEN": OPCODE_STRLEN,
    "SUBSTR": OPCODE_SUBSTR,
    "UPPER": OPCODE_UPPER,
    "LOWER": OPCODE_LOWER,
    "SPLIT": OPCODE_SPLIT,
    "STRJOIN": OPCODE_STRJOIN,
    "STRCHAR": OPCODE_STRCHAR,
    "LIST": OPCODE_LIST,
    "LISTGET": OPCODE_LISTGET,
    "LISTLEN": OPCODE_LISTLEN,
    "LISTAPPEND": OPCODE_LISTAPPEND,
    "LISTSET": OPCODE_LISTSET,
    "LISTREMOVE": OPCODE_LISTREMOVE,
    "LISTCONTAINS": OPCODE_LISTCONTAINS,
    "LISTJOIN": OPCODE_LISTJOIN,
    "ARRCREATE": OPCODE_ARRCREATE,
    "ARRAY": OPCODE_ARRCREATE,
    "FOPEN": OPCODE_FOPEN,
    "FREAD": OPCODE_FREAD,
    "FWRITE": OPCODE_FWRITE,
    "FAPPEND": OPCODE_FAPPEND,
    "FDELETE": OPCODE_FDELETE,
    "FEXISTS": OPCODE_FEXISTS,
    "MKDIR": OPCODE_MKDIR,
    "FREADLINE": OPCODE_FREADLINE,
    "FWRITELINE": OPCODE_FWRITELINE,
    "FLEN": OPCODE_FLEN,
    "PATHJOIN": OPCODE_PATHJOIN,
    "PATHBASE": OPCODE_PATHBASE,
    "PATHDIR": OPCODE_PATHDIR,
    "PATHEXISTS": OPCODE_PATHEXISTS,
    "FLIST": OPCODE_FLIST,
    "HTTPGET": OPCODE_HTTPGET,
    "HTTPPOST": OPCODE_HTTPPOST,
    "HTTPDOWN": OPCODE_HTTPDOWN,
    "JSONPARSE": OPCODE_JSONPARSE,
    "JSONSTR": OPCODE_JSONSTR,
    "JSONGET": OPCODE_JSONGET,
    "JSONSET": OPCODE_JSONSET,
    "HTTPFILE": OPCODE_HTTPFILE,
    "NETINFO": OPCODE_NETINFO,
    "ZIP": OPCODE_ZIP,
    "UNZIP": OPCODE_UNZIP,
    "SOCKCONN": OPCODE_SOCKCONN,
    "SOCKSEND": OPCODE_SOCKSEND,
    "SOCKRECV": OPCODE_SOCKRECV,
    "SOCKCLOSE": OPCODE_SOCKCLOSE,
    "OSNAME": OPCODE_OSNAME,
    "OSARCH": OPCODE_OSARCH,
    "OSLANG": OPCODE_OSLANG,
    "OSHOST": OPCODE_OSHOST,
    "SERVERBIND": OPCODE_SERVERBIND,
    "SERVERLSTN": OPCODE_SERVERLSTN,
    "SERVERACCPT": OPCODE_SERVERACCPT,
    "SERVERSEND": OPCODE_SERVERSEND,
    "SERVERRECV": OPCODE_SERVERRECV,
    "SERVERCLS": OPCODE_SERVERCLS,
    "DATE": OPCODE_DATE,
    "DATEDMY": OPCODE_DATEDMY,
    "WEEKDAY": OPCODE_WEEKDAY,
    "DAYOFYEAR": OPCODE_DAYOFYEAR,
    "MONTH": OPCODE_MONTH,
    "YEAR": OPCODE_YEAR,
    "DAY": OPCODE_DAY,
    "TIME": OPCODE_TIME,
    "HOUR": OPCODE_HOUR,
    "MINUTE": OPCODE_MINUTE,
    "ARGS": OPCODE_ARGS,
    "ARGGET": OPCODE_ARGGET,
    "ARGLEN": OPCODE_ARGLEN,
    "SECOND": OPCODE_SECOND,
    "TIMESTAMP": OPCODE_TIMESTAMP,
    "SLEEP": OPCODE_SLEEP,
    "FPS": OPCODE_FPS,
    "TICK": OPCODE_TICK,
    "SCHEDULE": OPCODE_SCHEDULE,
    "IMPORT": OPCODE_IMPORT,
    "RANDINT": OPCODE_RANDINT,
    "RANDSTR": OPCODE_RANDSTR,
    "RANDCHOICE": OPCODE_RANDCHOICE,
    "UUID": OPCODE_UUID,
    "HASH": OPCODE_HASH,
    "HASHSHA256": OPCODE_HASHSHA256,
    "HASHMD5": OPCODE_HASHMD5,
    "ENCRYPT": OPCODE_ENCRYPT,
    "DECRYPT": OPCODE_DECRYPT,
    "SHELLEXEC": OPCODE_SHELLEXEC,
    "EXIT": OPCODE_EXIT,
    "TRY": OPCODE_TRY,
    "CATCH": OPCODE_CATCH,
    "ENDTRY": OPCODE_ENDTRY,
    "THROW": OPCODE_THROW,
    "ERRGET": OPCODE_ERRGET,
    "PARAM": OPCODE_PARAM,
    "CALLP": OPCODE_CALLP,
    "FDIV": OPCODE_FDIV,
    "MIN": OPCODE_MIN,
    "MAX": OPCODE_MAX,
    "STRPAD": OPCODE_STRPAD,
    "STRREPEAT": OPCODE_STRREPEAT,
    "STRCOUNT": OPCODE_STRCOUNT,
    "STRCMP": OPCODE_STRCMP,
    "STRSLICE": OPCODE_STRSLICE,
    "SORT": OPCODE_SORT,
    "REVERSE": OPCODE_REVERSE,
    "SLICE": OPCODE_SLICE,
    "INDEXOF": OPCODE_INDEXOF,
    "UNIQUE": OPCODE_UNIQUE,
    "RANGE": OPCODE_RANGE,
    "FCOPY": OPCODE_FCOPY,
    "FMOVE": OPCODE_FMOVE,
    "FSTAT": OPCODE_FSTAT,
    "FTOUCH": OPCODE_FTOUCH,
    "URLENCODE": OPCODE_URLENCODE,
    "URLDECODE": OPCODE_URLDECODE,
    "HTTPSTATUS": OPCODE_HTTPSTATUS,
    "HTTPTIMEOUT": OPCODE_HTTPTIMEOUT,
    "HTTPGETH": OPCODE_HTTPGETH,
    "HTTPPOSTH": OPCODE_HTTPPOSTH,
}
def _encodeStr(s: str) -> bytes:
    encoded = s.encode("utf-8")
    return struct.pack(">H", len(encoded)) + encoded
def _encodeInt(n: int) -> bytes:
    return struct.pack(">q", n)
def _encodeBool(b: bool) -> bytes:
    return struct.pack("B", 1 if b else 0)
def _encodeToken(tok: str) -> bytes:
    data = tok.encode("utf-8")
    return struct.pack(">H", len(data)) + data
class Compiler:
    def __init__(self):
        self.output = bytearray()
        self.errors = []
    def _emit(self, byte: int):
        self.output.append(byte)
    def _emitBytes(self, data: bytes):
        self.output.extend(data)
    def _parseValue(self, token: str):
        t = token.strip()
        if t.startswith('"') and t.endswith('"'):
            return ("str", t[1:-1])
        if t.lower() in ("true", "1"):
            return ("bool", True)
        if t.lower() in ("false", "0"):
            return ("bool", False)
        try:
            return ("int", int(t))
        except ValueError:
            return ("ref", t)
    def _emitValue(self, valType: str, val: Any):
        if valType == "str":
            self._emit(0x01)
            self._emitBytes(_encodeStr(val))
        elif valType == "int":
            self._emit(0x02)
            self._emitBytes(_encodeInt(val))
        elif valType == "bool":
            self._emit(0x03)
            self._emitBytes(_encodeBool(val))
        elif valType == "ref":
            self._emit(0x04)
            self._emitBytes(_encodeToken(val))
    def _emitSingleValue(self, args: list):
        val = " ".join(args)
        if val:
            if not val.startswith('"') and not val.lstrip("-").isdigit() and val.lower() not in ("true", "false", "0", "1"):
                self._emitValue("str", val)
            else:
                vt, vv = self._parseValue(val)
                self._emitValue(vt, vv)
        else:
            self._emit(0x00)
    def _emitDestSingle(self, args: list):
        if len(args) >= 2:
            self._emitBytes(_encodeToken(args[0]))
            vt, vv = self._parseValue(args[1])
            self._emitValue(vt, vv)
    def _emitDestDouble(self, args: list):
        if len(args) >= 3:
            self._emitBytes(_encodeToken(args[0]))
            vt1, vv1 = self._parseValue(args[1])
            self._emitValue(vt1, vv1)
            vt2, vv2 = self._parseValue(" ".join(args[2:]))
            self._emitValue(vt2, vv2)
    def _emitDestTriple(self, args: list):
        if len(args) >= 4:
            self._emitBytes(_encodeToken(args[0]))
            vt1, vv1 = self._parseValue(args[1])
            self._emitValue(vt1, vv1)
            vt2, vv2 = self._parseValue(args[2])
            self._emitValue(vt2, vv2)
            vt3, vv3 = self._parseValue(" ".join(args[3:]))
            self._emitValue(vt3, vv3)
    def _emitDestOnly(self, args: list):
        if args:
            self._emitBytes(_encodeToken(args[0]))
    def compileLine(self, line: str):
        line = re.sub(r'<!--.*?-->', '', line).strip()
        if not line:
            return
        parts = self._tokenize(line)
        if not parts:
            return
        mnemonic = parts[0].upper()
        args = parts[1:]
        if mnemonic not in MNEMONIC_MAP:
            self.errors.append(f"Unknown mnemonic: {mnemonic}")
            return
        opcode = MNEMONIC_MAP[mnemonic]
        self._emit(opcode)
        if mnemonic in ("STR", "INT", "BOOL"):
            if len(args) >= 2:
                self._emitBytes(_encodeToken(args[0]))
                vt, vv = self._parseValue(" ".join(args[1:]))
                self._emitValue(vt, vv)
            elif len(args) == 1:
                self._emitBytes(_encodeToken(args[0]))
                if mnemonic == "STR":
                    self._emitValue("str", "")
                elif mnemonic == "INT":
                    self._emitValue("int", 0)
                elif mnemonic == "BOOL":
                    self._emitValue("bool", False)
        elif mnemonic == "SET":
            if len(args) >= 2:
                self._emitBytes(_encodeToken(args[0]))
                vt, vv = self._parseValue(" ".join(args[1:]))
                self._emitValue(vt, vv)
        elif mnemonic in ("PRINT", "PRINTLN", "IF", "ELIF", "WHILE"):
            val = " ".join(args)
            vt, vv = self._parseValue(val)
            self._emitValue(vt, vv)
        elif mnemonic in ("ELSE", "ENDIF", "ENDWHILE", "BREAK", "CONTINUE", "ENDFUNC", "EXIT", "TRY", "ENDTRY"):
            pass
        elif mnemonic == "FUNC":
            if args:
                self._emitBytes(_encodeToken(args[0]))
        elif mnemonic in ("CALL", "IMPORT", "SIGNAL", "EMIT", "SLEEP", "HTTPTIMEOUT", "FTOUCH"):
            self._emitSingleValue(args)
        elif mnemonic in ("RETURN", "THROW"):
            val = " ".join(args)
            vt, vv = self._parseValue(val)
            self._emitValue(vt, vv)
        elif mnemonic in ("ADD", "SUB", "MUL", "DIV", "MOD", "EQ", "NEQ", "LT", "GT", "LTE", "GTE", "AND", "OR", "CONCAT", "POW", "STRFIND", "STRSTARTS", "STRENDS", "STRCHAR", "STRJOIN", "LISTCONTAINS", "LISTJOIN", "JSONGET", "PATHJOIN", "ENCRYPT", "DECRYPT", "RANDINT", "RANDSTR", "HTTPPOST", "SOCKCONN", "FREADLINE", "LISTGET", "FDIV", "MIN", "MAX", "STRREPEAT", "STRCOUNT", "STRCMP", "INDEXOF", "RANGE", "HTTPGETH", "HTTPPOSTH"):
            self._emitDestDouble(args)
        elif mnemonic in ("NOT", "STRLEN", "UPPER", "LOWER", "LISTLEN", "LISTAPPEND", "LISTREMOVE", "FOPEN", "FREAD", "FEXISTS", "HTTPGET", "HTTPDOWN", "HTTPFILE", "JSONPARSE", "JSONSTR", "ROUND", "FLOOR", "CEIL", "SQRT", "ABS", "ISODD", "ISEVEN", "ISINT", "INTPARSE", "INTSTR", "STRIS", "STRTRIM", "STRREV", "FLEN", "PATHBASE", "PATHDIR", "PATHEXISTS", "FLIST", "HASH", "HASHSHA256", "HASHMD5", "RANDCHOICE", "SOCKRECV", "SOCKCLOSE", "SERVERACCPT", "SERVERCLS", "ARGGET", "SHELLEXEC", "SCHEDULE", "FSTAT", "URLENCODE", "URLDECODE", "HTTPSTATUS", "UNIQUE", "SORT", "REVERSE"):
            self._emitDestSingle(args)
        elif mnemonic in ("SUBSTR", "STRREPLACE", "JSONSET", "INTCLAMP", "STRPAD", "STRSLICE", "SLICE"):
            self._emitDestTriple(args)
        elif mnemonic == "CALLP":
            if len(args) >= 2:
                self._emitBytes(_encodeToken(args[0]))
                funcName = args[1]
                if funcName.startswith('"') and funcName.endswith('"'):
                    funcName = funcName[1:-1]
                self._emitValue("str", funcName)
                rest = args[2:]
                self._emit(len(rest))
                for a in rest:
                    vt, vv = self._parseValue(a)
                    self._emitValue(vt, vv)
        elif mnemonic == "LIST" or mnemonic == "ARRAY" or mnemonic == "ARRCREATE":
            if args:
                self._emitBytes(_encodeToken(args[0]))
                self._emit(len(args) - 1)
                for a in args[1:]:
                    vt, vv = self._parseValue(a)
                    self._emitValue(vt, vv)
        elif mnemonic == "LISTSET":
            if len(args) >= 3:
                self._emitBytes(_encodeToken(args[0]))
                vt1, vv1 = self._parseValue(args[1])
                self._emitValue(vt1, vv1)
                vt2, vv2 = self._parseValue(" ".join(args[2:]))
                self._emitValue(vt2, vv2)
        elif mnemonic in ("FWRITE", "FAPPEND", "ZIP", "UNZIP", "FCOPY", "FMOVE"):
            if len(args) >= 2:
                vt1, vv1 = self._parseValue(args[0])
                self._emitValue(vt1, vv1)
                vt2, vv2 = self._parseValue(" ".join(args[1:]))
                self._emitValue(vt2, vv2)
        elif mnemonic == "FWRITELINE":
            if len(args) >= 3:
                vt1, vv1 = self._parseValue(args[0])
                self._emitValue(vt1, vv1)
                vt2, vv2 = self._parseValue(args[1])
                self._emitValue(vt2, vv2)
                vt3, vv3 = self._parseValue(" ".join(args[2:]))
                self._emitValue(vt3, vv3)
        elif mnemonic in ("FDELETE", "MKDIR"):
            if args:
                vt, vv = self._parseValue(args[0])
                self._emitValue(vt, vv)
        elif mnemonic in ("CATCH", "ERRGET", "PARAM"):
            self._emitDestOnly(args)
        elif mnemonic in ("SOCKSEND", "SERVERSEND"):
            if len(args) >= 2:
                vt1, vv1 = self._parseValue(args[0])
                self._emitValue(vt1, vv1)
                vt2, vv2 = self._parseValue(" ".join(args[2 - 1:]))
                self._emitValue(vt2, vv2)
        elif mnemonic == "SERVERBIND":
            if len(args) >= 2:
                self._emitBytes(_encodeToken(args[0]))
                vt, vv = self._parseValue(args[1])
                self._emitValue(vt, vv)
        elif mnemonic == "SERVERLSTN":
            if args:
                vt, vv = self._parseValue(args[0])
                self._emitValue(vt, vv)
        elif mnemonic == "SERVERRECV":
            if len(args) >= 2:
                vt1, vv1 = self._parseValue(args[0])
                self._emitValue(vt1, vv1)
                vt2, vv2 = self._parseValue(" ".join(args[1:]))
                self._emitValue(vt2, vv2)
        elif mnemonic == "ARGS" or mnemonic == "ARGLEN":
            self._emitDestOnly(args)
        elif mnemonic == "OSNAME" or mnemonic == "OSARCH" or mnemonic == "OSLANG" or mnemonic == "OSHOST":
            self._emitDestOnly(args)
        elif mnemonic == "DATE" or mnemonic == "DATEDMY" or mnemonic == "WEEKDAY" or mnemonic == "DAYOFYEAR" or mnemonic == "MONTH" or mnemonic == "YEAR" or mnemonic == "DAY":
            self._emitDestOnly(args)
        elif mnemonic == "TIME" or mnemonic == "HOUR" or mnemonic == "MINUTE" or mnemonic == "SECOND" or mnemonic == "TIMESTAMP" or mnemonic == "FPS" or mnemonic == "TICK":
            self._emitDestOnly(args)
        elif mnemonic == "UUID" or mnemonic == "NETINFO":
            self._emitDestOnly(args)
    def _tokenize(self, line: str) -> list:
        tokens = []
        current = ""
        inQuote = False
        i = 0
        while i < len(line):
            c = line[i]
            if c == '"' and not inQuote:
                inQuote = True
                current += c
            elif c == '"' and inQuote:
                inQuote = False
                current += c
            elif c == ' ' and not inQuote:
                if current:
                    tokens.append(current)
                    current = ""
            else:
                current += c
            i += 1
        if current:
            tokens.append(current)
        return tokens
    def compile(self, source: str) -> bytes:
        self.output = bytearray()
        self.errors = []
        for line in source.splitlines():
            self.compileLine(line)
        if self.errors:
            raise ValueError("Compile errors:\n" + "\n".join(self.errors))
        return bytes(self.output)
    def toHexFile(self, bytecode: bytes) -> str:
        lines = []
        i = 0
        rowLen = 16
        while i < len(bytecode):
            chunk = bytecode[i:i+rowLen]
            hexPart = " ".join(f"{b:02x}" for b in chunk)
            obfKey = hashlib.md5(str(i).encode()).hexdigest()[:4]
            lines.append(f"0x{obfKey} {hexPart}")
            i += rowLen
        return "\n".join(lines)
def compileSource(source: str) -> str:
    c = Compiler()
    bytecode = c.compile(source)
    return c.toHexFile(bytecode)
def fromHexFile(content: str) -> bytes:
    result = bytearray()
    for line in content.splitlines():
        line = line.strip()
        if not line:
            continue
        parts = line.split()
        if len(parts) < 2:
            continue
        hexBytes = parts[1:]
        for h in hexBytes:
            try:
                result.append(int(h, 16))
            except ValueError:
                pass
    return bytes(result)
