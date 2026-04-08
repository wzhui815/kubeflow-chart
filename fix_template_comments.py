#!/usr/bin/env python3
"""
Fix Helm template comments that contain {{ }} syntax
which causes Helm to try to parse them as variables.

Solution: Replace {{ with {{`{{`}} in comments
"""

import re
from pathlib import Path

def fix_template_file(filepath):
    """Fix template syntax in comments."""
    content = filepath.read_text()
    original = content

    # Pattern 1: Fix {{revision-name}} -> {{`{{`revision-name`}}`}}
    # These are in comments showing label selectors
    content = re.sub(
        r'{{([a-zA-Z0-9_]+-[a-zA-Z0-9_]+)}}',
        r'{{`{{`\1`}}`}}',
        content
    )

    # Pattern 2: Fix {{gateway_name}}, {{namespace}} etc in comments
    # Match {{variable_name}} pattern that appears in comments
    # But avoid real Helm variables like {{ .Values.xxx }}
    content = re.sub(
        r'#.*{{([a-zA-Z0-9_]+)}}',
        lambda m: m.group(0).replace('{{', '{{`{{`').replace('}}', '`}}`}}'),
        content
    )

    if content != original:
        filepath.write_text(content)
        print(f"Fixed: {filepath}")
        return True
    return False

def main():
    templates_dir = Path("/root/manifests/helm/charts/kubeflow/templates")

    fixed_count = 0
    for yaml_file in templates_dir.rglob("*.yaml"):
        if fix_template_file(yaml_file):
            fixed_count += 1

    print(f"\nTotal files fixed: {fixed_count}")

if __name__ == "__main__":
    main()
