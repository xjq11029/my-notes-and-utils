# -*- coding: utf-8 -*-
"""第 19 章配套：一个可被 `langgraph dev` / Agent Server 加载的最小图。

部署配置见同目录 `langgraph.json`：
    dependencies: ["."]
    graphs: {"agent": "./19_deploy_agent.py:graph"}

本地验证：
    langgraph validate -c langgraph.json
    langgraph dev -c langgraph.json --no-browser

这是 Python-only 的部署样例：LangGraph CLI 与 Agent Server 由 Python 侧分发，
TS 侧没有同等的本地 `langgraph dev` 运行样例（第 19 章正文标注了这个例外）。
"""

from typing import TypedDict

from langgraph.graph import END, START, StateGraph


class DeployState(TypedDict):
    question: str
    answer: str


def answer(state: DeployState) -> dict:
    return {"answer": f"echo: {state['question']}"}


graph = (
    StateGraph(DeployState)
    .add_node("answer", answer)
    .add_edge(START, "answer")
    .add_edge("answer", END)
    .compile()
)


if __name__ == "__main__":
    print(graph.invoke({"question": "hello", "answer": ""}))
