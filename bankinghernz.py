import datetime
import json
import os

# ============================================
# FEATURE 1: INTEREST CALCULATION FOR SAVINGS ACCOUNTS
# ============================================

class SavingsAccount:
    """Savings account with interest calculation"""
    
    def __init__(self, account_number, account_holder, balance=0, interest_rate=0.04):
        self.account_number = account_number
        self.account_holder = account_holder
        self.balance = balance
        self.interest_rate = interest_rate  # 4% default annual interest rate
    
    def calculate_interest(self):
        """
        Calculate monthly interest for savings account
        Returns: interest amount
        """
        # Monthly interest = (Annual rate / 12) * current balance
        monthly_rate = self.interest_rate / 12
        interest = self.balance * monthly_rate
        return interest
    
    def apply_interest(self):
        """
        Apply interest to the account balance
        Returns: interest amount added
        """
        interest = self.calculate_interest()
        if interest > 0:
            self.balance += interest
        return interest


# ============================================
# FEATURE 2: TRANSACTION HISTORY WITH TIMESTAMPS
# ============================================

class Transaction:
    """Represents a single transaction with timestamp"""
    
    def __init__(self, transaction_id, account_number, transaction_type, amount, balance_after):
        self.transaction_id = transaction_id
        self.account_number = account_number
        self.transaction_type = transaction_type  # 'deposit', 'withdrawal', 'interest', 'transfer'
        self.amount = amount
        self.balance_after = balance_after
        self.timestamp = datetime.datetime.now()
    
    def to_dict(self):
        """Convert to dictionary for JSON storage"""
        return {
            'transaction_id': self.transaction_id,
            'account_number': self.account_number,
            'transaction_type': self.transaction_type,
            'amount': self.amount,
            'balance_after': self.balance_after,
            'timestamp': self.timestamp.isoformat()
        }
    
    @staticmethod
    def from_dict(data):
        """Create transaction from dictionary"""
        trans = Transaction(
            data['transaction_id'],
            data['account_number'],
            data['transaction_type'],
            data['amount'],
            data['balance_after']
        )
        trans.timestamp = datetime.datetime.fromisoformat(data['timestamp'])
        return trans
    
    def display(self):
        """Display transaction details"""
        timestamp_str = self.timestamp.strftime("%Y-%m-%d %H:%M:%S")
        print(f"[{timestamp_str}] {self.transaction_type}: ${self.amount:.2f} | Balance: ${self.balance_after:.2f}")


class TransactionHistory:
    """Manages transaction history for accounts"""
    
    def __init__(self, history_file='transaction_history.json'):
        self.history_file = history_file
        self.transactions = []
        self.next_id = 1
        self.load_history()
    
    def load_history(self):
        """Load transaction history from file"""
        if os.path.exists(self.history_file):
            try:
                with open(self.history_file, 'r') as f:
                    data = json.load(f)
                    self.transactions = [Transaction.from_dict(t) for t in data.get('transactions', [])]
                    self.next_id = data.get('next_id', 1)
                print(f"✓ Loaded {len(self.transactions)} transactions")
            except:
                print("! No transaction history found, starting fresh")
    
    def save_history(self):
        """Save transaction history to file"""
        with open(self.history_file, 'w') as f:
            json.dump({
                'transactions': [t.to_dict() for t in self.transactions],
                'next_id': self.next_id
            }, f, indent=4)
    
    def add_transaction(self, account_number, transaction_type, amount, balance_after):
        """
        Add a new transaction to history with timestamp
        Returns: transaction object
        """
        transaction = Transaction(
            self.next_id,
            account_number,
            transaction_type,
            amount,
            balance_after
        )
        self.transactions.append(transaction)
        self.next_id += 1
        self.save_history()
        return transaction
    
    def get_account_history(self, account_number, limit=None):
        """
        Get transaction history for a specific account
        Returns: list of transactions sorted newest first
        """
        account_txns = [t for t in self.transactions if t.account_number == account_number]
        # Sort by timestamp (newest first)
        account_txns.sort(key=lambda x: x.timestamp, reverse=True)
        
        if limit:
            return account_txns[:limit]
        return account_txns
    
    def display_history(self, account_number, limit=20):
        """Display transaction history for an account"""
        history = self.get_account_history(account_number, limit)
        
        if not history:
            print(f"\n📭 No transaction history found for account {account_number}")
            return
        
        print(f"\n{'='*70}")
        print(f"TRANSACTION HISTORY - Account: {account_number}".center(70))
        print(f"{'='*70}")
        print(f"{'Date & Time':<22} {'Type':<12} {'Amount':<12} {'Balance':<12}")
        print("-"*70)
        
        for t in history:
            timestamp_str = t.timestamp.strftime("%Y-%m-%d %H:%M:%S")
            print(f"{timestamp_str:<22} {t.transaction_type:<12} ${t.amount:<11.2f} ${t.balance_after:<11.2f}")
        
        print("-"*70)
        total_txns = len(self.get_account_history(account_number))
        if total_txns > limit:
            print(f"(Showing last {limit} of {total_txns} transactions)")
    
    def get_all_transactions(self):
        """Get all transactions"""
        return sorted(self.transactions, key=lambda x: x.timestamp, reverse=True)
