import csv
import os
import statistics

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt


RESULTS_DIR = "results"
PLOTS_DIR = os.path.join(RESULTS_DIR, "plots")

INPUT_FILES = {
    "Glucose4": "sat_baseline.csv",
    "OR-Tools CP-SAT": "cp_sat_baseline.csv",
    "CPLEX CP": "cplex_cp_baseline.csv",
    "CPLEX MIP": "cplex_mip_baseline.csv",
    "Gurobi": "gurobi_baseline.csv",
}

COMMON_SIZES = [4, 8]


def read_csv(filename):
    path = os.path.join(RESULTS_DIR, filename)
    with open(path, "r", newline="", encoding="utf-8-sig") as file:
        return list(csv.DictReader(file))


def get_solve_time(row):
    for key in ("solve_time_mean_s", "solve_time_mean",
                "solve_time_mean_seconds", "mean_time_seconds"):
        if row.get(key) not in (None, ""):
            return float(row[key])
    return None


def is_valid(row):
    return row.get("valid", "").strip().lower() == "true"


def collect_data():
    records = []

    for solver, filename in INPUT_FILES.items():
        for row in read_csv(filename):
            records.append({
                "solver": solver,
                "n": int(row["n"]),
                "status": row.get("status", ""),
                "valid": is_valid(row),
                "solve_time_seconds": get_solve_time(row),
                "repeats": int(row.get("repeats", 0)),
                "source_file": filename,
            })

    return records


def write_common_comparison(records):
    output_path = os.path.join(
        RESULTS_DIR, "common_solver_comparison.csv"
    )

    selected = [
        row for row in records
        if row["n"] in COMMON_SIZES
        and row["valid"]
        and row["solve_time_seconds"] is not None
    ]

    with open(output_path, "w", newline="", encoding="utf-8") as file:
        fields = [
            "solver", "n", "status", "valid", "repeats",
            "solve_time_seconds", "source_file",
        ]
        writer = csv.DictWriter(file, fieldnames=fields)
        writer.writeheader()
        writer.writerows(
            sorted(selected, key=lambda r: (r["n"], r["solver"]))
        )

    print(f"Saved: {output_path}")


def write_scalability_summary(records):
    output_path = os.path.join(
        RESULTS_DIR, "solver_scalability_summary.csv"
    )

    solvers = list(INPUT_FILES.keys())
    rows = []

    for solver in solvers:
        solver_records = [r for r in records if r["solver"] == solver]
        successful = [
            r for r in solver_records
            if r["valid"] and r["solve_time_seconds"] is not None
        ]
        failed_or_limited = [
            r for r in solver_records if not r["valid"]
        ]

        rows.append({
            "solver": solver,
            "largest_successful_n": (
                max((r["n"] for r in successful), default="")
            ),
            "successful_sizes": ";".join(
                str(r["n"]) for r in sorted(successful, key=lambda x: x["n"])
            ),
            "non_successful_sizes": ";".join(
                f'{r["n"]}:{r["status"]}'
                for r in sorted(failed_or_limited, key=lambda x: x["n"])
            ),
        })

    with open(output_path, "w", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(
            file,
            fieldnames=[
                "solver", "largest_successful_n",
                "successful_sizes", "non_successful_sizes",
            ],
        )
        writer.writeheader()
        writer.writerows(rows)

    print(f"Saved: {output_path}")


def plot_common_sizes(records):
    os.makedirs(PLOTS_DIR, exist_ok=True)

    for n in COMMON_SIZES:
        selected = [
            r for r in records
            if r["n"] == n
            and r["valid"]
            and r["solve_time_seconds"] is not None
        ]
        selected.sort(key=lambda r: r["solve_time_seconds"])

        if not selected:
            continue

        labels = [r["solver"] for r in selected]
        times = [r["solve_time_seconds"] for r in selected]

        fig, ax = plt.subplots(figsize=(9, 5))
        bars = ax.barh(labels, times)
        ax.set_xscale("log")
        ax.set_xlabel("Mean solve time (seconds, log scale)")
        ax.set_title(f"N-Queens solver comparison (N={n})")
        ax.grid(axis="x", linestyle="--", alpha=0.4)

        for bar, value in zip(bars, times):
            ax.annotate(
                f"{value:.3g}s",
                (value, bar.get_y() + bar.get_height() / 2),
                xytext=(5, 0),
                textcoords="offset points",
                va="center",
                fontsize=8,
            )

        fig.tight_layout()
        path = os.path.join(PLOTS_DIR, f"solver_comparison_n{n}.png")
        fig.savefig(path, dpi=200, bbox_inches="tight")
        plt.close(fig)
        print(f"Saved: {path}")


def plot_scalability(records):
    os.makedirs(PLOTS_DIR, exist_ok=True)

    fig, ax = plt.subplots(figsize=(9, 6))

    for solver in INPUT_FILES:
        selected = sorted(
            [
                r for r in records
                if r["solver"] == solver
                and r["valid"]
                and r["solve_time_seconds"] is not None
            ],
            key=lambda r: r["n"],
        )

        if selected:
            ax.plot(
                [r["n"] for r in selected],
                [r["solve_time_seconds"] for r in selected],
                marker="o",
                label=solver,
            )

    ax.set_yscale("log")
    ax.set_xlabel("Board size N")
    ax.set_ylabel("Mean solve time (seconds, log scale)")
    ax.set_title("N-Queens solver scalability")
    ax.grid(True, linestyle="--", alpha=0.4)
    ax.legend()
    fig.tight_layout()

    path = os.path.join(PLOTS_DIR, "solver_scalability.png")
    fig.savefig(path, dpi=200, bbox_inches="tight")
    plt.close(fig)
    print(f"Saved: {path}")


def main():
    os.makedirs(RESULTS_DIR, exist_ok=True)

    records = collect_data()
    write_common_comparison(records)
    write_scalability_summary(records)
    plot_common_sizes(records)
    plot_scalability(records)

    print("\nAnalysis outputs generated successfully.")


if __name__ == "__main__":
    main()
