import csv
import os
from statistics import mean

from nqueens_cplex_mip import solve_nqueens


SIZES = [4, 8]
REPEATS = 5

OUTPUT_FILE = "results/cplex_mip_baseline.csv"


def main():
    results = []

    for n in SIZES:
        runs = []

        for repeat in range(REPEATS):
            result = solve_nqueens(n)
            runs.append(result)

            print(
                f"N={n:2} | run={repeat + 1}/{REPEATS} | "
                f"status={result['status']} | "
                f"valid={result['valid']} | "
                f"time={result['solve_time']:.6f}s"
            )

        results.append({
            "solver": "CPLEX MIP",
            "n": n,
            "repeats": REPEATS,
            "status": runs[-1]["status"],
            "valid": all(run["valid"] for run in runs),
            "solve_time_mean": mean(
                run["solve_time"] for run in runs
            ),
        })

    os.makedirs(os.path.dirname(OUTPUT_FILE), exist_ok=True)

    with open(OUTPUT_FILE, "w", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(
            file,
            fieldnames=[
                "solver",
                "n",
                "repeats",
                "status",
                "valid",
                "solve_time_mean",
            ],
        )
        writer.writeheader()
        writer.writerows(results)

    print(f"\nĐã lưu kết quả vào: {OUTPUT_FILE}")


if __name__ == "__main__":
    main()