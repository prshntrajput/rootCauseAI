"""
Demo: Smart Patcher in Action
Shows safe code patching with rootCauseAI
"""

from backend.patcher import SmartPatcher
from backend.graph.state import FixSuggestion
from pathlib import Path

print("🔧 rootCauseAI Smart Patcher Demo")
print("="*60)

# Create demo file
demo_file = Path("demo_buggy_code.py")
demo_file.write_text("""def calculate_total(prices):
    total = 0
    for price in prices:
        total = total + price  # Bug: price might be string
    return total

def main():
    items = ["10", "20", "30"]  # Strings instead of numbers
    result = calculate_total(items)
    print(f"Total: {result}")

if __name__ == "__main__":
    main()
""")

print(f"Created demo file: {demo_file}")
print("\nOriginal code:")
print(demo_file.read_text())

# Create fix
fix = FixSuggestion(
    file_path=str(demo_file),
    original_snippet='        total = total + price  # Bug: price might be string',
    new_snippet='        total = total + int(price)  # Fixed: convert to int',
    explanation="Convert price to integer before addition to avoid TypeError",
    confidence=0.95,
    line_number=4
)

# Apply fix
patcher = SmartPatcher()

print("\n" + "="*60)
print("Applying fix...")
print("="*60)

results = patcher.apply_fixes(
    fixes=[fix],
    language="python",
    dry_run=False,
    interactive=False
)

print("\nFixed code:")
print(demo_file.read_text())

# Show history
print("\n" + "="*60)
patcher.show_history(count=5)
patcher.show_stats()

# Cleanup
demo_file.unlink()
print(f"\n✅ Demo complete! (cleaned up {demo_file})")
