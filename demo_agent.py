"""
Demo: AI Error Fixing Agent
Shows the agent in action with a sample error
"""

from backend.graph import AgentRunner

# Sample Python error
error_log = """
Traceback (most recent call last):
  File "backend/api/views.py", line 42, in get_user_data
    age = user_data["age"] + 1
TypeError: can only concatenate str (not "int") to str
"""

print("🤖 AI Error Fixing Agent Demo")
print("="*60)

# Create and run agent
runner = AgentRunner(max_retries=3)
result = runner.run_and_display(error_log)

print("\n✅ Demo complete!")
