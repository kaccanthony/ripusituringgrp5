# ============================================
# BANK SYSTEM - COMPLETE & ORGANIZED
# ============================================

import datetime
import json
import os
from typing import Optional, List, Dict

# ─────────────────────────────────────────────
#  CONSTANTS
# ─────────────────────────────────────────────

MINIMUM_BALANCE     = 500.00
BELOW_MINIMUM_FEE   = 300.00
FIXED_INTEREST_RATE = 0.75      # annual % for loan calculator
OVERDRAFT_LIMIT     = 100.00
SAVINGS_INTEREST_RATE = 0.04    # annual rate for savings accounts

SEPARATOR = "=" * 55
THIN_SEP  = "-" * 55
HISTORY_FILE = "transaction_history.json"


# ─────────────────────────────────────────────
#  ACCOUNT CLASSES
# ─────────────────────────────────────────────

class BankAccount:
    def __init__(self, account_number: str, name: str, account_type: str, 
                balance: float = 0.0, status: str = "Active"):
        self.account_number = account_number
        self.name = name
        self.account_type = account_type
        self.balance = balance
        self.status = status  # Active | Dormant | Frozen | Suspended
        self.transactions: List[Dict] = []

    def _log_transaction(self, txn_type: str, amount: float):
        txn = {
            "transaction_id": len(self.transactions) + 1,
            "account_number": self.account_number,
            "transaction_type": txn_type,
            "amount": amount,
            "balance_after": self.balance,
            "timestamp": datetime.datetime.now().isoformat()
        }
        self.transactions.append(txn)

    def deposit(self, amount: float) -> bool:
        if amount <= 0:
            print("\n   Deposit amount must be greater than zero.")
            return False
        self.balance += amount
        self._log_transaction("Deposit", amount)
        print(f"\n   Deposited ${amount:,.2f}. New balance: ${self.balance:,.2f}")
        return True

    def withdraw(self, amount: float) -> bool:
        if amount <= 0:
            print("\n   Withdrawal amount must be greater than zero.")
            return False
        if amount > self.balance:
            print(f"\n   Insufficient funds! Current balance: ${self.balance:,.2f}")
            return False
        self.balance -= amount
        self._log_transaction("Withdrawal", -amount)
        print(f"\n   Withdrew ${amount:,.2f}. New balance: ${self.balance:,.2f}")
        return True

    def get_history(self, limit: Optional[int] = 20):
        return sorted(self.transactions, key=lambda x: x["timestamp"], reverse=True)[:limit]


class CheckingAccount(BankAccount):
    def __init__(self, account_number: str, name: str, balance: float = 0.0, status: str = "Active"):
        super().__init__(account_number, name, "Checking", balance, status)
        self.overdraft_limit = OVERDRAFT_LIMIT

    def withdraw(self, amount: float) -> bool:
        if amount <= 0:
            print("\n   Withdrawal amount must be greater than zero.")
            return False
        if amount > self.balance + self.overdraft_limit:
            print(f"\n   Transaction declined! Exceeds ${self.overdraft_limit:.2f} overdraft limit.")
            return False
        self.balance -= amount
        self._log_transaction("Withdrawal", -amount)
        print(f"\n   Withdrew ${amount:,.2f}. New balance: ${self.balance:,.2f}")
        return True


class SavingsAccount(BankAccount):
    def __init__(self, account_number: str, name: str, balance: float = 0.0, status: str = "Active"):
        super().__init__(account_number, name, "Savings", balance, status)
        self.interest_rate = SAVINGS_INTEREST_RATE

    def calculate_interest(self) -> float:
        monthly_rate = self.interest_rate / 12
        return self.balance * monthly_rate

    def apply_interest(self):
        interest = self.calculate_interest()
        if interest > 0:
            self.balance += interest
            self._log_transaction("Interest", interest)
            print(f"   Interest of ${interest:,.2f} applied to {self.name}.")


# ─────────────────────────────────────────────
#  BANK MANAGER
# ─────────────────────────────────────────────

