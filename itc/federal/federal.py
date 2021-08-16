#! /usr/bin/env python3

import json
import os

from ..taxes import FileType, Taxes


class FederalTaxes(Taxes):

    branch = "Federal"

    def __init__(self, tax_year: int, filing_status: FileType):
        """Create a Federal Tax object."""
        super().__init__(tax_year, filing_status)

        wrkdir = os.path.dirname(os.path.abspath(__file__))
        path = os.path.join(wrkdir, f"{tax_year}.json")
        with open(path, "r") as file_:
            data = json.load(file_)

        self.income_tax_rates = {
            FileType.__members__[status]: {
                int(key): float(value) for key, value in brackets.items()
            }
            for status, brackets in data.items()
        }
