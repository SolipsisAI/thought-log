from enum import Enum, EnumMeta


class MetaEnum(EnumMeta):
    def __contains__(cls, item):
        try:
            cls(item)
        except ValueError:
            return False
        return True


class SupportedFiletypes(Enum, metaclass=MetaEnum):
    ZIP = "application/zip"
    PLAIN = "text/plain"
    MARKDOWN = "text/markdown"
    CSV = "text/csv"
    JSON = "application/json"
