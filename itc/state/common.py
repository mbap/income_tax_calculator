#! /usr/bin/env python3

import json
import os

from ..taxes import FileType, Taxes


class StateTaxMeta(type):
    registry = {}

    def __init__(self, name, bases, namespace, **kwds):
        if self.branch:
            StateTaxMeta.registry[self.branch] = self


class StateTaxes(Taxes, metaclass=StateTaxMeta):

    branch = None

    def __init__(self, tax_year: int, filing_status: FileType):
        """Create a Federal Tax object."""
        super().__init__(tax_year, filing_status)

        wrkdir = os.path.dirname(os.path.abspath(__file__))
        path = os.path.join(
            wrkdir, f'{self.__class__.__module__.split(".")[-1]}', f"{tax_year}.json"
        )
        with open(path, "r") as file_:
            data = json.load(file_)

        self.income_tax_rates = {
            FileType.__members__[status]: {
                int(key): float(value) for key, value in brackets.items()
            }
            for status, brackets in data.items()
        }
