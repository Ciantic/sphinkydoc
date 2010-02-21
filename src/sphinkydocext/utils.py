import re

def quote_split(str):
    return [p for p in re.split("( |[\\\"'].*[\\\"'])", str) if p.strip()]