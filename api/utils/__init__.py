def rename_keys(d, key_map: dict):
    if isinstance(d, dict):
        return {key_map.get(k, k): rename_keys(v, key_map) for k, v in d.items()}
    elif isinstance(d, list):
        return [rename_keys(item, key_map) for item in d]
    else:
        return d
