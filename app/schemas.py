from dataclasses import dataclass


@dataclass
class TimeInterval:
    hours: int
    minutes: int
    seconds: int

    @property
    def total_seconds(self) -> int:
        return (self.hours * 3600) + (self.minutes * 60) + self.seconds

    @classmethod
    def from_seconds(cls, seconds: int) -> 'TimeInterval':
        return cls(
            hours=seconds // 3600,
            minutes=(seconds % 3600) // 60,
            seconds=(seconds % 3600) % 60
        )

    @property
    def string(self) -> str:
        return f'{self.hours:0>2}:{self.minutes:0>2}:{self.seconds:0>2}'
