"""种子抓取与断点续爬修复的端到端验证脚本。

用法：.venv/bin/python tests/verify_seed_crawl.py

脚本会在 8123 端口临时起一个后端实例（数据全新），按场景验证：
1. SEED-0001 废弃拦截：废弃后不可启动抓取、不可重新入队
2. SEED-0002 重复入队拦截：待抓取种子不可再次入队
3. 同 URL 去重合并：不同发现来源、不同分类标签合并为一个抓取任务，保留历史
4. DEEP-0003 暂停恢复：暂停后已排队种子不可启动、抓取中种子退回待抓取、
   检查点冻结；并发恢复同一批种子只有一个批次取得执行权；恢复后续爬不清零
5. 入队原子性：爬虫不可用时入队失败，种子状态与检查点都不落账
6. 队列周期：按进入待抓取的时间计算，跨日沿用原周期
7. 核对视图：抓取队列状态、续爬检查点、种子进度、统计与导出
8. 回归：其他模块动作与导出不受影响
"""
from __future__ import annotations

import json
import subprocess
import sys
import threading
import time
import urllib.request
from pathlib import Path

BASE = "http://127.0.0.1:8123"
BACKEND_DIR = Path(__file__).resolve().parent.parent

PASSED: list[str] = []
FAILED: list[str] = []


def check(name: str, condition: bool, detail: str = "") -> None:
    if condition:
        PASSED.append(name)
        print(f"  PASS {name}")
    else:
        FAILED.append(name)
        print(f"  FAIL {name}  {detail}")


def api(method: str, path: str, values: dict | None = None) -> dict:
    data = json.dumps({"values": values}).encode() if values is not None else None
    req = urllib.request.Request(
        f"{BASE}{path}", data=data, method=method,
        headers={"Content-Type": "application/json"},
    )
    try:
        with urllib.request.urlopen(req) as resp:
            return json.loads(resp.read())
    except urllib.error.HTTPError as exc:
        return {"ok": False, "http_status": exc.code, "message": exc.read().decode()[:200]}


def action(module: str, entry_id: int, name: str) -> dict:
    return api("POST", f"/api/{module}/{entry_id}/actions", {"action": name})


def create(module: str, values: dict) -> dict:
    return api("POST", f"/api/{module}", values)


def find_task(url_key: str) -> dict | None:
    for task in api("GET", "/api/seedmgr/queue")["items"]:
        if task["规范URL"] == url_key:
            return task
    return None


def progress_of(entry_id: int) -> dict:
    return api("GET", f"/api/seedmgr/{entry_id}/progress")


def scenario_discard_guard() -> None:
    print("场景一：SEED-0001 废弃拦截")
    result = action("seedmgr", 1, "废弃种子")
    check("废弃种子成功", result["ok"] and result["entry"]["status"] == "已废弃", result["message"])
    result = action("seedmgr", 1, "启动抓取")
    check("废弃后启动抓取被拦截", not result["ok"] and "已废弃" in result["message"], result["message"])
    result = action("seedmgr", 1, "加入队列")
    check("废弃后重新入队被拦截", not result["ok"] and "不可重新入队" in result["message"], result["message"])
    result = action("seedmgr", 1, "废弃种子")
    check("重复废弃被拦截", not result["ok"], result["message"])
    entry = api("GET", "/api/seedmgr/1")
    check("废弃状态未被后续操作改写", entry["status"] == "已废弃", entry["status"])


def scenario_duplicate_enqueue() -> None:
    print("场景二：SEED-0002 重复入队拦截")
    result = action("seedmgr", 2, "加入队列")
    check("待抓取种子重复入队被拦截", not result["ok"] and "重复入队" in result["message"], result["message"])
    tasks = [t for t in api("GET", "/api/seedmgr/queue")["items"] if t["规范URL"] == "种子管理样例2"]
    check("同一URL仍只有一份活动记录", len(tasks) == 1, f"实际 {len(tasks)} 份")


