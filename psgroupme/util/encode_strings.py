def encode_strings(data):
    if isinstance(data, str):
        return str(data)
    elif isinstance(data, list):
        return [encode_strings(x) for x in data]
    elif isinstance(data, dict):
        res = {}
        for k, v in data.items():
            res[encode_strings(k)] = encode_strings(v)
        return res
    return data
