def has_break_char(content):
    break_chars = [".", "。", "?", "？", "!", "！", ":", "：", ";", "；"]
    for c in break_chars:
        if c in content:
            return True
    return False
