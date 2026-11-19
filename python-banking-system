from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime


@dataclass
class Transaction:
  """Represents a single account activity entry."""

  tx_type: str
  amount: float
  balance_after: float
  note: str = ""
  timestamp: str = field(
      default_factory=lambda: datetime.now().strftime("%Y-%m-%d %H:%M:%S")
  )


class BankAccount(ABC):
  """Abstract base class encapsulating shared bank account behavior."""

  def __init__(
      self, account_number: str, owner_name: str, initial_balance: float = 0.0
  ) -> None:
    if initial_balance < 0:
      raise ValueError("Initial balance cannot be negative.")
    self.account_number = account_number.strip()
    self.owner_name = owner_name.strip()
    self._balance = round(float(initial_balance), 2)
    self._transactions: list[Transaction] = []
    if self._balance > 0:
      self._record("OPENING_DEPOSIT", self._balance, "Initial deposit")

  @property
  def balance(self) -> float:
    """Expose balance safely without allowing unvalidated external mutation."""
    return self._balance

  def _record(
      self, tx_type: str, amount: float, note: str = ""
  ) -> Transaction:
    tx = Transaction(
        tx_type=tx_type,
        amount=round(float(amount), 2),
        balance_after=self._balance,
        note=note,
    )
    self._transactions.append(tx)
    return tx

  def deposit(self, amount: float, note: str = "Cash/UPI deposit") -> float:
    """Deposit a positive amount and record the transaction."""
    if amount <= 0:
      raise ValueError("Deposit amount must be greater than zero.")
    self._balance = round(self._balance + float(amount), 2)
    self._record("DEPOSIT", amount, note)
    return self._balance

  @abstractmethod
  def withdraw(self, amount: float, note: str = "Withdrawal") -> float:
    """Each account type enforces its own withdrawal rules (polymorphism)."""

  def get_statement(self) -> list[Transaction]:
    """Return a copy of the account's transaction history."""
    return list(self._transactions)


class SavingsAccount(BankAccount):
  """Savings account enforcing a minimum balance floor and interest calculation."""

  def __init__(
      self,
      account_number: str,
      owner_name: str,
      initial_balance: float = 0.0,
      min_balance: float = 1000.0,
      interest_rate: float = 0.04,
  ) -> None:
    if initial_balance < min_balance:
      raise ValueError(
          f"Savings account requires at least ₹{min_balance:.2f} initial"
          " balance."
      )
    self.min_balance = float(min_balance)
    self.interest_rate = float(interest_rate)
    super().__init__(account_number, owner_name, initial_balance)

  def withdraw(self, amount: float, note: str = "Savings withdrawal") -> float:
    if amount <= 0:
      raise ValueError("Withdrawal amount must be greater than zero.")
    projected = round(self._balance - float(amount), 2)
    if projected < self.min_balance:
      raise ValueError(
          f"Cannot withdraw ₹{amount:.2f}: minimum balance of"
          f" ₹{self.min_balance:.2f} required."
      )
    self._balance = projected
    self._record("WITHDRAWAL", amount, note)
    return self._balance

  def apply_interest(self) -> float:
    """Credit interest earned on the current balance."""
    interest = round(self._balance * self.interest_rate, 2)
    if interest > 0:
      self._balance = round(self._balance + interest, 2)
      self._record(
          "INTEREST", interest, f"{self.interest_rate * 100:.1f}% interest"
      )
    return interest


class CheckingAccount(BankAccount):
  """Checking account allowing a controlled overdraft limit."""

  def __init__(
      self,
      account_number: str,
      owner_name: str,
      initial_balance: float = 0.0,
      overdraft_limit: float = 5000.0,
  ) -> None:
    self.overdraft_limit = float(overdraft_limit)
    super().__init__(account_number, owner_name, initial_balance)

  def withdraw(self, amount: float, note: str = "Checking withdrawal") -> float:
    if amount <= 0:
      raise ValueError("Withdrawal amount must be greater than zero.")
    projected = round(self._balance - float(amount), 2)
    if projected < -self.overdraft_limit:
      raise ValueError(
          f"Withdrawal exceeds overdraft limit of ₹{self.overdraft_limit:.2f}."
      )
    self._balance = projected
    self._record("WITHDRAWAL", amount, note)
    return self._balance


class Bank:
  """Manages multiple accounts and account-level operations."""

  def __init__(self, name: str) -> None:
    self.name = name
    self._accounts: dict[str, BankAccount] = {}

  def open_account(self, account: BankAccount) -> None:
    if account.account_number in self._accounts:
      raise ValueError(f"Account '{account.account_number}' already exists.")
    self._accounts[account.account_number] = account

  def get_account(self, account_number: str) -> BankAccount:
    account = self._accounts.get(account_number)
    if not account:
      raise KeyError(f"Account '{account_number}' not found.")
    return account

  def transfer(
      self, from_acc: str, to_acc: str, amount: float
  ) -> tuple[float, float]:
    sender = self.get_account(from_acc)
    receiver = self.get_account(to_acc)
    sender.withdraw(amount, note=f"Transfer to {to_acc}")
    receiver.deposit(amount, note=f"Transfer from {from_acc}")
    return sender.balance, receiver.balance


if __name__ == "__main__":
  bank = Bank("Codomax Bank")
  acc1 = SavingsAccount("SB101", "Ritick Singh", initial_balance=5000)
  acc2 = CheckingAccount("CA201", "Aarav Sharma", initial_balance=1500)

  bank.open_account(acc1)
  bank.open_account(acc2)

  acc1.deposit(2500)
  acc1.withdraw(1200)
  acc1.apply_interest()
  bank.transfer("SB101", "CA201", 1000)

  for tx in acc1.get_statement():
    print(
        f"[{tx.timestamp}] {tx.tx_type}: ₹{tx.amount:.2f} | Balance:"
        f" ₹{tx.balance_after:.2f} ({tx.note})"
    )
