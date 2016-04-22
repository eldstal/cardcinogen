import sys

# Global log function.
# This object exposes a write(string) function.
log = sys.stderr

def setlog(obj):
  global log
  log = obj
