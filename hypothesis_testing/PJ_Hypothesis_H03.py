import os
import pandas as pd
from scipy import stats

def one_sided_test():
    # Find mappen hvor denne fil ligger
    base_dir = os.path.dirname(os.path.abspath(__file__))

    # Byg sti til CSV-fil
    file_path = os.path.normpath(
        os.path.join(
            base_dir,
            "..",
            "data_simulation",
            "SIR_results_network_0_T13370.txt.csv"
        )
    )

    #file_path = os.path.join(base_dir, "..", "SIR_results_network_0_T13370.txt.csv")

    print(file_path)
    print(os.path.exists(file_path))

    print("Bruger fil:", file_path)

    # Læs data
    df = pd.read_csv(file_path)

    x = df["PageRankTargeted"]
    y = df["BetweennessTargeted"]

    res = stats.ttest_ind(x, y, alternative="two-sided")

    print("\nH0: mu_PR = mu_BC")
    print("H1: mu_PR not = mu_BC")
    print(f"t = {res.statistic:.4f}")
    print(f"p = {res.pvalue:.4f}")


if __name__ == "__main__":
    one_sided_test()