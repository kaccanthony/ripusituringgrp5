def details():
    print("\nInsert account details")
    print("\n================================================================================")
    print("1. View Transaction history")
    print("2. Switch account?")
    print("3. Go back to main menu?")
    print("================================================================================")
    deet = input("\nEnter your choice: ")
    if deet == "1":
        print("insert transaction history code here")

    elif deet == "2":
        print("insert switch account code here")

    elif deet == "3":
        print("\nReturning to the main menu...")
        return

    else:
        print("\nInvalid choice. Please enter 1, 2, or 3.")

def main():
    while True:
        print("================================================================================")
        print("WELCOME USER!")
        print("\nWhat do you want to do today?")
        print("1. DEPOSIT")
        print("2. WITHDRAW")
        print("3. CHECK BALANCE")
        print("4. LOAN")
        print("5. INTEREST CALCULATOR")
        print("6. ACCOUNT DETAILS")
        print("7. EXIT")
        print("\n================================================================================")
        choice = input("\nEnter your choice: ")

        if choice == "1":
            print("insert deposit code here")

        elif choice == "2":
            print("insert withdraw code here")

        elif choice == "3":
            print("insert check balance code here")

        elif choice == "4":
            print("insert loan code here")

        elif choice == "5":
            print("insert interest calculator code here")

        elif choice == "6":
            print("insert account details code here")
            details()

        elif choice == "7":
            print("Goodbye!")
            break

        else:
            print("\nInvalid choice. Please enter 1, 2, 3, 4, 5, 6, or 7.")

        print()

if __name__ == "__main__":
    main()