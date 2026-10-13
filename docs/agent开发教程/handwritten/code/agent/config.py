"""环境配置：从环境变量读取 OpenAI 兼容服务配置。

从零手写，不引入 pydantic-settings——三个 os.getenv 就够了。
生产项目可以换成 pydantic-settings，获得 .env 加载、类型校验与默认值管理。
"""
import os


class Settings:
    """OpenAI 兼容服务配置。

    环境变量：
        OPENAI_API_KEY   API 密钥（离线运行留空，示例脚本显式注入假模型）
        OPENAI_BASE_URL  服务地址（可选；Ollama 为 http://localhost:11434/v1）
        OPENAI_MODEL     模型名
    """

    def __init__(self) -> None:
        self.api_key = os.getenv("OPENAI_API_KEY", "")
        self.base_url = os.getenv("OPENAI_BASE_URL", "")
        self.model = os.getenv("OPENAI_MODEL", "gpt-4o-mini")


settings = Settings()
