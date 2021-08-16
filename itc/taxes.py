#! /usr/bin/env python3

import enum

from .exceptions import TaxException


class FileType(enum.Enum):
    single = enum.auto()
    married_joint = enum.auto()
    married_separate = enum.auto()
    head_of_house = enum.auto()

    def __str__(self) -> str:
        return str(self.name)


class Taxes:

    branch = None
    income_tax_rates = None

    def __init__(self, tax_year: int, filing_status: FileType):
        """Create a Federal Tax object."""
        self.year = tax_year
        self.status = filing_status

    def income_tax(self, taxable_income: float) -> float:
        """Calculate taxable income"""
        brackets = self.income_tax_rates[self.status]
        pool = taxable_income
        taxes = 0.0
        last = 0.0
        num_brackets = len(brackets)
        for idx, data in enumerate(sorted(brackets.items(), key=lambda x: x[0])):
            income, rate = data
            if taxable_income > income and idx != (num_brackets - 1):
                # If your income isn't in the highest brackets yet and you
                # make more than the upper limit in this bracket you pay the
                # max in this bracket.
                brak = income - last
                last = income
                pool -= brak
                taxes += brak * rate
            else:
                taxes += pool * rate
                if last + pool != taxable_income:
                    raise TaxException(f"{self.branch} income tax calculation error.")
                break
        return taxes
