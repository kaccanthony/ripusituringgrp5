# from rich.console import Console
# console = console()

MINIMUM_BALANCE = 500.00
BELOW_MINIMUM_FEE = 300.00

# dummy class, for testing only

class Account:
    def __init__(self, name, balance, acc_number, acc_status):
        self.name = name
        self.balance = balance
        self.acc_number = acc_number
        self.acc_status = acc_status # "Active", "Dormant", "Frozen", "Suspended"

accounts = {
    "ACC001": Account("Alice",  5000.00, "ACC001", "Active"),
    "ACC002": Account("Bob",    1200.00, "ACC002", "Active"),
    "ACC003": Account("Carlos", 800.00,  "ACC003", "Frozen"),
    "ACC004": Account("Diana",  400.00,  "ACC004", "Dormant"),
}

# actual fund transferring function (for my part)

def fundtransfer(sender, receiver, amount):

    # sender -> moves through the access point
    # access point -> send to the receiver

    if sender not in accounts:
        print("Sender account does not exist.")
        return

    if receiver not in accounts:
        print("Receiver account does not exist.")
        return

    sender_acc   = accounts[sender]
    receiver_acc = accounts[receiver]

    BLOCKED_STATUSES = {"Frozen", "Suspended", "Dormant"}

    if sender_acc.acc_status in BLOCKED_STATUSES:
        print(f"Transfer denied: Sender account is {sender_acc.acc_status}.")  # fix 1
        return                                                                  # fix 2

    if sender_acc.balance < amount:                                             # fix 3
        print("Insufficient funds to transfer.")
        return

    sender_acc.balance   -= amount                                              # fix 4
    receiver_acc.balance += amount                                              # fix 4
    print("\033[1mTransaction Successful!\033[0m")
    print(f"{sender_acc.name} new balance: {sender_acc.balance:.2f}") # could be changed to "your new balance"
    print(f"{receiver_acc.name} new balance: {receiver_acc.balance:.2f}") # could be changed cuz ykyk privacy thing

    if sender_acc.balance < MINIMUM_BALANCE: # example warning
        print(f"Warning: {sender_acc.name}'s balance is below the minimum. A fee may be charged.")

# balance fee enforcement

def min_balance_fee(account):
    if account.balance < MINIMUM_BALANCE:
        fee = min(BELOW_MINIMUM_FEE, account.balance)  # don't overdraft beyond zero
        account.balance -= fee
        print(f"Fee of {fee:.2f} applied to {account.name}. New balance: {account.balance:.2f}")

def month_end_sweep():
    for acc in accounts.values():
        min_balance_fee(acc)

fundtransfer("ACC001", "ACC002", 20.00)

month_end_sweep()
print("Hi")