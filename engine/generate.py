#!/usr/bin/env python3
"""
DevOps Bootcamp — AI quiz/drill generator (Anthropic API).
Tashqi SDK kerak emas (urllib). Prompt caching bilan arzon.

Key manbai (shu tartibda):
  1. ANTHROPIC_API_KEY muhit o'zgaruvchisi
  2. engine/config.json -> {"anthropic_api_key": "sk-ant-..."}

Foydalanish:
  python3 generate.py --topic linux --difficulty 2 --n 20
  python3 generate.py --bulk            # barcha mavzu/darajalar bo'yicha to'ldirish
  python3 generate.py --model claude-haiku-4-5 ...   # arzonroq model
"""
import argparse
import json
import os
import sys
import time
import urllib.request

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import db  # noqa: E402

CONFIG = os.path.join(db.ENGINE_DIR, "config.json")
API_URL = "https://api.anthropic.com/v1/messages"
DEFAULT_MODEL = "claude-sonnet-4-6"   # sifat uchun; --model claude-haiku-4-5 = arzonroq

SYSTEM = (
    "You are an expert DevOps instructor creating high-quality multiple-choice quiz "
    "questions for an Uzbek-speaking learner. Rules:\n"
    "- Questions, options and explanations in UZBEK (latin script); keep technical "
    "terms/commands in English (e.g. 'chmod', 'Deployment').\n"
    "- Exactly 4 options each. Exactly ONE correct. Plausible distractors.\n"
    "- 'correct' is the 0-based index of the right option.\n"
    "- 'explanation' must be ONE short sentence teaching WHY.\n"
    "- Factually correct and verifiable. No trick questions.\n"
    "- Difficulty 1=basic recall ... 5=advanced reasoning.\n"
    "- Output ONLY a valid JSON array, no prose, no markdown fences."
)

# mavzu -> (foydalanuvchiga ko'rsatma uchun) tavsif
TOPICS = {
    "linux": "Linux filesystem, permissions, processes, systemd, text tools",
    "bash": "Bash scripting: variables, conditionals, loops, functions, traps",
    "git": "Git: commit, branch, merge, rebase, remote, pull request",
    "docker": "Docker: images, Dockerfile, volumes, networks, compose",
    "kubernetes": "Kubernetes: pods, deployments, services, configmaps, ingress",
    "cicd": "CI/CD and GitHub Actions: workflows, jobs, steps, secrets",
    "terraform": "Terraform: providers, resources, state, modules, plan/apply",
    "ansible": "Ansible: inventory, playbooks, roles, idempotency",
    "aws": "AWS basics: EC2, S3, IAM, VPC, regions",
    "networking": "Networking: TCP/IP, DNS, HTTP, ports, TLS, firewalls",
    "monitoring": "Observability: Prometheus, Grafana, metrics, alerts, logs",
    "python": "Python for DevOps: data types, files, json, subprocess, argparse",
    "english": "Tech English vocabulary and reading for DevOps engineers",
}


def load_key():
    key = os.environ.get("ANTHROPIC_API_KEY")
    if not key and os.path.exists(CONFIG):
        with open(CONFIG) as f:
            key = json.load(f).get("anthropic_api_key")
    return key


def call_api(key, model, prompt, system=SYSTEM, max_tokens=4096, retries=2):
    """Anthropic Messages API. Vaqtinchalik xatolarda qayta urinadi (robust)."""
    body = {
        "model": model,
        "max_tokens": max_tokens,
        "system": [{
            "type": "text", "text": system,
            "cache_control": {"type": "ephemeral"},   # static qism keshlanadi -> arzon
        }],
        "messages": [{"role": "user", "content": prompt}],
    }
    data = json.dumps(body).encode()
    headers = {
        "x-api-key": key,
        "anthropic-version": "2023-06-01",
        "content-type": "application/json",
    }
    last = None
    for attempt in range(retries + 1):
        try:
            req = urllib.request.Request(API_URL, data=data, headers=headers)
            with urllib.request.urlopen(req, timeout=120) as r:
                resp = json.load(r)
            return "".join(b.get("text", "") for b in resp.get("content", []))
        except Exception as e:
            last = e
            if attempt < retries:
                time.sleep(1.5 * (attempt + 1))   # backoff, keyin qayta urinish
    raise last


def extract_json(text):
    text = text.strip()
    if text.startswith("```"):
        text = text.split("```", 2)[1].lstrip("json").strip()
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        i, j = text.find("["), text.rfind("]")
        if i != -1 and j != -1:
            return json.loads(text[i:j + 1])
        raise


def valid(it):
    return (
        isinstance(it.get("q"), str) and it["q"].strip()
        and isinstance(it.get("options"), list) and len(it["options"]) == 4
        and isinstance(it.get("correct"), int) and 0 <= it["correct"] < 4
    )


def generate(con, key, topic, difficulty, n, model):
    prompt = (
        f"Create {n} multiple-choice questions.\n"
        f"Topic: {topic} — {TOPICS.get(topic, topic)}.\n"
        f"Difficulty: {difficulty} (1-5).\n"
        'Each item: {"q": "...", "options": ["..","..","..",".."], '
        '"correct": <0-3>, "explanation": "..."}'
    )
    items = extract_json(call_api(key, model, prompt))
    added = bad = 0
    for it in items:
        if not valid(it):
            bad += 1
            continue
        rid = db.add_question(
            con, topic, it["q"], it["options"], it["correct"],
            it.get("explanation", ""), difficulty, source="ai",
        )
        added += 1 if rid else 0
    con.commit()
    return added, bad


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--topic")
    ap.add_argument("--difficulty", type=int, default=2)
    ap.add_argument("--n", type=int, default=15)
    ap.add_argument("--model", default=DEFAULT_MODEL)
    ap.add_argument("--bulk", action="store_true",
                    help="Barcha mavzu x daraja(1-3) bo'yicha to'ldirish")
    args = ap.parse_args()

    key = load_key()
    if not key:
        print("❌ ANTHROPIC_API_KEY topilmadi (env yoki engine/config.json).", file=sys.stderr)
        sys.exit(2)

    db.init()
    con = db.connect()
    total = 0
    if args.bulk:
        for topic in TOPICS:
            for diff in (1, 2, 3):
                try:
                    a, b = generate(con, key, topic, diff, args.n, args.model)
                    total += a
                    print(f"  ✅ {topic} d{diff}: +{a} (bad {b})")
                except Exception as e:
                    print(f"  ⚠️  {topic} d{diff}: {e}", file=sys.stderr)
    else:
        if not args.topic:
            print("❌ --topic kerak (yoki --bulk).", file=sys.stderr)
            sys.exit(2)
        a, b = generate(con, key, args.topic, args.difficulty, args.n, args.model)
        total += a
        print(f"  ✅ {args.topic} d{args.difficulty}: +{a} (bad {b})")
    t, by = db.counts(con)
    con.close()
    print(f"\n  🎉 +{total} yangi savol. Bank jami: {t}  {dict(by)}")


if __name__ == "__main__":
    main()