class BankManager:
    def __init__(self):
        self.accounts: Dict[str, BankAccount] = {}
        self._load_test_accounts()
        self._load_transaction_history()

    def _load_test_accounts(self):
        test_data = [
            SavingsAccount("ACC001", "Alice", 5000.00, "Active"),
            CheckingAccount("ACC002", "Bob", 1200.00, "Active"),
            SavingsAccount("ACC003", "Carlos", 800.00, "Frozen"),
            CheckingAccount("ACC004", "Diana", 400.00, "Dormant"),
            SavingsAccount("ACC005", "Eve", 3500.00, "Active"),
        ]
        for acc in test_data:
            self.accounts[acc.account_number] = acc
        print(f"   {len(self.accounts)} test accounts loaded.")

    def _load_transaction_history(self):
        if os.path.exists(HISTORY_FILE):
            try:
                with open(HISTORY_FILE, "r") as f:
                    data = json.load(f)
                    for acc_num, txns in data.items():
                        if acc_num in self.accounts:
                            self.accounts[acc_num].transactions = txns
                print(f"   ✓ Loaded transaction history from {HISTORY_FILE}")
            except Exception as e:
                print(f"   Warning: Could not load history: {e}")

    def save_transaction_history(self):
        data = {acc_num: acc.transactions for acc_num, acc in self.accounts.items()}
        try:
            with open(HISTORY_FILE, "w") as f:
                json.dump(data, f, indent=4)
        except Exception as e:
            print(f"   Warning: Could not save history: {e}")

    # ── Account Management ───────────────────
    def account_exists(self, account_number: str) -> bool:
        return account_number in self.accounts

    def get_account(self, account_number: str) -> Optional[BankAccount]:
        acc = self.accounts.get(account_number)
        if not acc:
            print(f"\n   Account '{account_number}' not found.")
        return acc

    def create_account(self, account_number: str, name: str, account_type: str):
        if account_number in self.accounts:
            print(f"\n    Account {account_number} already exists!")
            return

        if account_type == "1":
            self.accounts[account_number] = SavingsAccount(account_number, name)
            print(f"\n   Savings account [{account_number}] created for {name}.")
        elif account_type == "2":
            self.accounts[account_number] = CheckingAccount(account_number, name)
            print(f"\n   Checking account [{account_number}] created for {name}.")
        else:
            print("\n    Invalid type. Account creation aborted.")
            return

        self.save_transaction_history()

    def display_accounts(self):
        if not self.accounts:
            print("\n  📭 No accounts registered.")
            return
        print(f"\n  {'Acc Number':<12} | {'Name':<14} | {'Type':<10} | {'Status':<12} | {'Balance':>10}")
        print("  " + THIN_SEP)
        for acc in self.accounts.values():
            print(f"  {acc.account_number:<12} | {acc.name:<14} | "
                f"{acc.account_type:<10} | {acc.status:<12} | ${acc.balance:>9,.2f}")

    # ── Transactions ─────────────────────────
    def deposit(self, account_number: str, amount: float):
        acc = self.get_account(account_number)
        if not acc:
            return
        if acc.deposit(amount):
            self._warn_low_balance(acc)
            self.save_transaction_history()

    def withdraw(self, account_number: str, amount: float):
        acc = self.get_account(account_number)
        if not acc:
            return
        blocked = {"Frozen", "Suspended", "Dormant"}
        if acc.status in blocked:
            print(f"\n   Withdrawal denied: account is {acc.status}.")
            return
        if acc.withdraw(amount):
            self._warn_low_balance(acc)
            self.save_transaction_history()

    def fund_transfer(self, sender_num: str, receiver_num: str, amount: float):
        sender = self.get_account(sender_num)
        receiver = self.get_account(receiver_num)
        if not sender or not receiver:
            return

        blocked = {"Frozen", "Suspended", "Dormant"}
        if sender.status in blocked or receiver.status in blocked:
            print("\n   Transfer denied: one or both accounts are blocked.")
            return
        if amount <= 0:
            print("\n   Transfer amount must be greater than zero.")
            return
        if sender.balance < amount:
            print("\n   Insufficient funds to transfer.")
            return

        sender.balance -= amount
        receiver.balance += amount

        sender._log_transaction("Transfer Out", -amount)
        receiver._log_transaction("Transfer In", amount)

        print("\n  \033[1mTransaction Successful!\033[0m")
        print(f"  Your new balance: ${sender.balance:,.2f}")

        self._warn_low_balance(sender)
        self.save_transaction_history()

    def check_balance(self, account_number: str):
        acc = self.get_account(account_number)
        if acc:
            print(f"\n  Account  : {acc.account_number}")
            print(f"  Name     : {acc.name}")
            print(f"  Type     : {acc.account_type}")
            print(f"  Status   : {acc.status}")
            print(f"  Balance  : ${acc.balance:,.2f}")

    def display_account_history(self, account_number: str, limit: int = 20):
        acc = self.get_account(account_number)
        if not acc:
            return

        history = acc.get_history(limit)
        if not history:
            print(f"\nNo transaction history for account {account_number}")
            return

        print("\n" + "=" * 70)
        print(f"TRANSACTION HISTORY - Account: {account_number}".center(70))
        print("=" * 70)
        print(f"{'Date & Time':<22} {'Type':<15} {'Amount':<12} {'Balance':<12}")
        print("-" * 70)

        for t in history:
            ts = datetime.datetime.fromisoformat(t["timestamp"]).strftime("%Y-%m-%d %H:%M:%S")
            print(f"{ts:<22} {t['transaction_type']:<15} "
                  f"${t['amount']:>10,.2f} ${t['balance_after']:>10,.2f}")

        print("-" * 70)

    # ── Maintenance ──────────────────────────
    def _warn_low_balance(self, acc: BankAccount):
        if acc.balance < MINIMUM_BALANCE:
            print(f"\n    Warning: {acc.name}'s balance is below the ${MINIMUM_BALANCE:,.2f} minimum.")

    def _apply_min_balance_fee(self, acc: BankAccount):
        if acc.balance < MINIMUM_BALANCE and acc.balance > 0:
            fee = min(BELOW_MINIMUM_FEE, acc.balance)
            acc.balance -= fee
            acc._log_transaction("Fee", -fee)
            print(f"  Fee of ${fee:,.2f} applied to {acc.name}.")

    def month_end_sweep(self):
        print("\n   Running month-end sweep...")
        for acc in self.accounts.values():
            self._apply_min_balance_fee(acc)
            if isinstance(acc, SavingsAccount):
                acc.apply_interest()
        self.save_transaction_history()
        print("   Month-end sweep complete.")


