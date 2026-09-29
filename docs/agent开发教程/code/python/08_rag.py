# -*- coding: utf-8 -*-
"""第 8 章示例：RAG 全链路 —— Load → Split → Embed → Store → Retrieve。

演示五件事：
  1. 文档加载器（Loader）的本质：把任意文件变成 Document(page_content, metadata)
  2. 文档切分器（TextSplitter）：三个方法的调用链，以及两种实现的差别
  3. 嵌入模型（Embeddings）：embed_documents 与 embed_query 的区别
  4. 向量存储（VectorStore）：写入、相似度检索，以及「检索质量决定 RAG 上限」
  5. 把检索器包成 @tool 交给 agent —— 检索是一个工具，不是一个步骤

⚠️ 本示例全程离线、零 API Key：
   · 用 DeterministicFakeEmbedding 代替真实嵌入模型（向量是假的，但**可复现**）
   · 用 FakeEmbeddings 做一次对照，证明它每次调用结果都不同，只够验证管道
   · 用 _fake_model.py 的 ScriptedChatModel 代替真实 LLM

   所以本示例验证的是**链路通不通**，不是**检索准不准**。
   假嵌入的向量没有语义，检索排序不代表相关性。

运行：python 08_rag.py
"""

import atexit
import json
import logging
import shutil
import sys
import tempfile
import warnings
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    # line_buffering：让 print 与 logging（走 stderr）的输出顺序保持真实先后，
    # 否则重定向到文件时 stderr 会全部挤到最前面。
    sys.stdout.reconfigure(encoding="utf-8", line_buffering=True)

# langchain-community 0.4.2 已进入 sunset，import 时会打印一次 DeprecationWarning。
# 本节只借它的 Loader 讲「文件 → Document」这件事，与 sunset 无关，静音以保持输出干净。
warnings.filterwarnings("ignore", category=DeprecationWarning)

from langchain.agents import create_agent
from langchain.tools import tool
from langchain_community.document_loaders import (
    CSVLoader,
    DirectoryLoader,
    JSONLoader,
    PyPDFLoader,
    TextLoader,
)
from langchain_core.documents import Document
from langchain_core.embeddings import DeterministicFakeEmbedding, FakeEmbeddings
from langchain_core.vectorstores import InMemoryVectorStore
from langchain_text_splitters import CharacterTextSplitter, RecursiveCharacterTextSplitter

from _fake_model import ScriptedChatModel, reply, show, tool_call


# ---------------------------------------------------------------------------
# 0. 现场造一份「私有语料」——本示例不依赖任何外部素材
# ---------------------------------------------------------------------------
TMP = Path(tempfile.mkdtemp(prefix="rag_demo_"))
atexit.register(shutil.rmtree, TMP, ignore_errors=True)


def _build_min_pdf(text: str) -> bytes:
    """手搓一个最小的合法 PDF（单页 + 一行文本），用来实测 PyPDFLoader。

    真正的 PDF 由生成器产出；这里手工拼是为了让示例**自包含**——
    不下载、不依赖外部文件，同时又能走通 pypdf 的解析路径。
    """
    content = f"BT /F1 12 Tf 72 720 Td ({text}) Tj ET".encode("latin-1")
    bodies = [
        b"<< /Type /Catalog /Pages 2 0 R >>",
        b"<< /Type /Pages /Kids [3 0 R] /Count 1 >>",
        b"<< /Type /Page /Parent 2 0 R /MediaBox [0 0 612 792] /Contents 4 0 R "
        b"/Resources << /Font << /F1 5 0 R >> >> >>",
        b"<< /Length " + str(len(content)).encode() + b" >>\nstream\n" + content + b"\nendstream",
        b"<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica >>",
    ]
    out = bytearray(b"%PDF-1.4\n")
    offsets: list[int] = []
    for i, body in enumerate(bodies, 1):
        offsets.append(len(out))
        out += f"{i} 0 obj\n".encode() + body + b"\nendobj\n"
    xref_pos = len(out)
    out += f"xref\n0 {len(bodies) + 1}\n".encode() + b"0000000000 65535 f \n"
    for off in offsets:
        out += f"{off:010d} 00000 n \n".encode()
    out += (
        f"trailer\n<< /Size {len(bodies) + 1} /Root 1 0 R >>\n"
        f"startxref\n{xref_pos}\n%%EOF\n"
    ).encode()
    return bytes(out)


