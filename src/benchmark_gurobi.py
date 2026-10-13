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
        build_times = []
        solve_times = []
        total_times = []
        final_result = None

        for repeat in range(1, REPEATS + 1):
            result = solve_nqueens(n)
            final_result = result

            build_time = result["build_time_seconds"]
            solve_time = result["solve_time_seconds"]
            total_time = result["time_seconds"]

            build_times.append(build_time)
            solve_times.append(solve_time)
            total_times.append(total_time)

            print(
                f"N={n:2d} | run={repeat}/{REPEATS} | "
                f"status={result['status']} | "
                f"build={build_time:.6f}s | "
                f"solve={solve_time:.6f}s | "
                f"total={total_time:.6f}s"
            )

        rows.append({
            "solver": "Gurobi",
            "n": n,
            "repeats": REPEATS,
            "status": final_result["status"],
            "build_time_mean_seconds": statistics.mean(build_times),
            "solve_time_mean_seconds": statistics.mean(solve_times),
            "total_time_mean_seconds": statistics.mean(total_times),
            "solve_time_stdev_seconds": (
                statistics.stdev(solve_times)
                if len(solve_times) > 1 else 0.0
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
