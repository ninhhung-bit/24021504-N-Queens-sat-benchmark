
import csv
from pathlib import Path
from statistics import mean
from time import perf_counter

from pysat.solvers import Solver

from nqueens_sat import build_cnf, var, validate_board


SIZES = [4, 8, 16, 32, 64]
ENCODINGS = ["pairwise", "seqcounter"]
REPEATS = 5


def run_once(n, encoding):
    clauses, build_time = build_cnf(n, encoding)

    solve_start = perf_counter()

    with Solver(name="g4", bootstrap_with=clauses) as solver:
        is_sat = solver.solve()
        solve_time = perf_counter() - solve_start

        if is_sat:
            model = {lit for lit in solver.get_model() if lit > 0}
            board = [
                [int(var(i, j, n) in model) for j in range(n)]
                for i in range(n)
            ]
        else:
            board = None

        valid = validate_board(board)

        # Include auxiliary variables in the SAT variable count.
        num_variables = solver.nof_vars()
        num_clauses = solver.nof_clauses()

    return {
        "n": n,
        "encoding": encoding,
        "status": "SAT" if is_sat else "UNSAT",
        "valid": valid,
        "variables": num_variables,
        "clauses": num_clauses,
        "build_time": build_time,
        "solve_time": solve_time,
        "total_time": build_time + solve_time,
    }


def main():
    results = []

    for encoding in ENCODINGS:
        for n in SIZES:
            runs = [run_once(n, encoding) for _ in range(REPEATS)]

            row = {
                "n": n,
                "encoding": encoding,
                "status": runs[0]["status"],
                "valid": all(r["valid"] for r in runs),
                "variables": runs[0]["variables"],
                "clauses": runs[0]["clauses"],
                "build_time_mean": mean(r["build_time"] for r in runs),
                "solve_time_mean": mean(r["solve_time"] for r in runs),
                "total_time_mean": mean(r["total_time"] for r in runs),
                "repeats": REPEATS,
            }

            results.append(row)

            print(
                f"N={n:2} | {encoding:10} | "
                f"{row['status']:5} | valid={row['valid']} | "
                f"vars={row['variables']:7} | "
                f"clauses={row['clauses']:8} | "
                f"build={row['build_time_mean']:.6f}s | "
                f"solve={row['solve_time_mean']:.6f}s"
            )

    output = Path(__file__).resolve().parent.parent / "results"
    output.mkdir(parents=True, exist_ok=True)
    csv_path = output / "sat_encoding_comparison.csv"

    with csv_path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=results[0].keys())
        writer.writeheader()
        writer.writerows(results)

    print(f"\nSaved results to {csv_path}")


if __name__ == "__main__":
    main()
