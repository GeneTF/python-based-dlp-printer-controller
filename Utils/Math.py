

def clamp(value, min_in, max_in):
    if value > max_in:
        return max_in
    elif value < min_in:
        return min_in
    else:
        return value
