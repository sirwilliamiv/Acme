"""python -m shunt.report -- print the savings table."""
from . import ledger

if __name__ == "__main__":
    print(ledger.report())
