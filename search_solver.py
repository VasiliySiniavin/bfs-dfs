from abc import ABC, abstractmethod
import time
import tracemalloc
from typing import List, Optional


class Node:
    __slots__ = ("state", "parent", "action", "cost", "depth")

    def __init__(self, state, parent=None, action=None, cost=0, depth=0):
        self.state = state
        self.parent = parent
        self.action = action
        self.cost = cost
        self.depth = depth

    def __repr__(self):
        return f"Node({self.state}, depth={self.depth})"


class SearchSolver(ABC):
    def __init__(self, problem, verbose: bool = False):
        self.problem = problem
        self.verbose = verbose
        self.statistics = {}
        self.solution_node: Optional[Node] = None
        self.expanded_nodes: List[Node] = []  # все раскрытые узлы (для дерева)
        self.search_log: List[str] = []  # пошаговый лог

    @abstractmethod
    def solve(self):
        pass

    def get_statistics(self):
        return self.statistics

    def reconstruct_path(self):
        if self.solution_node is None:
            return None
        path = []
        node = self.solution_node
        while node:
            path.append((node.state, node.action, node.cost))
            node = node.parent
        path.reverse()
        return path

    def _reset_stats(self):
        self.statistics = {
            "expanded": 0,
            "generated": 0,
            "max_frontier": 0,
            "max_depth": 0,
            "time_ms": 0.0,
            "memory_mb": 0.0,
            "solution_found": False,
            "path_length": 0,
            "path_cost": 0.0,
        }
        self.solution_node = None
        self.expanded_nodes = []
        self.search_log = []

    # ---------- ВИЗУАЛИЗАЦИЯ ----------

    def print_step_log(self):
        """Печатает пошаговый лог раскрытия узлов."""
        if not self.search_log:
            print("    (лог пуст: поиск не выполнялся)")
            return
        print("\n    Пошаговый лог раскрытия узлов:")
        for line in self.search_log:
            print(f"      {line}")

    def print_search_tree(self):
        """
        Печатает дерево поиска в ASCII, построенное по раскрытым узлам.
        Корень — начальное состояние; дети — потомки, порождённые при раскрытии.
        Помечает найденный путь символами '*', если решение найдено.
        """
        if not self.expanded_nodes:
            print("    (дерево пусто: поиск не выполнялся)")
            return

        # множество состояний, входящих в найденный путь
        solution_states = set()
        if self.solution_node is not None:
            n = self.solution_node
            while n is not None:
                solution_states.add(id(n))
                n = n.parent

        # узел -> его дети (порождённые при раскрытии, хранятся в expanded_nodes)
        children_map = {}
        for node in self.expanded_nodes:
            # дети = узлы из expanded_nodes, у которых parent — этот node
            children_map[id(node)] = []
        for node in self.expanded_nodes:
            if node.parent is not None and id(node.parent) in children_map:
                children_map[id(node.parent)].append(node)

        root = self.expanded_nodes[0]
        # восстановим корень, если порядок раскрытия был не от корня (DFS: pop сначала)
        # фактически корень — это узел без parent, встречающийся первым
        for node in self.expanded_nodes:
            if node.parent is None:
                root = node
                break

        print("\n    Дерево поиска (раскрытые узлы; * — на найденном пути):")
        lines: List[str] = []
        self._build_tree_lines(
            root,
            children_map,
            lines,
            prefix="",
            is_last=True,
            solution_states=solution_states,
            is_root=True,
        )
        for line in lines:
            print(f"      {line}")

    def _build_tree_lines(
        self, node, children_map, lines, prefix, is_last, solution_states, is_root=False
    ):
        marker = "*" if id(node) in solution_states else " "
        label = f"{marker} {''.join(node.state)} (d={node.depth})"
        if is_root:
            lines.append(label)
            new_prefix = ""
        else:
            connector = "└── " if is_last else "├── "
            lines.append(prefix + connector + label)
            new_prefix = prefix + ("    " if is_last else "│   ")

        children = children_map.get(id(node), [])
        for i, child in enumerate(children):
            self._build_tree_lines(
                child,
                children_map,
                lines,
                new_prefix,
                is_last=(i == len(children) - 1),
                solution_states=solution_states,
            )