#!/usr/bin/env python3
"""
Git Version Manager for Kubeflow Helm Charts

This script manages git version information for Helm charts,
ensuring traceability between kustomize manifests and generated helm charts.
"""

import subprocess
import json
import yaml
from datetime import datetime
from pathlib import Path


class VersionManager:
    """Manages git version information for Helm charts."""

    def __init__(self, kustomize_dir: str, helm_dir: str):
        self.kustomize_dir = Path(kustomize_dir)
        self.helm_dir = Path(helm_dir)
        self.chart_yaml = self.helm_dir / "charts" / "kubeflow" / "Chart.yaml"

    def get_git_info(self) -> dict:
        """Get git information from kustomize directory."""
        try:
            # Get current commit hash
            commit = subprocess.run(
                ["git", "-C", str(self.kustomize_dir), "rev-parse", "--short", "HEAD"],
                capture_output=True, text=True, check=True
            ).stdout.strip()

            # Get commit date
            commit_date = subprocess.run(
                ["git", "-C", str(self.kustomize_dir), "log", "-1", "--format=%ci"],
                capture_output=True, text=True, check=True
            ).stdout.strip()

            # Get commit message
            commit_msg = subprocess.run(
                ["git", "-C", str(self.kustomize_dir), "log", "-1", "--format=%s"],
                capture_output=True, text=True, check=True
            ).stdout.strip()

            # Get branch name
            branch = subprocess.run(
                ["git", "-C", str(self.kustomize_dir), "rev-parse", "--abbrev-ref", "HEAD"],
                capture_output=True, text=True, check=True
            ).stdout.strip()

            # Get tag if exists
            try:
                tag = subprocess.run(
                    ["git", "-C", str(self.kustomize_dir), "describe", "--tags", "--exact-match"],
                    capture_output=True, text=True, check=True
                ).stdout.strip()
            except subprocess.CalledProcessError:
                tag = None

            return {
                "commit": commit,
                "commit_date": commit_date,
                "commit_message": commit_msg,
                "branch": branch,
                "tag": tag,
                "generated_at": datetime.now().isoformat()
            }

        except subprocess.CalledProcessError as e:
            print(f"Error getting git info: {e}")
            return {}

    def update_chart_yaml(self, git_info: dict):
        """Update Chart.yaml with git version information."""
        if not self.chart_yaml.exists():
            print(f"Chart.yaml not found at {self.chart_yaml}")
            return

        with open(self.chart_yaml, 'r') as f:
            chart = yaml.safe_load(f)

        # Add annotations with git info
        if 'annotations' not in chart:
            chart['annotations'] = {}

        chart['annotations']['kustomize.commit'] = git_info.get('commit', 'unknown')
        chart['annotations']['kustomize.branch'] = git_info.get('branch', 'unknown')
        chart['annotations']['kustomize.commitDate'] = git_info.get('commit_date', 'unknown')
        chart['annotations']['helm.generatedAt'] = git_info.get('generated_at', 'unknown')

        if git_info.get('tag'):
            chart['annotations']['kustomize.tag'] = git_info['tag']

        # Write back
        with open(self.chart_yaml, 'w') as f:
            yaml.dump(chart, f, default_flow_style=False, sort_keys=False)

        print(f"Updated {self.chart_yaml} with git version info")

    def generate_version_file(self, git_info: dict):
        """Generate a version.json file for tracking."""
        version_file = self.helm_dir / "charts" / "kubeflow" / "version.json"

        version_data = {
            "git": git_info,
            "helm_chart": {
                "name": "kubeflow",
                "description": "Kubeflow Helm Chart",
                "generated_from": "kustomize"
            }
        }

        with open(version_file, 'w') as f:
            json.dump(version_data, f, indent=2)

        print(f"Generated version file: {version_file}")

    def run(self):
        """Run version management."""
        print("=" * 60)
        print("Git Version Manager for Kubeflow Helm Charts")
        print("=" * 60)
        print()

        # Get git info
        print("Fetching git information from kustomize directory...")
        git_info = self.get_git_info()

        if not git_info:
            print("Failed to get git information!")
            return

        print(f"  Commit: {git_info['commit']}")
        print(f"  Branch: {git_info['branch']}")
        print(f"  Date: {git_info['commit_date']}")
        if git_info.get('tag'):
            print(f"  Tag: {git_info['tag']}")
        print()

        # Update Chart.yaml
        print("Updating Chart.yaml with version annotations...")
        self.update_chart_yaml(git_info)
        print()

        # Generate version.json
        print("Generating version.json file...")
        self.generate_version_file(git_info)
        print()

        print("=" * 60)
        print("Version management complete!")
        print("=" * 60)


def main():
    """Main entry point."""
    import argparse

    parser = argparse.ArgumentParser(
        description="Git Version Manager for Kubeflow Helm Charts"
    )
    parser.add_argument(
        "--kustomize-dir",
        default="../kustomize",
        help="Path to kustomize directory (default: ../kustomize)"
    )
    parser.add_argument(
        "--helm-dir",
        default=".",
        help="Path to helm directory (default: .)"
    )

    args = parser.parse_args()

    manager = VersionManager(
        kustomize_dir=args.kustomize_dir,
        helm_dir=args.helm_dir
    )
    manager.run()


if __name__ == "__main__":
    main()
