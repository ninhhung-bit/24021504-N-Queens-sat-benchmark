from time import perf_counter

from ortools.sat.python import cp_model


def validate_board(board):
    if board is None:
        return False

    n = len(board)

    if len(set(board)) != n:
        return False

    for row1 in range(n):
        for row2 in range(row1 + 1, n):
            if abs(board[row1] - board[row2]) == abs(row1 - row2):
                return False

    return True


def solve_nqueens(n):
    model = cp_model.CpModel()

    # queen[row] là cột đặt hậu ở hàng tương ứng
    queen = [
        model.NewIntVar(0, n - 1, f"queen_{row}")
        for row in range(n)
    ]

    # Mỗi cột chỉ có tối đa một quân hậu
    model.AddAllDifferent(queen)

    # Không có hai quân hậu nằm trên cùng đường chéo
    for row1 in range(n):
        for row2 in range(row1 + 1, n):
            model.Add(
                queen[row1] - queen[row2] != row1 - row2
            )
            model.Add(
                queen[row1] - queen[row2] != row2 - row1
            )

    solver = cp_model.CpSolver()

    start = perf_counter()
    status = solver.Solve(model)
    total_time = perf_counter() - start

    if status in (cp_model.OPTIMAL, cp_model.FEASIBLE):
        board = [solver.Value(queen[row]) for row in range(n)]
        valid = validate_board(board)
    else:
        board = None
        valid = False

    return {
        "n": n,
        "status": solver.StatusName(status),
        "valid": valid,
        "solve_time": total_time,
        "board": board,
    }


if __name__ == "__main__":
    for n in [1, 2, 3, 4, 8, 16, 32, 64]:
        result = solve_nqueens(n)

        print(
            f"N={result['n']:2} | "
            f"status={result['status']:9} | "
            f"valid={result['valid']} | "
            f"solve_time={result['solve_time']:.6f}s"
        )