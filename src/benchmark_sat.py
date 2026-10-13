import csv
import statistics
from pathlib import Path

from nqueens_sat import solve_nqueens


SIZES = [4, 8, 16, 32, 64]
REPEATS = 5


def main():
    output_path = Path("results")
    output_path.mkdir(exist_ok=True)

    csv_path = output_path / "sat_baseline.csv"
    rows = []

    for n in SIZES:
        build_times = []
        solve_times = []
        total_times = []
        last_result = None

        for _ in range(REPEATS):
            result = solve_nqueens(n)
            last_result = result

            build_times.append(result["build_time"])
            solve_times.append(result["solve_time"])
            total_times.append(result["total_time"])

        rows.append({
            "solver": "Glucose4",
            "encoding": "pairwise",
            "n": n,
            "repeats": REPEATS,
            "status": last_result["status"],
            "valid": last_result["valid"],
            "variables": last_result["variables"],
            "clauses": last_result["clauses"],
            "build_time_mean_s": statistics.mean(build_times),
            "solve_time_mean_s": statistics.mean(solve_times),
            "total_time_mean_s": statistics.mean(total_times),
        })

        print(
            f"N={n:3} | {last_result['status']:5} | "
            f"valid={last_result['valid']} | "
            f"vars={last_result['variables']:6} | "
            f"clauses={last_result['clauses']:8} | "
            f"build={statistics.mean(build_times):.6f}s | "
            f"solve={statistics.mean(solve_times):.6f}s"
        )

    fieldnames = list(rows[0].keys())

    with csv_path.open("w", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(file, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)

    print(f"\nSaved benchmark results to: {csv_path.resolve()}")


if __name__ == "__main__":
    main()

