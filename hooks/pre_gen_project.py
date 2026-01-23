import keyword
import re
import sys

project_slug = "{{ cookiecutter.project_slug }}"
package_name = "{{ cookiecutter.package_name }}"

# Enforce kebab-case slug: lowercase alnum separated by hyphens only
if not re.fullmatch(r"[a-z0-9]+(-[a-z0-9]+)*", project_slug):
    sys.exit(
        "ERROR: project_slug must be lowercase letters/numbers separated by hyphens only "
        "(example: my-tool). Underscores are not allowed."
    )

# Enforce snake_case package: valid Python identifier, no hyphens
if "-" in package_name:
    sys.exit("ERROR: package_name may not contain hyphens. Use underscores (example: my_tool).")

if not re.fullmatch(r"[A-Za-z_][A-Za-z0-9_]*", package_name):
    sys.exit(
        "ERROR: package_name must be a valid Python identifier "
        "(example: my_tool)."
    )

if keyword.iskeyword(package_name):
    sys.exit(f"ERROR: package_name '{package_name}' is a Python keyword.")

expected_package = project_slug.replace("-", "_")
if package_name != expected_package:
    sys.exit(
        f"ERROR: package_name should equal project_slug with '-' replaced by '_'. "
        f"Expected '{expected_package}', got '{package_name}'."
    )
