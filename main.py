from problem import GrammarProblem
from bfs import BFS
from dfs import DFS


def _print_table(rows):
    if not rows:
        return
    headers = list(rows[0].keys())
    str_rows = [[str(row[h]) for h in headers] for row in rows]
    widths = [
        max(len(h), *(len(r[i]) for r in str_rows)) for i, h in enumerate(headers)
    ]
    sep = "+" + "+".join("-" * (w + 2) for w in widths) + "+"

    def fmt_row(cells):
        return "| " + " | ".join(c.ljust(w) for c, w in zip(cells, widths)) + " |"

    print(sep)
    print(fmt_row(headers))
    print(sep)
    for r in str_rows:
        print(fmt_row(r))
    print(sep)


def _format_path(path):
    if not path:
        return "—"
    return " -> ".join("".join(state) for state, _, _ in path)


def run_test(name, rules, start, target, dfs_max_depth=None, visualize=False):
    problem = GrammarProblem(rules, start, target)
    print(f"\n=== Тест № {name} ===")
    print(f"Грамматика: {rules}")
    print(f"Старт: {start}, Цель: '{target}'")
    if dfs_max_depth is not None:
        print(f"DFS max_depth = {dfs_max_depth}")

    results = []
    for algo_name, solver_cls in [("BFS", BFS), ("DFS", DFS)]:
        if algo_name == "DFS":
            solver = solver_cls(problem, max_depth=dfs_max_depth, verbose=visualize)
        else:
            solver = solver_cls(problem, verbose=visualize)

        solver.solve()
        stats = solver.get_statistics()
        path = solver.reconstruct_path()

        if visualize:
            print(f"\n  ---------- Визуализация {algo_name} ----------")
            solver.print_step_log()
            solver.print_search_tree()
            print(f"  ------------------------------------------------\n")

        solution_found = bool(stats.get("solution_found", False))
        found_str = "да" if solution_found else "нет"

        if solution_found:
            reason = "—"
        elif stats.get("depth_limit_reached", False):
            reason = f"достигнут лимит глубины ({dfs_max_depth})"
        elif (
            algo_name == "DFS"
            and dfs_max_depth is not None
            and stats["max_depth"] >= dfs_max_depth
        ):
            reason = f"достигнут лимит глубины ({dfs_max_depth})"
        else:
            reason = "фронт исчерпан (решения нет в пространстве поиска)"

        print(f"\n  [{algo_name}]")
        print(f"    Решение найдено:        {found_str}")
        if not solution_found:
            print(f"    Причина:                {reason}")
        print(f"    Раскрыто узлов:         {stats['expanded']}")
        print(f"    Порождено узлов:        {stats['generated']}")
        print(f"    Макс. размер фронта:    {stats['max_frontier']}")
        print(f"    Макс. глубина:          {stats['max_depth']}")
        print(f"    Время (мс):             {stats['time_ms']:.2f}")
        print(f"    Память (МБ):            {stats['memory_mb']:.2f}")
        print(f"    Длина пути:             {stats['path_length']}")
        print(f"    Стоимость пути:         {stats['path_cost']}")
        print(f"    Путь:                   {_format_path(path)}")

        results.append(
            {
                "Алгоритм": algo_name,
                "Найдено": found_str,
                "Причина": reason,
                "Раскрыто": stats["expanded"],
                "Порождено": stats["generated"],
                "Макс. фронт": stats["max_frontier"],
                "Макс. глубина": stats["max_depth"],
                "Время (мс)": round(stats["time_ms"], 2),
                "Память (МБ)": round(stats["memory_mb"], 2),
                "Длина пути": stats["path_length"],
                "Стоимость": round(stats["path_cost"], 2),
            }
        )

    _print_table(results)


if __name__ == "__main__":
    # Тест 1 — с визуализацией
    run_test(
        "1: Тривиальная S -> aS | b, цель 'aaab'",
        {"S": [("a", "S"), ("b",)]},
        "S",
        "aaab",
        visualize=True,
    )

    # Тест 2
    run_test(
        "2: Праворекурсивная арифметика, цель 'id+id'",
        {
            "E": [("T", "+", "E"), ("T",)],
            "T": [("id",)],
        },
        "E",
        "id+id",
    )

    # Тест 3
    run_test(
        "3: S -> aS | b, цель 'a'*10 + 'b'",
        {"S": [("a", "S"), ("b",)]},
        "S",
        "a" * 10 + "b",
    )

    # Тест 4
    run_test(
        "4: S -> A | B, A -> C, C -> a, B -> a, цель 'a'",
        {
            "S": [("A",), ("B",)],
            "A": [("C",)],
            "C": [("a",)],
            "B": [("a",)],
        },
        "S",
        "a",
    )

    # Тест 5 — порядок правил [("b",), ("S","a")]: b кладётся в стек
    # ПЕРВЫМ, Sa — ВТОРЫМ, pop() берёт Sa -> уход в бесконечную ветвь.
    # max_depth=5 останавливает поиск: решение b не найдено.
    run_test(
        "S -> S a | b, цель 'ba' (DFS с max_depth=1)",
        {"S": [("b",), ("S", "a")]},
        "S",
        "ba",
        dfs_max_depth=1,
        visualize=True,
    )
