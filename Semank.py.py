import json
import os

class BankAccount:
    def __init__(self, account_number, account_type, balance=0.0):
        self.account_number = account_number
        self.account_type = account_type
        self.balance = balance

    def deposit(self, amount):
        if amount <= 0:
            print("\n❌ Validation Error: Deposit amount must be greater than zero.")
            return False
        self.balance += amount
        print(f"\n✅ Deposited ${amount:.2f}. New balance: ${self.balance:.2f}")
        return True

    def withdraw(self, amount):
        if amount <= 0:
            print("\n❌ Validation Error: Withdrawal amount must be greater than zero.")
            return False
        if amount > self.balance:
            print(f"\n❌ Validation Error: Insufficient funds! Current balance is ${self.balance:.2f}.")
            return False
        self.balance -= amount
        print(f"\n✅ Withdrew ${amount:.2f}. New balance: ${self.balance:.2f}")
        return True

    def to_dict(self):
        return {
            "account_number": self.account_number,
            "account_type": self.account_type,
            "balance": self.balance
        }

class CheckingAccount(BankAccount):
    def __init__(self, account_number, balance=0.0, overdraft_limit=100.0):
        super().__init__(account_number, "Checking", balance)
        self.overdraft_limit = overdraft_limit

    def withdraw(self, amount):
        if amount <= 0:
            print("\n❌ Validation Error: Withdrawal amount must be greater than zero.")
            return False
        if amount > self.balance + self.overdraft_limit:
            print(f"\n❌ Validation Error: Transaction declined! Exceeds ${self.overdraft_limit:.2f} overdraft limit.")
            return False
        self.balance -= amount
        print(f"\n✅ Withdrew ${amount:.2f}. New balance: ${self.balance:.2f}")
        return True

class SavingsAccount(BankAccount):
    def __init__(self, account_number, balance=0.0):
        super().__init__(account_number, "Savings", balance)

class BankManager:
    def __init__(self, filename="bank_database.json"):
        self.filename = filename
        self.accounts = {}
        self.load_data()

    def load_data(self):
        if os.path.exists(self.filename):
            with open(self.filename, 'r') as file:
                try:
                    data = json.load(file)
                    for acc_num, acc_data in data.items():
                        if acc_data["account_type"] == "Checking":
                            self.accounts[acc_num] = CheckingAccount(acc_num, acc_data["balance"])
                        else:
                            self.accounts[acc_num] = SavingsAccount(acc_num, acc_data["balance"])
                    print(f"📁 Loaded {len(self.accounts)} accounts from database.")
                except json.JSONDecodeError:
                    print("⚠️ Database file corrupted or empty. Starting fresh.")
        else:
            print("🆕 No existing database found. Starting fresh.")

    def save_data(self):
        with open(self.filename, 'w') as file:
            data = {acc_num: acc.to_dict() for acc_num, acc in self.accounts.items()}
            json.dump(data, file, indent=4)

    def create_account(self, account_number, account_type):
        if account_number in self.accounts:
            print(f"\n⚠️ Account {account_number} already exists!")
            return
        
        if account_type == '1':
            self.accounts[account_number] = SavingsAccount(account_number)
            print(f"\n🌟 Savings account {account_number} created successfully.")
        elif account_type == '2':
            self.accounts[account_number] = CheckingAccount(account_number)
            print(f"\n🌟 Checking account {account_number} created successfully.")
        else:
            print("\n⚠️ Invalid selection. Account creation aborted.")
            return
        
        self.save_data()

    def process_transaction(self, account_number, action, amount):
        if account_number not in self.accounts:
            print("\n⚠️ Account not found!")
            return
        
        account = self.accounts[account_number]
        success = False
        
        if action == '1':
            success = account.deposit(amount)
        elif action == '2':
            success = account.withdraw(amount)
        
        if success:
            self.save_data()

    def display_accounts(self):
        if not self.accounts:
            print("\n📭 No accounts registered in the system.")
            return
        print("\n=== Registered Accounts ===")
        print(f"{'Acc Number':<12} | {'Type':<10} | {'Balance':<10}")
        print("-" * 38)
        for acc_num, acc in self.accounts.items():
            print(f"{acc_num:<12} | {acc.account_type:<10} | ${acc.balance:<10.2f}")


# --- Interactive User Interface Loop ---
def main():
    bank = BankManager()
    
    while True:
        print("\n==============================")
        print("      BANK PERSISTENCE CLI    ")
        print("==============================")
        print("1. Create New Account")
        print("2. Deposit Funds")
        print("3. Withdraw Funds")
        print("4. View All Accounts")
        print("5. Exit Application")
        
        choice = input("\nEnter your choice (1-5): ").strip()
        
        if choice == '1':
            acc_num = input("Enter a unique account number: ").strip()
            if not acc_num:
                print("⚠️ Account number cannot be empty.")
                continue
            print("Select Account Type:")
            print("1. Savings")
            print("2. Checking")
            acc_type = input("Choice (1 or 2): ").strip()
            bank.create_account(acc_num, acc_type)
            
        elif choice == '2':
            acc_num = input("Enter account number: ").strip()
            try:
                amount = float(input("Enter deposit amount: $"))
                bank.process_transaction(acc_num, '1', amount)
            except ValueError:
                print("❌ Invalid input! Please enter a numerical value for amount.")
                
        elif choice == '3':
            acc_num = input("Enter account number: ").strip()
            try:
                amount = float(input("Enter withdrawal amount: $"))
                bank.process_transaction(acc_num, '2', amount)
            except ValueError:
                print("❌ Invalid input! Please enter a numerical value for amount.")
                
        elif choice == '4':
            bank.display_accounts()
            
        elif choice == '5':
            print("\n💾 Data automatically synced. Goodbye!")
            break
        else:
            print("\n⚠️ Invalid option. Please enter a number between 1 and 5.")

if __name__ == "__main__":
    main()