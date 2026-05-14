#!/usr/bin/env python3
from __future__ import annotations

import sys
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
APP_ROOT = REPO_ROOT / "AppAgentX"
sys.path.insert(0, str(APP_ROOT))


def mask(value: str) -> str:
    if not value:
        return "<empty>"
    if len(value) <= 8:
        return "<set>"
    return f"{value[:4]}...{value[-4:]}"


def verify_config_import():
    import config

    required = {
        "LLM_BASE_URL": config.LLM_BASE_URL,
        "LLM_API_KEY": config.LLM_API_KEY,
        "LLM_MODEL": config.LLM_MODEL,
        "Neo4j_URI": config.Neo4j_URI,
        "Neo4j_AUTH_USER": config.Neo4j_AUTH[0],
        "Neo4j_AUTH_PASSWORD": config.Neo4j_AUTH[1],
        "PINECONE_API_KEY": config.PINECONE_API_KEY,
    }
    missing = [key for key, value in required.items() if not value]
    if missing:
        raise RuntimeError(f"missing config fields: {','.join(missing)}")

    if config.LLM_API_KEY in {"sk-", "填你的key"}:
        raise RuntimeError("LLM_API_KEY still looks like a placeholder")
    if config.PINECONE_API_KEY in {"pcsk_", "填你的key"}:
        raise RuntimeError("PINECONE_API_KEY still looks like a placeholder")
    if config.Neo4j_AUTH[1] in {"12345678", "填你的password"}:
        raise RuntimeError("Neo4j password still looks like a placeholder")

    print("config_import_ok")
    print("llm_base_url", config.LLM_BASE_URL)
    print("llm_model", config.LLM_MODEL)
    print("neo4j_uri_prefix_ok", config.Neo4j_URI.startswith(("neo4j://", "neo4j+s://", "bolt://", "bolt+s://")))
    print("neo4j_user", config.Neo4j_AUTH[0])
    print("llm_api_key", mask(config.LLM_API_KEY))
    print("pinecone_api_key", mask(config.PINECONE_API_KEY))
    return config


def verify_llm(config):
    import httpx
    from openai import OpenAI

    http_client = httpx.Client(trust_env=False, timeout=30)
    client = OpenAI(
        api_key=config.LLM_API_KEY,
        base_url=config.LLM_BASE_URL,
        http_client=http_client,
        timeout=30,
        max_retries=1,
    )
    response = client.chat.completions.create(
        model=config.LLM_MODEL,
        messages=[
            {
                "role": "user",
                "content": "Return exactly this text in the final answer: OK",
            }
        ],
        max_tokens=64,
    )
    if not response.choices:
        raise RuntimeError("empty LLM choices")
    content = response.choices[0].message.content or ""
    finish_reason = response.choices[0].finish_reason
    print("llm_request_ok")
    print("llm_response_nonempty", bool(content.strip()))
    print("llm_finish_reason", finish_reason)


def verify_neo4j(config):
    from neo4j import GraphDatabase

    driver = GraphDatabase.driver(
        config.Neo4j_URI,
        auth=config.Neo4j_AUTH,
        connection_timeout=10,
    )
    try:
        driver.verify_connectivity()
        print("neo4j_connectivity_ok")
    finally:
        driver.close()


def verify_pinecone(config):
    from pinecone import Pinecone

    pc = Pinecone(api_key=config.PINECONE_API_KEY)
    pc.list_indexes()
    print("pinecone_connectivity_ok")


def main() -> int:
    config = verify_config_import()
    checks = [
        ("llm", lambda: verify_llm(config)),
        ("neo4j", lambda: verify_neo4j(config)),
        ("pinecone", lambda: verify_pinecone(config)),
    ]
    failures = []
    for name, check in checks:
        try:
            check()
        except Exception as exc:
            failures.append(name)
            print(f"{name}_failed", type(exc).__name__, str(exc).splitlines()[0])

    if failures:
        print("step3_config_services_failed", ",".join(failures))
        return 1

    print("step3_config_services_ok")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