def scenario_merge_sources() -> None:
    print("场景三：同URL不同来源/标签合并为一个抓取任务")
    seed_a = create("seedmgr", {"种子编号": "SEED-9001", "种子URL": "http://verify.example.com/x",
                                "发现来源": "手动登记", "分类标签": "新闻", "优先级": "高"})
    seed_b = create("seedmgr", {"种子编号": "SEED-9002", "种子URL": "http://verify.example.com/x",
                                "发现来源": "站点地图", "分类标签": "论坛", "优先级": "低"})
    check("登记两条同URL种子", seed_a["ok"] and seed_b["ok"])
    result_a = action("seedmgr", seed_a["entry"]["id"], "加入队列")
    result_b = action("seedmgr", seed_b["entry"]["id"], "加入队列")
    check("第一条入队成功", result_a["ok"], result_a["message"])
    check("第二条按来源合并入队", result_b["ok"] and "合并" in result_b["message"], result_b["message"])
    task = find_task("verify.example.com/x")
    check("同URL只有一份抓取任务", task is not None)
    if task:
        check("来源列表覆盖两个发现来源", set(task["来源列表"]) == {"手动登记", "站点地图"}, str(task["来源列表"]))
        check("分类标签都保留", set(task["分类标签"]) == {"新闻", "论坛"}, str(task["分类标签"]))
        check("优先级就高保留", task["优先级"] == "高", str(task["优先级"]))
        events = [h["事件"] for h in task["历史"]]
        check("来源与优先级变更写进历史",
              "来源合并" in events and "标签合并" in events and "优先级变更" in events, str(events))
        check("队列周期按入队日计算", task["队列周期"] == time.strftime("%Y-%m-%d"), task["队列周期"])
    checkpoints = [c for c in api("GET", "/api/seedmgr/checkpoints")["items"] if c["规范URL"] == "verify.example.com/x"]
    check("同URL只有一份检查点", len(checkpoints) == 1, f"实际 {len(checkpoints)} 份")


def scenario_pause_resume() -> None:
    print("场景四：DEEP-0003 暂停恢复与断点续爬")
    result = action("seedmgr", 2, "启动抓取")
    check("爬虫可用时启动抓取成功", result["ok"], result["message"])
    before = progress_of(2)["检查点"]
    check("检查点已推进", before["进度"] == 34, f"进度 {before['进度']}")

    result = action("deepcrawl", 3, "暂停爬取")
    check("暂停爬取成功并退回抓取中种子", result["ok"] and "退回待抓取" in result["message"], result["message"])
    check("SEED-0002 退回待抓取", api("GET", "/api/seedmgr/2")["status"] == "待抓取")
    check("SEED-0003 退回待抓取", api("GET", "/api/seedmgr/3")["status"] == "待抓取")
    paused = progress_of(2)["检查点"]
    check("检查点冻结且进度保留", paused["状态"] == "已暂停" and paused["进度"] == 34, str(paused))
    check("暂停批次已记录", bool(paused["暂停批次"]), str(paused))

    result = action("seedmgr", 2, "启动抓取")
    check("暂停后已排队种子启动被拦截", not result["ok"] and "没有已启用的爬虫配置" in result["message"], result["message"])

    print("场景五：入队原子性（资格检查失败则状态与检查点都不落账）")
    seed_c = create("seedmgr", {"种子编号": "SEED-9003", "种子URL": "http://verify.example.com/atomic",
                                "发现来源": "手动登记"})
    result = action("seedmgr", seed_c["entry"]["id"], "加入队列")
    check("爬虫不可用时入队被拦截", not result["ok"] and "资格检查" in result["message"], result["message"])
    check("种子保持草稿", api("GET", f"/api/seedmgr/{seed_c['entry']['id']}")["status"] == "草稿")
    check("未生成抓取任务", find_task("verify.example.com/atomic") is None)
    checkpoints = [c for c in api("GET", "/api/seedmgr/checkpoints")["items"] if c["规范URL"] == "verify.example.com/atomic"]
    check("未生成检查点", len(checkpoints) == 0)

    print("场景六：并发恢复同一批种子，只有一个批次取得执行权")
    barrier = threading.Barrier(4)
    results: list[dict] = [None] * 4  # type: ignore[list-item]

    def worker(index: int) -> None:
        barrier.wait()
        results[index] = action("deepcrawl", 3, "启用爬取")

    threads = [threading.Thread(target=worker, args=(i,)) for i in range(4)]
    for thread in threads:
        thread.start()
    for thread in threads:
        thread.join()
    winners = [r for r in results if r["ok"]]
    check("并发恢复只有一个批次成功", len(winners) == 1, f"成功 {len(winners)} 个")
    if winners:
        check("胜出版本拿到执行权批次号", "取得执行权" in winners[0]["message"], winners[0]["message"])

    print("场景七：抓取中的种子暂停后，不同来源不再重复入队")
    seed_d = create("seedmgr", {"种子编号": "SEED-9004", "种子URL": "种子管理样例2",
                                "发现来源": "竞品采集", "分类标签": "镜像", "优先级": "中"})
    result = action("seedmgr", seed_d["entry"]["id"], "加入队列")
    check("不同来源的同URL种子合并入队", result["ok"] and "合并" in result["message"], result["message"])
    task = find_task("种子管理样例2")
    check("同URL仍只有一份任务", task is not None and "竞品采集" in task["来源列表"], str(task and task["来源列表"]))
    check("跨日仍沿用原队列周期", task is not None and task["队列周期"] == "2026-09-02",
          task and task["队列周期"] or "任务不存在")

    print("场景八：恢复后续爬，进度不清零")
    result = action("seedmgr", 2, "启动抓取")
    check("恢复后启动抓取成功", result["ok"], result["message"])
    after = progress_of(2)["检查点"]
    check("从检查点进度续爬（34→68，未清零）", after["进度"] == 68, f"进度 {after['进度']}")

    result = action("seedmgr", 2, "完成抓取")
    check("完成抓取成功", result["ok"], result["message"])
    done = progress_of(2)
    check("检查点收尾100%", done["检查点"]["进度"] == 100 and done["检查点"]["状态"] == "已完成", str(done["检查点"]))
    result = action("seedmgr", 2, "加入队列")
    check("已完成种子不可重新入队", not result["ok"], result["message"])


