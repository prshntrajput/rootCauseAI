def calculate_total(prices):
    total = 0
    for price in prices:
        total = total + price  # Bug: price might be string
    return total

def main():
    items = ["10", "20", "30"]  # Strings instead of numbers
    result = calculate_total(items)
    print(f"Total: {result}")

if __name__ == "__main__":
    main()
