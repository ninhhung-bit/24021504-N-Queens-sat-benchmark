# N-Queens SAT Baseline

## Environment
- OS: Windows 11
- Python: 3.12.10
- SAT library: PySAT
- SAT solver: Glucose 4 (`g4`)

## SAT encoding
- One Boolean variable per board cell: `x(i, j)`
- Exactly one queen per row
- Exactly one queen per column
- At most one queen per diagonal
- At-least-one (ALO): one clause containing all variables in the constraint
- At-most-one (AMO): pairwise encoding

## Initial correctness tests

| N | Expected result | Observed result | Valid solution |
| 1 | SAT             | SAT             | True           |
| 2 | UNSAT           | UNSAT           | N/A            |
| 3 | UNSAT           | UNSAT           | N/A            |
| 4 | SAT             | SAT             | True           |
| 8 | SAT             | SAT             | True           |
| 16| SAT            | SAT             | True           |

## Initial observation
The baseline implementation passes all initial correctness tests. The reported runtime currently includes both CNF construction and SAT solving, so these times should not yet be treated as solver-only runtimes.
