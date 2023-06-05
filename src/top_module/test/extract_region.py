
def extract_region(lst, i_start, i_end):
    if i_start < 0 or i_end >= len(lst) or i_start > i_end:
        return None
    
    region = lst[i_start:i_end+1]
    return region

# Example usage
lst = [1, 2, 3, 4, 5, 6]
i_start = 1
i_end = 4

result = extract_region(lst, i_start, i_end)
print(result)