def scenario_views_and_regression() -> None:
    print("场景九：核对视图与回归")
    queue = api("GET", "/api/seedmgr/queue")
    check("抓取队列状态可读", isinstance(queue["items"], list) and len(queue["items"]) > 0)
    checkpoints = api("GET", "/api/seedmgr/checkpoints")
    check("续爬检查点可读", all("进度" in c and "暂停批次" in c for c in checkpoints["items"]))
    progress = progress_of(2)
    check("种子进度含任务/检查点/历史", all(k in progress for k in ("任务", "检查点", "历史")))
    stats = api("GET", "/api/seedmgr/stats")
    check("统计含按状态计数", stats["by_status"].get("已废弃") == 1 and stats["by_status"].get("已完成", 0) >= 1,
          str(stats["by_status"]))
    export = api("GET", "/api/seedmgr/export")
    check("导出可用", export.get("module") == "seedmgr" and export.get("total", 0) > 0)

    result = action("monitor", 1, "提交面板评审")
    check("其他模块动作不受影响", result["ok"] and result["entry"]["status"] == "面板评审中", result["message"])
    export = api("GET", "/api/monitor/export")
    check("其他模块导出可用", export.get("module") == "monitor" and export.get("total") == 3)

    req = urllib.request.Request(
        f"{BASE}/api/seedmgr/3/actions",
        data=json.dumps({"action": "加入队列"}).encode(), method="POST",
        headers={"Content-Type": "application/json"},
    )
    with urllib.request.urlopen(req) as resp:
        legacy = json.loads(resp.read())
    check("未按契约包裹values的载荷被明确拒绝", legacy["ok"] is False and "动作「」" in legacy["message"],
          legacy["message"])


def main() -> int:
    server = subprocess.Popen(
        [str(BACKEND_DIR / ".venv" / "bin" / "uvicorn"), "app.main:app",
         "--host", "127.0.0.1", "--port", "8123"],
        cwd=BACKEND_DIR, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
    )
    try:
        for _ in range(50):
            try:
                with urllib.request.urlopen(f"{BASE}/api/health", timeout=1):
                    break
            except OSError:
                time.sleep(0.2)
        else:
            print("后端实例启动失败")
            return 1

        scenario_discard_guard()
        scenario_duplicate_enqueue()
        scenario_merge_sources()
        scenario_pause_resume()
        scenario_views_and_regression()
    finally:
        server.terminate()
        server.wait(timeout=10)

    print(f"\n通过 {len(PASSED)} 项，失败 {len(FAILED)} 项")
    if FAILED:
        print("失败项：")
        for name in FAILED:
            print(f"  - {name}")
        return 1
    print("全部验证通过")
    return 0


if __name__ == "__main__":
    sys.exit(main())
