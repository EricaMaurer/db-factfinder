import json
from functools import cached_property
from pathlib import Path


class Variable:
    def __init__(self, kwargs):
        self.pff_variable = kwargs.get("pff_variable")
        self.census_variable = kwargs.get("census_variable")
        self.domain = kwargs.get("domain")
        self.base_variable = kwargs.get("base_variable")
        self.rounding = kwargs.get("rounding")
        self.source = kwargs.get("source")
        self.meta = kwargs


class Metadata:
    def __init__(self, year=2019, source="acs"):
        self.year = year
        self.source = source
        # Contains variables where the numerator comes from a DP dataset,
        # but pff uses a different base than the census
        self.profile_only_exceptions = [
            "abroad",
            "cvlfuem2",
            "dfhsdfcnt",
            "dfhssmcnt",
            "dfhsus",
            "hh5",
            "oochu4",
            "p65plbwpv",
            "pbwpv",
            "pu18bwpv",
        ]

    @cached_property
    def metadata(self) -> list:
        with open(
            f"{Path(__file__).parent}/data/{self.source}/{self.year}/metadata.json"
        ) as f:
            return json.load(f)

    @cached_property
    def median(self) -> list:
        with open(
            f"{Path(__file__).parent}/data/{self.source}/{self.year}/median.json"
        ) as f:
            return json.load(f)

    @cached_property
    def special(self) -> list:
        with open(
            f"{Path(__file__).parent}/data/{self.source}/{self.year}/special.json"
        ) as f:
            return json.load(f)

    @cached_property
    def profile_only_variables(self) -> list:
        return [
            i["pff_variable"]
            for i in self.metadata
            if (
                i["census_variable"][0][0:2] == "DP"
                and len(i["census_variable"]) == 1
                and i["pff_variable"] not in self.profile_only_exceptions
            )
        ]

    @cached_property
    def base_variables(self) -> list:
        """
        returns a list of base variables in the format of pff_variable
        """
        return list(set([i["base_variable"] for i in self.metadata]))

    def get_special_base_variables(self, pff_variable) -> list:
        """
        returns a list of special calculation base variables in the format
        of pff_variable
        """
        special = next(
            filter(lambda x: x["pff_variable"] == pff_variable, self.special)
        )
        return special["base_variables"]

    @cached_property
    def median_variables(self) -> list:
        """
        returns a list of median variables in the format of pff_variable
        """
        return list(self.median.keys())

    @cached_property
    def special_variables(self) -> list:
        """
        returns a list of special calculation variables in the format
        of pff_variable
        """
        return [i["pff_variable"] for i in self.special]

    def create_variable(self, pff_variable: str) -> Variable:
        """
        given pff_variable name, return a Variable object
        """
        meta = next(filter(lambda x: x["pff_variable"] == pff_variable, self.metadata))
        return Variable(meta)

    def create_census_variables(self, census_variable: list):
        """
        Based on the census variables, spit out the
        M variables and E variables
        e.g. ["B01001_044"] -> ["B01001_044M"], ["B01001_044E"]
        """
        E_variables = [i + "E" for i in census_variable if i[0] != "P"]
        if len(E_variables) == 0:  # Only decennial, pass raw variable name
            E_variables = census_variable
        M_variables = [i + "M" for i in census_variable if i[0] != "P"]
        return E_variables, M_variables
