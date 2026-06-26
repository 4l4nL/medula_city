# ai/run.py
from orchestrator import orchestrate

result = orchestrate("review player.py and tell me if there are any bugs")
print(result)