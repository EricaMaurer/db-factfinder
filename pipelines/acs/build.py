import itertools
import os
import sys
from pathlib import Path

import pandas as pd
from dotenv import load_dotenv
from tqdm import tqdm

from multiprocessing import Pool
from factfinder.calculate import Calculate

# Load .env environmental variables for local runs
try:
    env_path = f"{Path(__file__).parent.parent.parent}/.env"
    load_dotenv(dotenv_path=env_path)
except:
    print(".env file is missing ...")

# Function wrapper calculate for multiprocessing
def calc(*args):
    (var, domain), geo = args[0]
    return pff.calculate(var, geo).assign(domain=domain)

if __name__ == "__main__":
    # Get ACS year
    year = sys.argv[1]
    geography = sys.argv[2]

    if not os.path.exists("pff_output"):
        os.makedirs("pff_output")

    # Initialize pff instance
    calculate = Calculate(api_key=os.environ["API_KEY"], year=year, source="acs", geography=geography)

    # Declare geography and variables involved in this caculation
    geogs = calculate.geo.aggregated_geography.extend("tract", "block group")
    domains = ["demographic", "economic", "housing", "social"]
    variables = [
        (i["pff_variable"], i["domain"]) for i in calculate.meta.metadata if i["domain"] in domains
    ]

    # Loop through calculations and collect dataframes in dfs
    dfs = []
    for args in tqdm(list(itertools.product(variables, geogs))):
        dfs.append(calc(args))

    # Concatenate dataframes and export to 1 large csv
    df = pd.concat(dfs)
    df.to_csv(f"pff_output/acs_{year}_{geography}_geogs.csv", index=False)
