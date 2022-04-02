from collections import namedtuple

Status = namedtuple('Status', ['pub', 'priv', 'ffo'])
status = Status(pub="публичный", priv="сообществу", ffo="для друзей")
