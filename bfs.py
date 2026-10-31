from collections import deque
import time
import tracemalloc
from search_solver import SearchSolver, Node


class BFS(SearchSolver):
    def solve(self):
        self._reset_stats()
        tracemalloc.start()
        start_time = time.perf_counter()

        start_node = Node(self.problem.initial_state(), depth=0)
        if self.problem.is_goal(start_node.state):
            self.solution_node = start_node
            self.statistics["solution_found"] = True
            self.statistics["path_length"] = 0
            self.statistics["path_cost"] = 0.0
            self._finish(start_time)
            return start_node

        frontier = deque([start_node])
        visited = {start_node.state}
        self.statistics["max_frontier"] = 1

        step = 0
        while frontier:
            node = frontier.popleft()
            self.statistics["expanded"] += 1
            self.statistics["max_depth"] = max(self.statistics["max_depth"], node.depth)
            self.expanded_nodes.append(node)

            children_states = []
            for next_state, cost in self.problem.successors(node.state):
                self.statistics["generated"] += 1
                if next_state in visited:
                    continue
                visited.add(next_state)
                child = Node(
                    next_state, parent=node, cost=node.cost + cost, depth=node.depth + 1
                )
                children_states.append(next_state)

                if self.verbose:
                    self.search_log.append(
                        f"step {step:3d} | expand {''.join(node.state)} (d={node.depth}) "
                        f"-> child {''.join(child.state)} (d={child.depth})"
                    )
                step += 1

                if self.problem.is_goal(child.state):
                    self.solution_node = child
                    self.statistics["solution_found"] = True
                    self.statistics["path_length"] = child.depth
                    self.statistics["path_cost"] = child.cost
                    if self.verbose:
                        self.search_log.append(
                            f"step {step:3d} | GOAL: {''.join(child.state)} "
                            f"(depth={child.depth}, cost={child.cost})"
                        )
                    self._finish(start_time)
                    return child
                frontier.append(child)
                self.statistics["max_frontier"] = max(
                    self.statistics["max_frontier"], len(frontier)
                )

            if self.verbose and not children_states:
                self.search_log.append(
                    f"step {step:3d} | expand {''.join(node.state)} (d={node.depth}) "
                    f"-> no new children (all visited/dead end)"
                )

        self._finish(start_time)
        return None

    def _finish(self, start_time):
        end_time = time.perf_counter()
        current, peak = tracemalloc.get_traced_memory()
        tracemalloc.stop()
        self.statistics["time_ms"] = (end_time - start_time) * 1000
        self.statistics["memory_mb"] = peak / 1024 / 1024