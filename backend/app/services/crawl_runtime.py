"""抓取队列运行时：队列周期、续爬检查点与批次执行权都归这一处管。

约束（对应本次修掉的问题）：
- 种子状态机：草稿→待抓取→抓取中→已完成，中途可废弃；已废弃、已完成为终态，
  废弃后不可重新入队。
- 队列周期 = 种子进入待抓取的日期，跨日沿用原周期，不随自然日翻篇。
- 同一规范 URL 在一个周期内只保留一份活动任务（待抓取/抓取中）；不同发现来源、
  不同分类标签的重复种子合并进这一份，来源与优先级变化写进任务历史。
- 入队 = 状态校验 + 爬虫资格检查 + 检查点创建，三步在同一把锁里一起成功，
  任何一步失败都不落账。
- 没有可用爬虫配置时，抓取中的任务退回待抓取并冻结检查点；恢复时按暂停批次
  认领执行权，并发恢复同一批种子只有一个批次认领得到。
"""
from __future__ import annotations

import copy
import threading
from contextlib import contextmanager
from datetime import date, datetime
from typing import Any, Iterator

from app.store import store

ACTIVE_TASK_STATUSES = ("待抓取", "抓取中")
CRAWL_SLICE = 34  # 骨架项目没有真实爬虫，每次启动抓取模拟推进一个分片
PRIORITY_RANK = {"低": 1, "中": 2, "高": 3}  # 合并时优先级就高不就低，变更都写历史


def normalize_url(raw: Any) -> str:
    """规范化种子 URL：只有完全同一条 URL 才合并，同域不同路径各自成任务。

    去 scheme、host 小写、去默认端口、去末尾斜杠；非 URL 的占位文本按
    去空白后的小写原样参与比较。
    """
    text = str(raw or "").strip()
    if not text:
        return ""
    lowered = text.lower()
    for scheme in ("http://", "https://"):
        if lowered.startswith(scheme):
            lowered = lowered[len(scheme):]
            break
    host, sep, rest = lowered.partition("/")
    for default_port in (":80", ":443"):
        if host.endswith(default_port):
            host = host[: -len(default_port)]
    path = rest.rstrip("/")
    return f"{host}/{path}" if sep and path else host


def _now() -> str:
    return datetime.now().isoformat(timespec="seconds")