(TMP / "notes.txt").write_text(
    "RAG 的第一条铁律：检索质量决定生成质量。\n"
    "如果检索回来的片段本身不相关，再强的模型也只能编。\n",
    encoding="utf-8",
)
(TMP / "orders.csv").write_text(
    "order_id,product,status\n"
    "A-1001,机械键盘,已发货\n"
    "A-1002,人体工学椅,待发货\n"
    "A-1003,显示器支架,已签收\n",
    encoding="utf-8",
)
(TMP / "faq.json").write_text(
    json.dumps(
        [
            {"q": "RAG 是什么", "a": "检索增强生成，提问前先把相关资料塞进上下文。"},
            {"q": "为什么要切分", "a": "为了控制单次进上下文的文本长度，并提高检索命中率。"},
        ],
        ensure_ascii=False,
    ),
    encoding="utf-8",
)
(TMP / "guide.md").write_text(
    "# 部署说明\n\n生产环境请把向量库换成 Milvus 或 Chroma。\n",
    encoding="utf-8",
)
(TMP / "manual.pdf").write_bytes(_build_min_pdf("RAG means retrieval augmented generation."))


def _name(source: str) -> str:
    """只打印文件名——临时目录的绝对路径每次运行都不同，打全路径没法复现。"""
    return Path(source).name


def _meta(doc: Document) -> dict:
    """打印 metadata 时把 source 换成文件名，保证输出可复现。"""
    return {**doc.metadata, "source": _name(doc.metadata["source"])}


def _flat(text: str, width: int = 44) -> str:
    """把多行文本压成一行并截断，便于在终端里对照。"""
    one = " / ".join(text.splitlines())
    return one if len(one) <= width else one[: width - 3] + "..."


# ---------------------------------------------------------------------------
# 1. Loader 的本质：文件 → Document(page_content, metadata)
# ---------------------------------------------------------------------------
print("=" * 60)
print("① 文档加载器：所有 Loader 都只做一件事——文件 → Document")
print("=" * 60)

txt_docs = TextLoader(str(TMP / "notes.txt"), encoding="utf-8").load()
print(f"  [TextLoader]  {_name(txt_docs[0].metadata['source'])}  → {len(txt_docs)} 个 Document")
print(f"      page_content = {_flat(txt_docs[0].page_content)!r}")
print(f"      metadata     = {_meta(txt_docs[0])}")
print("      → 整个文件是一整条 page_content：Loader 不做任何切分。")

csv_docs = CSVLoader(str(TMP / "orders.csv"), encoding="utf-8").load()
print(f"\n  [CSVLoader]   orders.csv  → {len(csv_docs)} 个 Document（每行一条）")
for d in csv_docs[:2]:
    print(f"      {_flat(d.page_content)!r}   metadata={_meta(d)}")
print("      → 列名被拼进了 page_content，行号落在 metadata['row']。")

json_docs = JSONLoader(
    str(TMP / "faq.json"),
    jq_schema=".[]",                                  # jq 语法：遍历数组每个元素
    content_key="a",                                  # 哪个字段当正文
    metadata_func=lambda rec, meta: {**meta, "q": rec.get("q")},  # 其余字段进 metadata
    text_content=False,
).load()
print(f"\n  [JSONLoader]  faq.json  → {len(json_docs)} 个 Document")
for d in json_docs:
    print(f"      {_flat(d.page_content)!r}   metadata={_meta(d)}")
print("      → jq_schema 决定「切成几条」，content_key 决定「哪部分是正文」。")

pdf_docs = PyPDFLoader(str(TMP / "manual.pdf")).load()
print(f"\n  [PyPDFLoader] manual.pdf → {len(pdf_docs)} 个 Document（**每页一条**）")
print(f"      page_content = {_flat(pdf_docs[0].page_content)!r}")
print(f"      metadata     = {_meta(pdf_docs[0])}")
print("      → 页码在 metadata['page'] 里；后面要引用出处，靠的就是它。")

dir_docs = DirectoryLoader(
    str(TMP),
    glob="*.md",
    loader_cls=TextLoader,                 # ⚠️ 默认是 UnstructuredFileLoader（需额外装包）
    loader_kwargs={"encoding": "utf-8"},
).load()
print(f"\n  [DirectoryLoader] glob='*.md' → {len(dir_docs)} 个 Document")
print(f"      {_flat(dir_docs[0].page_content)!r}")
print("      → 批量加载只是「遍历文件 + 逐个套 Loader」，没有任何魔法。")
print("\n  结论：Loader 的产物永远是 Document；差异只在两件事——")
print("        ① 一个文件切几条（整文件 / 每行 / 每页 / 每条记录）")
print("        ② metadata 里留下什么（source / row / page / 自定义字段）")


