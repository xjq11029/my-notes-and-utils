"""提示词渲染：Jinja2 模板 + 运行环境变量。

系统提示词的四个动态变量（cwd / os / is_git / skills）在启动时渲染一次。
模板与代码分离：改提示词不用改代码，这就是模板引擎的价值。
"""
import os
import platform
import subprocess

from jinja2 import Environment, FileSystemLoader

_TEMPLATE_DIR = os.path.join(os.path.dirname(__file__), "prompt")


def get_cwd() -> str:
    return os.getcwd()


def get_os() -> str:
    return platform.system()


def get_is_git() -> bool:
    """判断当前目录是否在 Git 仓库内（沙箱/无 git 环境返回 False）。"""
    try:
        result = subprocess.run(
            ["git", "rev-parse", "--is-inside-work-tree"],
            capture_output=True, text=True, timeout=5,
        )
        return result.returncode == 0 and result.stdout.strip() == "true"
    except Exception:
        return False


def render_prompt(name: str = "system", **extra) -> str:
    """渲染模板。内置环境变量 + 任意额外变量（如技能清单 skills）。"""
    env = Environment(loader=FileSystemLoader(_TEMPLATE_DIR), keep_trailing_newline=True)
    template = env.get_template(f"{name}.j2")
    return template.render(
        cwd=get_cwd(),
        os=get_os(),
        is_git=get_is_git(),
        **extra,
    )
