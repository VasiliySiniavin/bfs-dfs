import time
import tracemalloc
from search_solver import SearchSolver, Node


class DFS(SearchSolver):

    def __init__(self, problem, max_depth=None, verbose: bool = False):
        super().__init__(problem, verbose=verbose)
        self.max_depth = max_depth

    def solve(self):
        self._reset_stats()
        tracemalloc.start()
        start_time = time.perf_counter()

        start_node = Node(self.problem.initial_state(), depth=0)
        frontier = [start_node]
        visited = {start_node.state}
        self.statistics["max_frontier"] = 1

        step = 0
        while frontier:
            node = frontier.pop()
            self.statistics["expanded"] += 1
            self.statistics["max_depth"] = max(self.statistics["max_depth"], node.depth)
            self.expanded_nodes.append(node)

            # --- ПРОВЕРКА ЦЕЛИ ПРИ ИЗВЛЕЧЕНИИ ИЗ СТЕКА ---
            if self.problem.is_goal(node.state):
                self.solution_node = node
                self.statistics["solution_found"] = True
                self.statistics["path_length"] = node.depth
                self.statistics["path_cost"] = node.cost
                if self.verbose:
                    self.search_log.append(
                        f"step {step:3d} | POP GOAL: {''.join(node.state)} "
                        f"(d={node.depth}, cost={node.cost})"
                    )
                self._finish(start_time)
                return node

            # --- ОГРАНИЧЕНИЕ ГЛУБИНЫ ---
            if self.max_depth is not None and node.depth >= self.max_depth:
                if self.verbose:
                    self.search_log.append(
                        f"step {step:3d} | pop {''.join(node.state)} (d={node.depth}) "
                        f"-> PRUNED (max_depth={self.max_depth})"
                    )
                continue

            # --- РАСКРЫТИЕ ---
            children = []
            for next_state, cost in self.problem.successors(node.state):
                self.statistics["generated"] += 1
                if next_state in visited:
                    continue
                visited.add(next_state)
                child = Node(
                    next_state, parent=node, cost=node.cost + cost, depth=node.depth + 1
                )
                children.append(child)

            # Кладём в стек в порядке правил; последний ребёнок окажется на вершине
            for child in children:
                frontier.append(child)

            if self.verbose:
                if children:
                    labels = ", ".join(
                        f"{''.join(c.state)} (d={c.depth})" for c in children
                    )
                    self.search_log.append(
                        f"step {step:3d} | pop {''.join(node.state)} (d={node.depth}) "
                        f"-> push [{labels}]"
                    )
                else:
                    self.search_log.append(
                        f"step {step:3d} | pop {''.join(node.state)} (d={node.depth}) "
                        f"-> no new children (all visited/dead end)"
                    )
            step += 1

            self.statistics["max_frontier"] = max(
                self.statistics["max_frontier"], len(frontier)
            )

        self._finish(start_time)
        return None

    def _finish(self, start_time):
        end_time = time.perf_counter()
        current, peak = tracemalloc.get_traced_memory()
        tracemalloc.stop()
        self.statistics["time_ms"] = (end_time - start_time) * 1000
        self.statistics["memory_mb"] = peak / 1024 / 1024