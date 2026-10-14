"""Compatibility exception for the standalone observable-machine adapter.

This adapter intentionally supplies only the WorkLimit exception used by the
unchanged upstream observable-machine module; it is not the divisor solver.
"""
class WorkLimit(RuntimeError):pass
