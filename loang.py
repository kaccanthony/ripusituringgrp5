def monthly_payment(p: float, r: float, years: int) -> float:
    if years <= 0:
        raise ValueError("Years must be greater than 0.")

    m = r / 100 / 12
    n = years * 12
    if m == 0:
        return p / n

    return p * m / (1 - (1 + m) ** -n)


if __name__ == "__main__":
    try:
        print("================================================================================")
        p = float(input("Loan amount: "))
        r = 0.75
        years = int(input("Loan term in years: "))

        pay = monthly_payment(p, r, years)
        total = pay * years * 12
        interest = total - p
        print("================================================================================")
        print(f"Monthly payment: ${pay:,.2f}")
        print(f"Total payment:   ${total:,.2f}")
        print(f"Total interest:  ${interest:,.2f}")
        print("================================================================================")
        print("Make sure to pay on time to avoid late fees and additional interest charges.")
        print("\nThank you for taking a loan with us!")
        print("================================================================================")
    except ValueError as error:
        print(f"Input error: {error}")


