import re

def quote_split(str):
    return [p.strip("\" ") for p in re.split("( |[\\\"'].*[\\\"'])", str) if p.strip("\" ")]