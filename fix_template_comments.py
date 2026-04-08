#!/usr/bin/env python3
"""
Fix Helm template comments that contain {{ }} syntax
which causes Helm to try to parse them as variables.
"""

from pathlib import Path


def wrap_yaml_comments_to_helm(yaml_content: str) -> str:
    """
    修复版：
    1. 连续 # 注释 + 中间空行 → 合并为一个完整 Helm 注释
    2. 注释块 最前 / 最后 的空行不包裹
    3. 注释块 内部空行 保留
    4. 输出格式 {{/* 内容 */}}
    """
    lines = yaml_content.splitlines(keepends=True)
    result = []
    comment_block = []  # 收集当前连续注释块（#行 + 内部空行）

    for line in lines:
        stripped = line.strip()
        is_comment_line = stripped.startswith("#")
        is_blank = stripped == ""

        # ------------------- 核心修复 -------------------
        # 是注释 或 内部空行 → 继续收集到同一个注释块
        if is_comment_line or (is_blank and comment_block):
            comment_block.append(line)
        
        # 不是注释、也不是注释块内部空行 → 结束注释块
        else:
            # 如果有正在收集的注释，先输出
            if comment_block:
                comment_content = "".join(comment_block).rstrip("\n")
                helm_comment = f"{{/*\n{comment_content}\n*/}}"
                result.append(helm_comment + "\n")
                comment_block = []

            # 把当前非注释行加进去（空行 / YAML 内容）
            result.append(line)

    # 处理文件末尾残留的注释块
    if comment_block:
        comment_content = "".join(comment_block).rstrip("\n")
        helm_comment = f"{{/*\n{comment_content}\n*/}}"
        result.append(helm_comment + "\n")

    return "".join(result)



def fix_template_file(filepath):
    """Fix template syntax in comments."""
    original = filepath.read_text()
    content = wrap_yaml_comments_to_helm(original)  # 先把注释块转换成 Helm 注释
    if content != original:
        filepath.write_text(content)
        print(f"Fixed: {filepath}")
        return True
    return False


def main():
    '''fix the templates after the kustomize manifest converted'''
    templates_dir = Path("/root/manifests/helm/charts/kubeflow/templates")

    fixed_count = 0
    for yaml_file in templates_dir.rglob("*.yaml"):
        if fix_template_file(yaml_file):
            fixed_count += 1

    print(f"\nTotal files fixed: {fixed_count}")

if __name__ == "__main__":
    main()
