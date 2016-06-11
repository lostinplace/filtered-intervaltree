def compute_distribution(a_list):
    result = {}
    for i in a_list:
        value = result.get(i) or 0
        value += 1
        result[i] = value
    return result