# ---------------------------------------------------------------------------
# 2. 切分器：split_text → create_documents → split_documents
# ---------------------------------------------------------------------------
print()
print("=" * 60)
print("② 文档切分器：三个方法其实是同一条调用链")
print("=" * 60)

# CharacterTextSplitter 切出超长 chunk 时用的是 logging.warning，不是 warnings.warn——
# 默认不配 logging 就什么都看不见。这里显式打开，好让下面那条警告出现在输出里。
logging.basicConfig(level=logging.WARNING, format="      [WARNING] %(message)s")

raw = (
    "检索增强生成的第一步，是把私有文档切成语义完整的片段。切得太碎会丢失上下文。"
    "\n\n"
    "切得太大会稀释关键词，所以 chunk_size 与 chunk_overlap 这两个参数要按语料来调。"
)

char_splitter = CharacterTextSplitter(chunk_size=30, chunk_overlap=0, separator="\n\n")
rec_splitter = RecursiveCharacterTextSplitter(chunk_size=30, chunk_overlap=0)

print(f"  原文共 {len(raw)} 字，含一个空行（分两段）")

print("\n  [CharacterTextSplitter] separator='\\n\\n'：")
char_chunks = char_splitter.split_text(raw)   # ← 超长 chunk 的 WARNING 在这里打出
print(f"      → {len(char_chunks)} 个 chunk")
for c in char_chunks:
    print(f"      {len(c):>3} 字 | {c}")
print("      → 只认 '\\n\\n'：切完就交差，长度**超过** chunk_size 也不管（38 > 30、53 > 30）。")
print("        上面那条 WARNING 是它唯一的提示，而且走的是 logging，默认看不见。")

rec_chunks = rec_splitter.split_text(raw)
print(f"\n  [RecursiveCharacterTextSplitter] → {len(rec_chunks)} 个 chunk")
for c in rec_chunks:
    print(f"      {len(c):>3} 字 | {c}")
print(f"      → 依次尝试 {rec_splitter._separators}，粗的切不动就换更细的，")
print("        所以默认选它：它保证「不超过 chunk_size」，代价是可能切在句子中间。")

overlap_chunks = RecursiveCharacterTextSplitter(chunk_size=30, chunk_overlap=6).split_text(raw)
print(f"\n  chunk_overlap=6 的同一段文本 → {len(overlap_chunks)} 个 chunk")
for c in overlap_chunks:
    print(f"      {len(c):>3} 字 | {c}")
print("      → overlap 让相邻 chunk 共享尾巴，避免答案正好被切断在边界上。")

print("\n  三个方法的调用链（实测）——")
print("      split_text(text)            → list[str]        只切文本")
print("      create_documents(texts)     → list[Document]   切文本 + 挂 metadata")
print("      split_documents(docs)       → list[Document]   切 Document + 继承 metadata")
docs = rec_splitter.create_documents([raw], metadatas=[{"source": "inline"}])
print(f"      create_documents(['…']) → {len(docs)} 个 Document，metadata={docs[0].metadata}")
split_from_doc = rec_splitter.split_documents(txt_docs)
print(f"      split_documents(1 个 Document) → {len(split_from_doc)} 个 Document，")
print(f"        metadata={_meta(split_from_doc[0])}  ← source 被继承下来了")


# ---------------------------------------------------------------------------
# 3. 嵌入：embed_documents vs embed_query
# ---------------------------------------------------------------------------
print()
print("=" * 60)
print("③ 嵌入模型：把文本映射成向量，两个方法分工不同")
print("=" * 60)

embedder = DeterministicFakeEmbedding(size=8)
vec_docs = embedder.embed_documents(["机械键盘已发货", "显示器支架已签收"])
vec_query = embedder.embed_query("键盘到哪了")
print(f"  embed_documents(['机械键盘已发货', '显示器支架已签收']) → {len(vec_docs)} 个向量")
print(f"      第 1 个向量的前 4 维 = {[round(float(x), 3) for x in vec_docs[0][:4]]}")
print(f"  embed_query('键盘到哪了') → 1 个向量")
print(f"      前 4 维 = {[round(float(x), 3) for x in vec_query[:4]]}")
print(f"      维度 = {len(vec_query)}（与 embed_documents 必须一致，否则算不了相似度）")
print("\n  为什么要分成两个方法？——因为有些真实嵌入模型对「文档」和「查询」用不同的")
print("  编码方式（比如非对称检索模型），入库走 embed_documents、检索走 embed_query。")
print("  维度一致是硬约束：混用两个不同模型建的库，检索时直接报错。")