# ─────────────────────────────────────────────
#  LOAN CALCULATOR
# ─────────────────────────────────────────────

def monthly_payment(principal: float, annual_rate_pct: float, years: int) -> float:
    if years <= 0:
        raise ValueError("Years must be greater than 0.")
    m = annual_rate_pct / 100 / 12
    n = years * 12
    if m == 0:
        return principal / n
    return principal * m / (1 - (1 + m) ** -n)


# ─────────────────────────────────────────────
#  INPUT HELPERS
# ─────────────────────────────────────────────

def section_header(title: str):
    print(f"\n{SEPARATOR}")
    print(f"  {title}")
    print(SEPARATOR)


def prompt_valid_account(bank: BankManager, label: str = "account number") -> Optional[str]:
    while True:
        raw = input(f"\n  Enter {label} (-1 to cancel): ").strip()
        if raw == "-1":
            print("  ↩  Cancelled.")
            return None
        if not raw:
            print("    Account number cannot be empty.")
            continue
        if bank.account_exists(raw):
            return raw
        print(f"   Account '{raw}' not found. Try again.")


def prompt_valid_amount(label: str = "amount") -> Optional[float]:
    while True:
        raw = input(f"  Enter {label} (-1 to cancel): $").strip()
        if raw == "-1":
            print("  ↩  Cancelled.")
            return None
        try:
            return float(raw)
        except ValueError:
            print("   Invalid number. Try again.")


# ─────────────────────────────────────────────
#  MENU ACTIONS
# ─────────────────────────────────────────────

def menu_create_account(bank: BankManager):
    section_header("CREATE NEW ACCOUNT")
    while True:
        acc_num = input("  Enter unique account number (-1 to cancel): ").strip()
        if acc_num == "-1":
            return
        if not acc_num:
            print("    Account number cannot be empty.")
            continue
        if bank.account_exists(acc_num):
            print("    Account already exists.")
            continue
        break

    name = input("  Enter account holder name: ").strip()
    if not name:
        print("    Name cannot be empty.")
        return

    print("  Account Type:\n    1. Savings\n    2. Checking")
    acc_type = input("  Choice (1 or 2): ").strip()
    bank.create_account(acc_num, name, acc_type)


def menu_deposit(bank): 
    section_header("DEPOSIT FUNDS")
    acc_num = prompt_valid_account(bank)
    if acc_num:
        amount = prompt_valid_amount("deposit amount")
        if amount is not None:
            bank.deposit(acc_num, amount)


