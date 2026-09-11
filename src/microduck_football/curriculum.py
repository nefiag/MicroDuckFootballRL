"""按评估成功率推进课程难度。"""

from dataclasses import dataclass


@dataclass
class Curriculum:
    level: int = 1
    threshold: float = 0.8
    max_level: int = 4

    def update(self, success_rate: float) -> bool:
        if success_rate >= self.threshold and self.level < self.max_level:
            self.level += 1
            return True
        return False