random_embedder = FakeEmbeddings(size=8)
a = random_embedder.embed_query("同一句话")
b = random_embedder.embed_query("同一句话")
print(f"\n  ⚠️ 对照：FakeEmbeddings 对**同一句话**连续调两次，")
print(f"      向量是否相同 = {a == b}   ← 每次都是新的随机向量")
print("     所以 FakeEmbeddings 只够验证「管道通不通」，检索排序毫无意义；")
print("     DeterministicFakeEmbedding 至少同文本同向量，输出可复现——本示例后面用它。")


# ---------------------------------------------------------------------------
# 4. 向量库：写入 + 相似度检索
# ---------------------------------------------------------------------------
print()
print("=" * 60)
print("④ 向量存储：写入语料，再按相似度取回")
print("=" * 60)

chunks = RecursiveCharacterTextSplitter(chunk_size=80, chunk_overlap=10).split_documents(
    csv_docs + json_docs + dir_docs
)
print(f"  待入库 chunk 数 = {len(chunks)}（来自 CSV + JSON + Markdown）")
print("  （上面 ② 用的是 chunk_size=30，演示「切得细」；这里语料每篇都很短，")
print("    chunk_size 设成 80 才不会把一行订单拆成两半——这就是按语料调参。）")
for i, c in enumerate(chunks, 1):
    print(f"      [{i}] {_flat(c.page_content, 40)}  ← {_name(c.metadata['source'])}")

store = InMemoryVectorStore(embedding=embedder)
store.add_documents(chunks)
print(f"\n  store.add_documents(...) → 写入完成；InMemoryVectorStore 存在内存里，进程退出即消失。")

hits = store.similarity_search_with_score("键盘", k=2)
print("\n  similarity_search_with_score('键盘', k=2)：")
for rank, (doc, score) in enumerate(hits, 1):
    print(f"      #{rank} score={score:.4f} | {_flat(doc.page_content, 34)} | 源={_name(doc.metadata['source'])}")
print("      → 返回 (Document, score) 二元组，Document 里连 metadata 一起带回来了——")
print("        这正是「回答时能标注出处」的原因。")
print("\n  ⚠️ 分数本身不要当真：假嵌入的向量没有语义，这个排序**不代表相关性**。")
print("     真实场景换成真实嵌入模型，同一段代码才谈得上「检索质量」。")

retriever = store.as_retriever(search_kwargs={"k": 2})
got = retriever.invoke("切分")
print(f"\n  store.as_retriever(search_kwargs={{'k': 2}}).invoke('切分') → {len(got)} 个 Document")
print("      → Retriever 是「只进不出的检索接口」：输入一句查询，输出一组 Document。")
print("        它是向量库和 agent 之间的标准接缝——下一节就把它包成工具。")


# ---------------------------------------------------------------------------
# 5. 把 retriever 包成 @tool，交给 agent
# ---------------------------------------------------------------------------
print()
print("=" * 60)
print("⑤ 接进 agent：检索是一个工具，不是一个步骤")
print("=" * 60)


@tool
def search_knowledge(query: str) -> str:
    """在内部知识库里检索与 query 最相关的片段。

    Args:
        query: 检索关键词或自然语言问题
    """
    found = retriever.invoke(query)
    if not found:
        return "没有检索到相关片段。"
    return "\n\n".join(
        f"[{i}] ({_name(d.metadata['source'])}) {d.page_content}"
        for i, d in enumerate(found, 1)
    )


print(f"  工具名 = {search_knowledge.name!r}")
print(f"  工具描述 = {search_knowledge.description!r}")
print("  → 模型看不到向量库、看不到 retriever，它只看到这个工具的 schema。")

agent = create_agent(
    model=ScriptedChatModel(
        script=[
            tool_call("search_knowledge", {"query": "切分"}, "c1"),
            reply("根据知识库：切分是为了控制单次进上下文的长度，并提高检索命中率。"),
        ]
    ),
    tools=[search_knowledge],
)
out = agent.invoke({"messages": [{"role": "user", "content": "为什么要做文档切分？"}]})
show(out["messages"])
print()
print("  → 模型先请求 search_knowledge，框架执行检索、把片段包成 ToolMessage 回灌，")
print("    模型再据此作答。这就是 RAG 的在线半程；离线半程（切分 / 嵌入 / 入库）")
print("    在上面 ①–④ 已经跑完，两半完全解耦。")
print("  → 注意：本示例里模型是脚本化的，所以「先检索再回答」是写死的；")
print("    真实模型才会自己判断要不要检索、检索什么——那部分需 API Key，未实测。")
