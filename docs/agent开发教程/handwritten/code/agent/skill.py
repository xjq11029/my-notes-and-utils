"""技能（Skill）：按需加载的提示词包，核心机制是「渐进式披露」。

问题：智能客服的产品知识、SaaS 的数据分析规范……这些提示词只在
特定场景才用得上，全部塞进系统提示词会造成「提示词膨胀」。

两步机制：
1. 启动时扫描 skills 目录，把每个 SKILL.md 的 name + description
   注入系统提示词——每个技能只花几十 token，模型知道「有哪些技能」；
2. 模型判断需要某个技能时，调用 load_skill 工具拿全文——这时才付出
   完整上下文的代价。

没命中几乎零成本，命中才付全文价格——这就是渐进式披露。
"""
import os

from agent.tool import tool


def parse_frontmatter(text: str) -> dict:
    """解析 SKILL.md 头部的 YAML frontmatter。

    只支持简单的 key: value 行（够 SKILL.md 用），不引入 PyYAML。
    """
    meta: dict[str, str] = {}
    if not text.startswith("---"):
        return meta
    for line in text.split("\n")[1:]:
        if line.strip() == "---":
            break
        if ":" in line:
            key, _, value = line.partition(":")
            meta[key.strip()] = value.strip()
    return meta


class SkillRegistry:
    """技能注册表：扫描目录、维护清单、按名加载全文。"""

    def __init__(self, *skill_dirs: str) -> None:
        self.skill_dirs = list(skill_dirs)
        self._skills: dict[str, dict] = {}
        self.scan()

    def scan(self) -> None:
        """扫描所有技能目录下的 <name>/SKILL.md。"""
        self._skills.clear()
        for d in self.skill_dirs:
            if not os.path.isdir(d):
                continue
            for entry in sorted(os.listdir(d)):
                path = os.path.join(d, entry, "SKILL.md")
                if not os.path.isfile(path):
                    continue
                with open(path, encoding="utf-8") as f:
                    meta = parse_frontmatter(f.read())
                name = meta.get("name", entry)
                self._skills[name] = {
                    "name": name,
                    "description": meta.get("description", ""),
                    "path": path,
                }

    def list_skills(self) -> list[dict]:
        """技能清单（注入系统提示词的那份：只有 name + description）。"""
        return [{"name": s["name"], "description": s["description"]}
                for s in self._skills.values()]

    def load(self, name: str) -> str:
        """读取技能全文（模型通过 load_skill 工具调用）。"""
        skill = self._skills.get(name)
        if skill is None:
            return f"错误：没有名为 {name} 的技能。可用技能：{', '.join(self._skills) or '无'}"
        with open(skill["path"], encoding="utf-8") as f:
            return f.read()


def make_load_skill_tool(skills: SkillRegistry):
    """工厂：为给定 SkillRegistry 生成 load_skill 工具（闭包持有注册表）。"""

    @tool(name="要加载的技能名，来自系统提示词中的可用技能清单")
    def load_skill(name: str) -> str:
        """读取一个技能的完整说明（SKILL.md 全文），按说明执行该领域的任务"""
        return skills.load(name)

    return load_skill
