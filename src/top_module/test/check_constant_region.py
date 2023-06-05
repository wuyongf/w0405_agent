def check_constant_region(lst, range_value):
    for i in range(len(lst) - range_value + 1):
        region = lst[i:i+range_value]
        if len(set(region)) == 1:
            return True
    return False


# Example usage
lst = [1, 2, 3, 3, 3, 4, 5, 6]
range_value = 3
result = check_constant_region(lst, range_value)
print(result)