def menu_withdraw(bank):
    section_header("WITHDRAW FUNDS")
    acc_num = prompt_valid_account(bank)
    if acc_num:
        amount = prompt_valid_amount("withdrawal amount")
        if amount is not None:
            bank.withdraw(acc_num, amount)


def menu_check_balance(bank):
    section_header("CHECK BALANCE")
    acc_num = prompt_valid_account(bank)
    if acc_num:
        bank.check_balance(acc_num)


def menu_fund_transfer(bank):
    section_header("FUND TRANSFER")
    sender = prompt_valid_account(bank, "sender account number")
    if not sender: return
    receiver = prompt_valid_account(bank, "receiver account number")
    if not receiver: return
    amount = prompt_valid_amount("transfer amount")
    if amount is not None:
        bank.fund_transfer(sender, receiver, amount)


def menu_loan_calculator(bank=None):
    section_header("LOAN CALCULATOR")
    try:
        principal = float(input("  Loan amount: $").strip())
        years = int(input("  Loan term (years): ").strip())
        pay = monthly_payment(principal, FIXED_INTEREST_RATE, years)
        total = pay * years * 12
        interest = total - principal

        print(f"\n  {THIN_SEP}")
        print(f"  Monthly payment : ${pay:>12,.2f}")
        print(f"  Total payment   : ${total:>12,.2f}")
        print(f"  Total interest  : ${interest:>12,.2f}")
        print(f"  {THIN_SEP}")
        print("    Pay on time to avoid late fees.")
    except ValueError as e:
        print(f"   Input error: {e}")


def menu_account_details(bank):
    section_header("ACCOUNT DETAILS")
    acc_num = prompt_valid_account(bank)
    if not acc_num:
        return

    while True:
        bank.check_balance(acc_num)
        print(f"\n  {THIN_SEP}")
        print("  1. View Transaction History")
        print("  2. Switch Account")
        print("  3. Back to Main Menu")
        print(f"  {THIN_SEP}")

        choice = input("  Enter your choice: ").strip()
        if choice == "1":
            bank.display_account_history(acc_num)
        elif choice == "2":
            new_num = prompt_valid_account(bank, "new account number")
            if new_num:
                acc_num = new_num
        elif choice == "3":
            break
        else:
            print("    Invalid choice.")


def menu_view_all_accounts(bank):
    section_header("ALL REGISTERED ACCOUNTS")
    bank.display_accounts()


def menu_month_end_sweep(bank):
    section_header("MONTH-END SWEEP")
    if input("  Run sweep? (y/n): ").strip().lower() == "y":
        bank.month_end_sweep()
    else:
        print("  Cancelled.")


# ─────────────────────────────────────────────
#  MAIN MENU
# ─────────────────────────────────────────────

MENU_OPTIONS = [
    ("1",  "Create New Account",  menu_create_account),
    ("2",  "Deposit",             menu_deposit),
    ("3",  "Withdraw",            menu_withdraw),
    ("4",  "Check Balance",       menu_check_balance),
    ("5",  "Fund Transfer",       menu_fund_transfer),
    ("6",  "Loan Calculator",     menu_loan_calculator),
    ("7",  "Account Details",     menu_account_details),
    ("8",  "View All Accounts",   menu_view_all_accounts),
    ("9",  "Month-End Sweep",     menu_month_end_sweep),
    ("10", "Exit",                None),
]


def print_main_menu():
    print(f"\n{SEPARATOR}")
    print("       BANK PERSISTENCE SYSTEM")
    print(SEPARATOR)
    for key, label, _ in MENU_OPTIONS:
        print(f"  {key:>2}. {label}")
    print(SEPARATOR)


def main():
    print(f"\n{SEPARATOR}")
    print("  Initializing Bank System...")
    print(SEPARATOR)

    bank = BankManager()

    while True:
        print_main_menu()
        choice = input("\n  Enter your choice: ").strip()

        if choice == "10":
            print("\n   Goodbye!\n")
            break

        # Find and call the matching function
        for key, _, func in MENU_OPTIONS:
            if key == choice:
                if func:
                    func(bank)
                break
        else:
            print(f"\n    Invalid option. Please enter 1–{len(MENU_OPTIONS)}.")


if __name__ == "__main__":
    main()
