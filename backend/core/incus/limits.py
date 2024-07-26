from dataclasses import dataclass

@dataclass
class IncusLimits:
    """
    This class is used to represent the limits of an instance.

    Args:
        cpu (int): The CPU limit.
        memory (int): The memory limit.
        disk (int): The disk limit.
        swap (int): The swap limit.
        io (int): The IO limit
    """
    cpu: int
    memory: int
    disk: int
    swap: int
    io: int

    def to_dict(self):
        return {
            'cpu': self.cpu,
            'memory': self.memory,
            'disk': self.disk,
            'swap': self.swap,
            'io': self.io
        }