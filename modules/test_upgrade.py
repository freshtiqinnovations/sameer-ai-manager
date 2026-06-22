from upgrade_manager import create_patch

patch = """
ADD NEW FEATURE:
Create safe compile validation system
"""

result = create_patch("compile_validator", patch)

print("Patch created:")
print(result)
