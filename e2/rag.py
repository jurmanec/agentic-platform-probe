"""Lexical retrieve → generate → cite / fail-closed for E2.

Uses keyword scoring over corpus chunks (no hosted embedding API). Generation
uses xAI via ChatXAI. Fail closed when retrieval scores are too low.
"""

from __future__ import annotations

import json
import os
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from langchain_core.messages import HumanMessage, SystemMessage
from langchain_xai import ChatXAI

CORPUS_DIR = Path(__file__).resolve().parent / "corpus"
DEFAULT_MODEL = "grok-3-fast"
TOP_K = 3
# Minimum keyword overlap score to treat retrieval as evidence.
# Score is count of shared tokens (len > 2); require at least 2 to reduce weak matches.
MIN_SCORE = 2.0

_STOPWORDS = frozenset(
    """
    a an the and or but if in on at to for of from with by as is are was were be been
    being have has had do does did will would can could should may might must
    this that these those it its they them their we our you your what which who
    when where why how not no nor so than then too very just also into over after
    before about between through during
    """.split()
)

SYSTEM_GROUNDED = """You are a marketing-ops documentation assistant.

Answer ONLY using the provided context excerpts. If the context is insufficient,
say you do not know. Do not invent budgets, policies, products, or rules.

When you answer, be concise. Do not invent citation IDs — the CLI attaches citations.
"""

@dataclass
class Chunk:
    doc_id: str
    path: str
    text: str
    score: float = 0.0


def _tokenize(text: str) -> set[str]:
    return {
        t
        for t in re.findall(r"[a-z0-9_]+", text.lower())
        if len(t) > 2 and t not in _STOPWORDS
    }


def load_chunks(corpus_dir: Path | None = None) -> list[Chunk]:
    root = corpus_dir or CORPUS_DIR
    chunks: list[Chunk] = []
    for path in sorted(root.glob("*.md")):
        text = path.read_text(encoding="utf-8").strip()
        if not text:
            continue
        # Split on markdown headings for slightly better locality.
        parts = re.split(r"(?=^## )", text, flags=re.MULTILINE)
        for i, part in enumerate(parts):
            part = part.strip()
            if not part:
                continue
            doc_id = f"{path.name}#{i}"
            chunks.append(Chunk(doc_id=doc_id, path=path.name, text=part))
    return chunks


def retrieve(query: str, chunks: list[Chunk] | None = None, top_k: int = TOP_K) -> list[Chunk]:
    pool = chunks if chunks is not None else load_chunks()
    q_tokens = _tokenize(query)
    if not q_tokens:
        return []
    scored: list[Chunk] = []
    for ch in pool:
        overlap = len(q_tokens & _tokenize(ch.text))
        if overlap <= 0:
            continue
        scored.append(
            Chunk(doc_id=ch.doc_id, path=ch.path, text=ch.text, score=float(overlap))
        )
    scored.sort(key=lambda c: c.score, reverse=True)
    return scored[:top_k]

def _format_context(chunks: list[Chunk]) -> str:
    blocks = []
    for i, ch in enumerate(chunks, start=1):
        blocks.append(f"[{i}] source={ch.path} id={ch.doc_id}\n{ch.text}")
    return "\n\n".join(blocks)


def answer_query(
    *,
    query: str,
    model_name: str | None = None,
    top_k: int = TOP_K,
    min_score: float = MIN_SCORE,
) -> dict[str, Any]:
    api_key = os.environ.get("XAI_API_KEY", "").strip()
    if not api_key:
        raise SystemExit(
            "XAI_API_KEY is not set. Copy .env.example to .env and add your key."
        )

    hits = retrieve(query, top_k=top_k)
    evidence = [h for h in hits if h.score >= min_score]

    if not evidence:
        return {
            "query": query,
            "answer": (
                "I do not have enough information in the marketing-ops corpus "
                "to answer that question."
            ),
            "citations": [],
            "status": "unknown",
            "retrieval": {
                "method": "lexical",
                "hit_count": 0,
                "min_score": min_score,
            },
        }

    model_id = model_name or os.environ.get("XAI_MODEL", DEFAULT_MODEL)
    llm = ChatXAI(model=model_id, temperature=0, api_key=api_key)
    context = _format_context(evidence)
    messages = [
        SystemMessage(content=SYSTEM_GROUNDED), 
        HumanMessage(
            content=(
                f"Context:\n{context}\n\n"
                f"Question: {query}\n\n"
                "Answer using only the context. If insufficient, say you do not know."
            )
        ),
    ]
    ai = llm.invoke(messages)
    content = getattr(ai, "content", "") or ""
    if isinstance(content, list):
        # Some providers return content blocks; flatten text.
        content = "".join(
            block.get("text", "") if isinstance(block, dict) else str(block)
            for block in content
        )

    # If the model refuses despite evidence, still report answered with citations
    # only when it clearly used the context; keep simple: always attach citations
    # when we had evidence, unless the answer explicitly says unknown.
    lowered = content.lower()
    refused = (
        "do not know" in lowered
        or "don't know" in lowered
        or "insufficient" in lowered
        or "not enough information" in lowered
    )

    citations = [
        {
            "doc_id": h.doc_id,
            "path": h.path,
            "score": h.score,
            "excerpt": h.text[:240] + ("…" if len(h.text) > 240 else ""),
        }
        for h in evidence
    ]

    if refused:
        return {
            "query": query,
            "answer": content.strip(),
            "citations": [],
            "status": "unknown",
            "retrieval": {
                "method": "lexical",
                "hit_count": len(evidence),
                "min_score": min_score,
            },
        }

    return {
        "query": query,
        "answer": content.strip(),
        "citations": citations,
        "status": "answered",
        "retrieval": {
            "method": "lexical",
            "hit_count": len(evidence),
            "min_score": min_score,
        },
    }


# Convenience for debugging without LLM
def debug_retrieve(query: str) -> str:
    hits = retrieve(query)
    return json.dumps(
        [{"doc_id": h.doc_id, "path": h.path, "score": h.score} for h in hits],
        indent=2,
    )
