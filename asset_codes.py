import re

def valid_asset_code(value):
    return isinstance(value, str) and bool(
        re.fullmatch(r"AST-[0-9]{4}", value)
    )
