from abc import ABC, abstractmethod
from typing import List, Tuple, Any, Dict


class Problem(ABC):
    @abstractmethod
    def initial_state(self) -> Any:
        pass

    @abstractmethod
    def is_goal(self, state: Any) -> bool:
        pass

    @abstractmethod
    def successors(self, state: Any) -> List[Tuple[Any, float]]:
        """Возвращает список (next_state, cost)."""
        pass


class GrammarProblem(Problem):
    def __init__(self, rules, start_symbol, target):
        self.rules = rules
        self.start_symbol = start_symbol
        self.target = target
        self.target_tokens = self._tokenize(target)
        self.max_len = len(self.target_tokens)

    def _tokenize(self, s):
        # Собираем все терминалы (символы, не являющиеся нетерминалами)
        terminals = set()
        for rhs_list in self.rules.values():
            for rhs in rhs_list:
                for sym in rhs:
                    if sym not in self.rules:
                        terminals.add(sym)
        # Сортируем по убыванию длины: 'id' раньше 'i'
        terminals_sorted = sorted(terminals, key=len, reverse=True)

        tokens = []
        i = 0
        while i < len(s):
            for t in terminals_sorted:
                if s.startswith(t, i):
                    tokens.append(t)
                    i += len(t)
                    break
            else:
                # символ не является терминалом — добавляем как есть
                tokens.append(s[i])
                i += 1
        return tuple(tokens)

    def initial_state(self):
        return (self.start_symbol,)

    def is_goal(self, state):
        return state == self.target_tokens

    def successors(self, state):
        if len(state) > self.max_len:
            return []
        for i, sym in enumerate(state):
            if sym in self.rules:
                result = []
                for rhs in self.rules[sym]:
                    new_state = state[:i] + rhs + state[i + 1 :]
                    if len(new_state) <= self.max_len:
                        result.append((new_state, 1.0))
                return result
        return []
