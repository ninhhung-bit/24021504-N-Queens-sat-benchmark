import csv
import os
import statistics

from nqueens_gurobi import solve_nqueens


SIZES = [4, 8, 14, 16, 32]
REPEATS = 5
OUTPUT_PATH = "results/gurobi_baseline.csv"


def main():
    os.makedirs("results", exist_ok=True)
    rows = []

    for n in SIZES:
        times = []
        final_result = None

        for repeat in range(1, REPEATS + 1):
            result = solve_nqueens(n)
            final_result = result
            times.append(result["time_seconds"])

            print(
                f"N={n:2d} | run={repeat}/{REPEATS} | "
                f"status={result['status']} | "
                f"time={result['time_seconds']:.6f}s"
            )

        rows.append({
            "solver": "Gurobi",
            "n": n,
            "repeats": REPEATS,
            "status": final_result["status"],
            "mean_time_seconds": statistics.mean(times),
            "stdev_time_seconds": (
                statistics.stdev(times) if len(times) > 1 else 0.0
            ),
            "valid": final_result["status"] == "OPTIMAL",
        })

    with open(OUTPUT_PATH, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=rows[0].keys())
        writer.writeheader()
        writer.writerows(rows)

    print(f"\nSaved results to {OUTPUT_PATH}")


if __name__ == "__main__":
    main()
