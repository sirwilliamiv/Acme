"""shunt - route low-reasoning I/O work away from the expensive model.

A Claude Code PreToolUse hook that intercepts large file reads, delegates them
to a cheap model, and hands the expensive model a digest instead of the raw file.
"""

__version__ = "0.1.0"
