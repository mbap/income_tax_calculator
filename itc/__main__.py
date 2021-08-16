#! /usr/bin/env python3

import argparse
import datetime
import logging
import sys

from .federal.federal import FederalTaxes
from .taxes import FileType
from .state import california, idaho  # noqa: F401
from .state.common import StateTaxMeta

LOG = logging.getLogger(__name__)


def parse_args():
    parser = argparse.ArgumentParser(description="Income Tax Calculator")
    parser.add_argument(
        "--gross-income",
        dest="gross",
        required=True,
        type=float,
        help=("Gross income as USD figure. Also known as total compensation (TC)"),
    )
    parser.add_argument(
        "--deductable-income",
        dest="deduction",
        required=True,
        type=float,
        help=(
            "Duducable income, such as 401k contributions or other tax "
            "advantaged account contributions that lower your taxable income."
        ),
    )
    parser.add_argument(
        "--monthly-expenses",
        dest="expenses",
        required=True,
        type=float,
        help="Estimated monthly cost of living expenses not including rent.",
    )
    parser.add_argument(
        "--monthly-housing",
        dest="housing",
        required=True,
        type=float,
        help="Cost of rent or mortage per month.",
    )

    benefits = parser.add_mutually_exclusive_group()
    benefits.add_argument(
        "--monthly-benefits",
        dest="mbenefits",
        required=False,
        default=0.0,
        type=float,
        help="Cost of benefits per month.",
    )
    benefits.add_argument(
        "--yearly-benefits",
        dest="ybenefits",
        required=False,
        default=0.0,
        type=float,
        help="Cost of benefits per year.",
    )

    parser.add_argument(
        "--after-tax-savings",
        dest="ats",
        required=False,
        default=0.0,
        type=float,
        help="Percentage of take home income to be saved for investments",
    )
    parser.add_argument(
        "--tax-year",
        dest="year",
        required=False,
        default=str(datetime.date.today().year),
        type=str,
        help="Tax year for calculations.",
    )
    parser.add_argument(
        "--filing-status",
        dest="status",
        required=True,
        choices=FileType.__members__.keys(),
        help="Tax filing status",
    )
    states = StateTaxMeta.registry.keys()
    parser.add_argument(
        "--state-taxes",
        dest="state",
        required=True,
        choices=states,
        help="State taxes.",
    )
    parser.add_argument(
        "--compare-state",
        dest="cstate",
        required=False,
        default=None,
        choices=states,
        help="Compare state taxes.",
    )
    return parser.parse_args()


def main():
    args = parse_args()

    # Settings
    tax_year = args.year
    filing_status = FileType.__members__[args.status]
    gross_income = args.gross
    deductions = args.deduction
    yearly_housing = args.housing * 12
    yearly_exp = args.expenses * 12
    if args.ybenefits:
        benefits = args.ybenefits
    elif args.mbenefits:
        benefits = args.mbenefits * 12
    else:
        benefits = 0

    # Get taxable income
    taxable_income = gross_income - deductions

    # Fed taxes
    fed = FederalTaxes(tax_year, filing_status)
    fed_taxes = fed.income_tax(taxable_income)

    # State taxes
    state_cls = StateTaxMeta.registry[args.state]
    state_taxes = state_cls(tax_year, filing_status).income_tax(taxable_income)

    take_home = gross_income - deductions - fed_taxes - state_taxes - benefits

    print(f"\nIncome Tax Estimations for Tax Year {tax_year}")
    print("==============================================\n")
    print(f"Gross income: ${gross_income:.2f}")
    print(f"Income deductions: ${deductions:.2f}")
    print(f"Reported wages: ${gross_income - deductions:.2f}\n")

    print(f"Federal taxes due: ${fed_taxes:.2f}")
    print(f"{args.state} state taxes due: ${state_taxes:.2f}")
    print(f"Yearly benefits costs: ${benefits:.2f} (per month: ${benefits / 12:.2f})\n")

    print(f"Pre-expenses take home: ${take_home:.2f}\n")

    print(
        f"Yearly housing costs: ${yearly_housing:.2f} (per month: ${args.housing:.2f})"
    )
    print(
        f"Yearly living expenses: ${yearly_exp:.2f} (per month: ${args.expenses:.2f})"
    )
    print(f"Annual cost of living: {yearly_housing + yearly_exp:.2f}\n")

    if not args.ats:
        final_take = take_home - yearly_housing - yearly_exp
        print(f"Final take home: {final_take:.2f}\n")
    else:
        # Calculate saving first.
        savings = take_home * args.ats
        final_take = take_home - yearly_housing - yearly_exp - savings

        print(f"Savings before expenses at ${args.ats * 100}%: ${savings:.2f}")
        print(f"Final take home: {final_take:.2f}\n")

        # Calculate savings after expenses
        after_exp = take_home - yearly_housing - yearly_exp
        savings = after_exp * args.ats
        final_take = after_exp - savings

        print(f"Savings after expenses at ${args.ats * 100}%: ${savings:.2f}")
        print(f"Final take home: {final_take:.2f}")

    # Comparable state
    if args.cstate:
        print("Compare state not yet implemented.")

    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except Exception as err:
        LOG.exception(str(err))
        sys.exit(1)