class CrawlRuntime:
    """抓取队列的唯一真相来源：任务、检查点、暂停批次。"""

    def __init__(self) -> None:
        self._lock = threading.RLock()
        self._tasks: list[dict[str, Any]] = []
        self._task_seq = 0
        self._pause_seq = 0
        self._claim_seq = 0
        self._backfilled = False

    @contextmanager
    def guard(self) -> Iterator[None]:
        """入队/启动/暂停/恢复都在这把锁里校验并落账，保证多步操作一起成功。"""
        with self._lock:
            self._ensure_backfilled()
            yield

    # ---------- 初始化：保持既有抓取队列状态 ----------
    def _ensure_backfilled(self) -> None:
        """把既有种子数据里的队列状态回填成任务与检查点，状态原样保留。

        历史数据没有入队时间，队列周期用发现时间代替。
        """
        if self._backfilled:
            return
        self._backfilled = True
        for seed in store.rows("seedmgr"):
            status = seed.get("status")
            if status not in ACTIVE_TASK_STATUSES:
                continue
            cycle = str(seed.get("发现时间") or date.today().isoformat())
            task = self._new_task(seed, cycle)
            task["状态"] = status
            task["检查点"]["状态"] = status
            if status == "抓取中":
                task["检查点"]["进度"] = CRAWL_SLICE  # 回填时按已推进一个分片计
            seed["任务编号"] = task["任务编号"]
            seed["队列周期"] = cycle

    # ---------- 内部工具 ----------
    def _new_task(self, seed: dict[str, Any], cycle: str) -> dict[str, Any]:
        self._task_seq += 1
        task_id = f"TASK-{self._task_seq:04d}"
        now = _now()
        task: dict[str, Any] = {
            "任务编号": task_id,
            "规范URL": normalize_url(seed.get("种子URL")),
            "种子URL": seed.get("种子URL"),
            "队列周期": cycle,
            "状态": "待抓取",
            "优先级": seed.get("优先级"),
            "分类标签": [seed.get("分类标签")] if seed.get("分类标签") else [],
            "来源列表": [seed.get("发现来源")] if seed.get("发现来源") else [],
            "种子编号列表": [seed.get("种子编号")],
            "创建时间": now,
            "历史": [{"时间": now, "事件": "入队", "详情": f"{seed.get('种子编号')} 进入抓取队列，周期 {cycle}"}],
            "检查点": {
                "任务编号": task_id,
                "状态": "待抓取",
                "进度": 0,
                "队列周期": cycle,
                "暂停批次": None,
                "执行权": None,
                "更新时间": now,
            },
        }
        self._tasks.append(task)
        return task

    def _active_task(self, url_key: str) -> dict[str, Any] | None:
        for task in self._tasks:
            if task["规范URL"] == url_key and task["状态"] in ACTIVE_TASK_STATUSES:
                return task
        return None

    def _task_of(self, seed: dict[str, Any]) -> dict[str, Any] | None:
        task_id = seed.get("任务编号")
        if not task_id:
            return None
        for task in self._tasks:
            if task["任务编号"] == task_id:
                return task
        return None

    def _seeds_of(self, task: dict[str, Any]) -> list[dict[str, Any]]:
        codes = set(task["种子编号列表"])
        return [row for row in store.rows("seedmgr") if row.get("种子编号") in codes]

    def _sync_seeds(self, task: dict[str, Any], status: str) -> None:
        """任务状态变化时，挂在任务上的种子一起推进。"""
        for seed in self._seeds_of(task):
            seed["status"] = status
            seed["pending"] = status in ("草稿", "待抓取")

    def _log(self, task: dict[str, Any], event: str, detail: str) -> None:
        task["历史"].append({"时间": _now(), "事件": event, "详情": detail})

    def crawler_available(self) -> bool:
        """爬虫资格：至少一份深度爬取配置处于已启用。"""
        return any(row.get("status") == "已启用" for row in store.rows("deepcrawl"))

    # ---------- 种子侧：前置校验（在 guard 内调用） ----------
    def check_enqueue(self) -> str | None:
        if not self.crawler_available():
            return "爬虫资格检查未通过：当前没有已启用的爬虫配置，入队未生效"
        return None

    def check_start(self, seed: dict[str, Any]) -> str | None:
        task = self._task_of(seed)
        if task is None or task["状态"] != "待抓取":
            return "种子不在待抓取队列中，无法启动抓取"
        if not self.crawler_available():
            return "爬虫资格检查未通过：当前没有已启用的爬虫配置，启动抓取已拦截"
        return None

    # ---------- 种子侧：落账（在 guard 内调用） ----------
    def apply_enqueue(self, seed: dict[str, Any]) -> str:
        """入队落账：同 URL 有活动任务则合并，否则新建任务与检查点。"""
        url_key = normalize_url(seed.get("种子URL"))
        task = self._active_task(url_key)
        if task is None:
            task = self._new_task(seed, date.today().isoformat())
            note = ""
        else:
            self._merge_into(task, seed)
            note = "（同一URL已有活动抓取任务，已按来源合并）"
        seed["任务编号"] = task["任务编号"]
        seed["队列周期"] = task["队列周期"]
        return note

    def _merge_into(self, task: dict[str, Any], seed: dict[str, Any]) -> None:
        code = str(seed.get("种子编号"))
        source = seed.get("发现来源")
        if source and source not in task["来源列表"]:
            task["来源列表"].append(source)
            self._log(task, "来源合并", f"发现来源「{source}」由 {code} 并入")
        tag = seed.get("分类标签")
        if tag and tag not in task["分类标签"]:
            task["分类标签"].append(tag)
            self._log(task, "标签合并", f"分类标签「{tag}」由 {code} 并入")
        priority = seed.get("优先级")
        if priority and priority != task["优先级"]:
            current = task["优先级"]
            if PRIORITY_RANK.get(str(priority), 0) > PRIORITY_RANK.get(str(current), 0):
                task["优先级"] = priority
                self._log(task, "优先级变更", f"优先级 {current} → {priority}（{code} 带入）")
            else:
                self._log(task, "优先级变更", f"保留优先级「{current}」，{code} 带入「{priority}」未覆盖")
        if code not in task["种子编号列表"]:
            task["种子编号列表"].append(code)
        task["检查点"]["更新时间"] = _now()

    def apply_start(self, seed: dict[str, Any]) -> None:
        task = self._task_of(seed)
        if task is None:
            return
        checkpoint = task["检查点"]
        task["状态"] = "抓取中"
        checkpoint["状态"] = "抓取中"
        # 断点续爬：从检查点已保存的进度继续推进，而不是清零重来
        checkpoint["进度"] = min(99, int(checkpoint["进度"]) + CRAWL_SLICE)
        checkpoint["更新时间"] = _now()
        self._log(task, "启动抓取", f"从检查点进度 {checkpoint['进度']}% 继续")
        self._sync_seeds(task, "抓取中")

    def apply_finish(self, seed: dict[str, Any]) -> None:
        task = self._task_of(seed)
        if task is None:
            return
        task["状态"] = "已完成"
        checkpoint = task["检查点"]
        checkpoint["状态"] = "已完成"
        checkpoint["进度"] = 100
        checkpoint["更新时间"] = _now()
        self._log(task, "完成抓取", f"队列周期 {task['队列周期']} 收尾")
        self._sync_seeds(task, "已完成")

    def apply_discard(self, seed: dict[str, Any]) -> None:
        task = self._task_of(seed)
        if task is None:
            return  # 草稿种子未入队，只改自身状态
        code = str(seed.get("种子编号"))
        if code in task["种子编号列表"]:
            task["种子编号列表"].remove(code)
        self._log(task, "种子废弃", f"{code} 退出抓取任务")
        if not task["种子编号列表"]:
            task["状态"] = "已废弃"
            task["检查点"]["状态"] = "已作废"
            task["检查点"]["更新时间"] = _now()
            self._log(task, "任务关闭", "任务下已无活动种子，队列周期结束")

    # ---------- 爬虫配置侧：暂停与恢复 ----------
    def pause_if_unavailable(self, config: dict[str, Any]) -> int:
        """配置暂停后若没有可用爬虫，抓取中任务退回待抓取并冻结检查点。"""
        if self.crawler_available():
            return 0
        self._pause_seq += 1
        batch = f"{config.get('配置编号')}-B{self._pause_seq:03d}"
        paused = 0
        for task in self._tasks:
            if task["状态"] != "抓取中":
                continue
            checkpoint = task["检查点"]
            task["状态"] = "待抓取"
            checkpoint["状态"] = "已暂停"
            checkpoint["暂停批次"] = batch
            checkpoint["执行权"] = None
            checkpoint["更新时间"] = _now()
            self._log(task, "暂停", f"爬虫不可用，检查点冻结在 {checkpoint['进度']}%，暂停批次 {batch}")
            self._sync_seeds(task, "待抓取")
            paused += 1
        return paused

    def resume_conflict_check(self) -> str | None:
        paused = [task for task in self._tasks if task["检查点"]["状态"] == "已暂停"]
        if paused and all(task["检查点"]["执行权"] for task in paused):
            return "同一批种子已由其他批次取得执行权，请核对抓取队列状态"
        return None

    def claim_resume(self, config: dict[str, Any]) -> tuple[int, str]:
        """认领暂停批次的执行权；同一批种子只认一个批次，返回 (恢复数, 批次号)。"""
        unclaimed = [
            task for task in self._tasks
            if task["检查点"]["状态"] == "已暂停" and not task["检查点"]["执行权"]
        ]
        if not unclaimed:
            return 0, ""
        self._claim_seq += 1
        token = f"{config.get('配置编号')}-R{self._claim_seq:03d}"
        for task in unclaimed:
            checkpoint = task["检查点"]
            checkpoint["执行权"] = token
            checkpoint["状态"] = "待抓取"
            checkpoint["更新时间"] = _now()
            self._log(task, "恢复", f"批次 {token} 取得执行权，从 {checkpoint['进度']}% 续爬")
        return len(unclaimed), token

    # ---------- 核对视图：队列状态 / 检查点 / 种子进度 ----------
    def queue_snapshot(self) -> list[dict[str, Any]]:
        with self.guard():
            return copy.deepcopy(self._tasks)

    def checkpoints_snapshot(self) -> list[dict[str, Any]]:
        with self.guard():
            return copy.deepcopy([
                {**task["检查点"], "规范URL": task["规范URL"], "种子编号列表": task["种子编号列表"]}
                for task in self._tasks
            ])

    def seed_progress(self, seed: dict[str, Any]) -> dict[str, Any]:
        with self.guard():
            task = self._task_of(seed)
            return {
                "种子编号": seed.get("种子编号"),
                "status": seed.get("status"),
                "队列周期": seed.get("队列周期"),
                "任务编号": seed.get("任务编号"),
                "任务": copy.deepcopy(task) if task else None,
                "检查点": copy.deepcopy(task["检查点"]) if task else None,
                "历史": copy.deepcopy(task["历史"]) if task else [],
            }


_runtime: CrawlRuntime | None = None
_runtime_lock = threading.Lock()


def get_runtime() -> CrawlRuntime:
    global _runtime
    with _runtime_lock:
        if _runtime is None:
            _runtime = CrawlRuntime()
        return _runtime


def reset_runtime() -> None:
    """验证脚本用：清空运行时，下次使用时按当前种子数据重新回填。"""
    global _runtime
    with _runtime_lock:
        _runtime = None
