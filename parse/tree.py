import itertools
import collections

Location = collections.namedtuple('Location', 'start, end, filename, first_line')


class StructMixIn:

    infix       = False
    closed      = False
    indented    = False
    traversable = False

  ### TOKEN AUTOLOCATION

    def in_between(self, left, right):

        self.location = Location(
            left.location.start,
            right.location.end,
            right.location.filename,
            left.location.first_line
        )
        return self

    def before(self, other):

        self.location = Location(
            other.location.start,
            other.location.start,
            other.location.filename,
            other.location.first_line
        )
        return self

    def after(self, other):

        self.location = Location(
            other.location.end,
            other.location.end,
            other.location.filename,
            other.location.first_line
        )
        return self

    def at(self, stream):

        self.location = Location(
            stream.position(stream.pstack[-1]),
            stream.position(stream.offset),
            stream.filename,
            stream.line(stream.pstack[-1])
        )
        return self


class Expression (list, StructMixIn):

    traversable = property(lambda self: not self.closed)


class Link (str, StructMixIn):

    def __new__(cls, data, infix=False):

        obj = str.__new__(cls, data)
        obj.infix = bool(infix)
        return obj


class Constant (StructMixIn):

    def __init__(self, value):

        super().__init__()
        self.value = value


class Internal (Constant):

    pass


def match(code, pattern, into):

    if isinstance(pattern, Link) and pattern == '_':

        # `_` matches anything.
        into.append(code)
        return True

    if isinstance(code, Expression):

        return (
            isinstance(pattern, type(code)) and
            len(code) == len(pattern)       and
            all(map(match, code, pattern, itertools.repeat(into)))
        )

    return type(code) == type(pattern) and code == pattern


def matchA(code, pattern):

    into = []
    return into if match(code, pattern, into) else []


def matchQ(code, pattern):

    return match(code, pattern, [])
