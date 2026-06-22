from upgrade_manager import apply_patch

filename = "20260511_013232_compile_validator.txt"

result = apply_patch(filename)

print("Applied:", result)
