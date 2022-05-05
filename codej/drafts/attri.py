from collections import namedtuple

Status = namedtuple('Status', ['pub', 'priv', 'hidden', 'draft', 'mod'])
status = Status(
    pub="публичный",
    priv="сообществу",
    hidden="в ленту",
    draft="черновик",
    mod="модерация")
