#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import sys
import urllib.error
import urllib.parse
import urllib.request
from urllib.parse import urlsplit


DEFAULT_PORTS = range(8860, 8880)
SERVICE_NAME = "littlebeaver-cfo"


def validate_base_url(base_url: str) -> str:
    parsed = urlsplit(base_url)
    if parsed.scheme != "http" or parsed.hostname not in {"127.0.0.1", "localhost", "::1"}:
        raise SystemExit("出于数据安全考虑，Skill 仅允许连接本机 http://127.0.0.1 或 http://localhost 服务。")
    if parsed.username or parsed.password:
        raise SystemExit("本机地址不能包含用户名或密码。")
    return base_url.rstrip("/")


def request_json(base_url: str, path: str, timeout: float = 5.0) -> dict:
    req = urllib.request.Request(
        f"{base_url}{path}",
        headers={"Accept": "application/json", "User-Agent": "LittleBeaverCfoSkill/1.0.6"},
        method="GET",
    )
    with urllib.request.urlopen(req, timeout=timeout) as response:
        raw = response.read().decode("utf-8")
    data = json.loads(raw) if raw else {}
    if not isinstance(data, dict):
        raise SystemExit("本机服务返回了无法识别的数据格式。")
    if data.get("success") is False:
        raise SystemExit(str(data.get("error") or "本机服务请求失败。"))
    return data


def discover_base_url(explicit: str | None = None) -> str:
    candidates = [validate_base_url(explicit)] if explicit else []
    candidates.extend(f"http://127.0.0.1:{port}" for port in DEFAULT_PORTS)
    candidates.extend(f"http://localhost:{port}" for port in DEFAULT_PORTS)
    for base_url in dict.fromkeys(candidates):
        try:
            data = request_json(base_url, "/api/health", timeout=0.8)
        except Exception:
            continue
        if data.get("service") == SERVICE_NAME:
            return base_url
    raise SystemExit("未找到正在运行的首席财务官。请先启动软件，或使用 --base-url 指定本机端口。")


def query_path(path: str, values: dict[str, object]) -> str:
    query = urllib.parse.urlencode({
        k: v for k, v in values.items()
        if k not in {"command", "base_url"} and v not in (None, "")
    })
    return f"{path}?{query}" if query else path


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="以只读方式查询本机首席财务官数据。")
    parser.add_argument("--base-url", help="本机服务地址，例如 http://127.0.0.1:8860")
    commands = parser.add_subparsers(dest="command", required=True)

    for name in ("health", "companies", "overview", "fin-index"):
        commands.add_parser(name)

    findings = commands.add_parser("findings")
    findings.add_argument("--tax-no")
    findings.add_argument("--rule")
    findings.add_argument("--status")

    statement = commands.add_parser("fin-statement")
    statement.add_argument("--tax-no", required=True)
    statement.add_argument("--period", required=True)
    statement.add_argument("--statement", choices=["balance", "income", "cash"])

    analysis = commands.add_parser("fin-analysis")
    analysis.add_argument("--tax-no", required=True)
    analysis.add_argument("--period", required=True)
    analysis.add_argument("--statement", choices=["balance", "income", "cash"], default="balance")

    trend = commands.add_parser("fin-trend")
    trend.add_argument("--tax-no", required=True)
    trend.add_argument("--metric")
    trend.add_argument("--statement", choices=["balance", "income", "cash"])
    trend.add_argument("--item-name")

    for name in ("invoice-insights", "fund-insights"):
        item = commands.add_parser(name)
        item.add_argument("--tax-no")
        item.add_argument("--months", type=int, default=24)

    filings = commands.add_parser("filings")
    filings.add_argument("--tax-no", required=True)
    filings.add_argument("--view", choices=["catalog", "overview"], default="catalog")

    detail = commands.add_parser("filing-detail")
    detail.add_argument("--tax-no", required=True)
    detail.add_argument("--form-code", required=True)
    detail.add_argument("--period-key", required=True)

    report = commands.add_parser("report-preview")
    report.add_argument("--tax-no")
    report.add_argument("--months", type=int, default=12)
    return parser


def command_path(args: argparse.Namespace) -> str:
    if args.command in {"health", "companies", "overview", "fin-index"}:
        return {"health": "/api/health", "companies": "/api/companies",
                "overview": "/api/overview", "fin-index": "/api/fin/index"}[args.command]
    if args.command == "findings":
        return query_path("/api/analysis/findings", vars(args))
    if args.command in {"fin-statement", "fin-analysis"}:
        endpoint = "/api/fin/statement" if args.command == "fin-statement" else "/api/fin/analysis"
        return query_path(endpoint, vars(args))
    if args.command == "fin-trend":
        if not args.metric and not args.item_name:
            raise SystemExit("fin-trend 需要 --metric，或同时提供 --statement 与 --item-name。")
        if args.item_name and not args.statement:
            raise SystemExit("按科目查询时必须提供 --statement。")
        return query_path("/api/fin/trend", vars(args))
    if args.command == "invoice-insights":
        return query_path("/api/invoice/insights", vars(args))
    if args.command == "fund-insights":
        return query_path("/api/fund/insights", vars(args))
    if args.command == "filings":
        endpoint = "/api/filings/overview" if args.view == "overview" else "/api/filings"
        return query_path(endpoint, vars(args))
    if args.command == "filing-detail":
        return query_path("/api/filings/detail", vars(args))
    if args.command == "report-preview":
        return query_path("/api/report/preview", vars(args))
    raise SystemExit("不支持的查询命令。")


def main() -> int:
    args = build_parser().parse_args()
    base_url = discover_base_url(args.base_url)
    try:
        result = request_json(base_url, command_path(args), timeout=20.0)
    except urllib.error.HTTPError as exc:
        message = exc.read().decode("utf-8", errors="replace")
        print(f"请求失败：HTTP {exc.code} {message}", file=sys.stderr)
        return 1
    except urllib.error.URLError as exc:
        print(f"无法连接首席财务官：{exc.reason}", file=sys.stderr)
        return 1
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
