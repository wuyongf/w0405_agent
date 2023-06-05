def calculate_rate_of_change(numbers):
    rates = []

    for i in range(1, len(numbers)):
        rate = (numbers[i] - numbers[i-1]) / numbers[i-1]
        rates.append(rate)

    return rates