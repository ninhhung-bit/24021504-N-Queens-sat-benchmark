N-Queens: SAT, Constraint Programming, and MIP Benchmark

Project: Comparison of SAT solving with other exact methods for the N-Queens problem
Student ID: 24021504

1. Overview

This project studies the N-Queens problem using different exact solving approaches. It compares a SAT solver with Constraint Programming (CP), Mixed-Integer Programming (MIP), and CP-SAT implementations.

The project also evaluates four SAT encodings to investigate how formula size and encoding structure affect solving performance.

2. Solvers and SAT Encodings

Solver comparison

SAT: PySAT with Glucose 4

Constraint Programming: CPLEX CP

Mixed-Integer Programming: CPLEX MIP

Mixed-Integer Programming: Gurobi

Constraint Programming / SAT-based optimization: OR-Tools CP-SAT

SAT encoding comparison

Pairwise

Sequential counter

Commander

Product

3. Repository Structure

.
├── src/
│   ├── nqueens_sat.py
│   ├── benchmark_sat.py
│   ├── benchmark_encodings.py
│   ├── nqueens_cp_sat.py
│   ├── benchmark_cp_sat.py
│   ├── nqueens_cplex_cp.py
│   ├── benchmark_cplex_cp.py
│   ├── nqueens_cplex_mip.py
│   ├── benchmark_cplex_mip.py
│   ├── nqueens_gurobi.py
│   ├── benchmark_gurobi.py
│   └── analyze_results.py
├── results/
│   ├── sat_baseline.csv
│   ├── sat_encoding_comparison.csv
│   ├── cp_sat_baseline.csv
│   ├── cplex_cp_baseline.csv
│   ├── cplex_mip_baseline.csv
│   ├── gurobi_baseline.csv
│   ├── common_solver_comparison.csv
│   ├── solver_scalability_summary.csv
│   └── plots/
├── test_encodings.py
├── test_seqcounter.py
├── baseline_notes.md
└── README.md

4. Experimental Setup

The experiments use Python implementations of the solvers and benchmark scripts in src/. Each benchmark configuration is repeated five times, and the results are saved as CSV files.

The SAT encoding experiments evaluate board sizes (N = 4, 8, 16, 32, 64). The solver comparison uses the available results for each solver and focuses on common instance sizes when direct comparisons are needed.

Reported metrics include solving time, formula size (number of variables and clauses for SAT), solver status, and solution validity where applicable.

5. Main Experimental Observations

SAT encodings

For (N = 64), the pairwise encoding generated 4,096 variables and 428,864 clauses. The sequential-counter, commander, and product encodings generated substantially fewer clauses.

In this experiment, pairwise had the lowest mean solving time at (N = 64), approximately 0.102 seconds. Commander took approximately 0.153 seconds, while sequential counter and product took approximately 0.859 and 0.994 seconds, respectively.

These results indicate that a smaller SAT formula does not necessarily result in faster solving.

Solver scalability

Glucose4, OR-Tools CP-SAT, and CPLEX CP successfully solved all tested sizes from (N = 4) to (N = 64). CPLEX MIP successfully completed the tested instances up to (N = 8). Gurobi successfully completed the tested instances up to (N = 14).

The larger tested CPLEX MIP and Gurobi instances encountered licensing limits. These cases are not evidence of infeasibility or intrinsic algorithmic failure.

All observations are specific to the tested environment and configurations; they should not be interpreted as universal rankings of the solvers.

6. Generated Results

The results/ directory contains raw benchmark outputs and aggregated CSV files.

The results/plots/ directory contains:

solver_comparison_n4.png

solver_comparison_n8.png

solver_scalability.png

To regenerate the aggregated tables and plots, run:

python src/analyze_results.py

7. Running the Experiments

Activate the Python virtual environment and install the required Python packages before running the scripts.

Examples:

python src/benchmark_sat.py
python src/benchmark_encodings.py
python src/benchmark_cp_sat.py
python src/benchmark_cplex_cp.py
python src/benchmark_cplex_mip.py
python src/benchmark_gurobi.py
python src/analyze_results.py

CPLEX and Gurobi require their respective software installations and valid licenses. Supported package versions and installation details depend on the local environment.

Benchmark scripts may overwrite their corresponding CSV outputs.

8. Limitations

Results depend on hardware, software versions, solver settings, and the experimental environment.

Licensing restrictions limited some CPLEX MIP and Gurobi experiments.

Timing measurements should be interpreted according to each benchmark script's measurement boundaries. In particular, model-building time and solving time are not recorded identically by every implementation.

The experiments cover a finite set of board sizes and do not establish universal performance rankings.

9. Data Availability

Source code, benchmark scripts, CSV results, and generated plots are maintained in this repository:

https://github.com/ninhhung-bit/24021504-N-Queens-sat-benchmark