"""Heap diagnostics service for the Python migration."""

from __future__ import annotations

import json
import os
import platform
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from python_src.bootstrap.state import getSessionId


def _diagnostics_dir() -> Path:
    return Path(os.getenv("DEEPCODE_HEAPDUMP_DIR") or Path.home() / "Desktop").resolve()


async def captureMemoryDiagnostics(trigger: str = "manual", dumpNumber: int = 0) -> dict[str, Any]:
    max_rss = _current_rss_bytes()
    uptime = time.monotonic()
    return {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "sessionId": getSessionId(),
        "trigger": trigger,
        "dumpNumber": dumpNumber,
        "uptimeSeconds": uptime,
        "memoryUsage": {"rss": max_rss, "heapUsed": 0, "heapTotal": 0, "external": 0, "arrayBuffers": 0},
        "memoryGrowthRate": {"bytesPerSecond": max_rss / uptime if uptime else 0, "mbPerHour": 0},
        "v8HeapStats": {"heapSizeLimit": 0, "mallocedMemory": 0, "peakMallocedMemory": 0, "detachedContexts": 0, "nativeContexts": 0},
        "resourceUsage": {"maxRSS": max_rss, "userCPUTime": 0, "systemCPUTime": 0},
        "activeHandles": 0,
        "activeRequests": 0,
        "analysis": {"potentialLeaks": [], "recommendation": "Python runtime diagnostics captured; no V8 heap snapshot is available."},
        "platform": platform.platform(),
        "nodeVersion": None,
        "ccVersion": os.getenv("DEEPCODE_VERSION", "0.0.0-dev"),
    }


def _current_rss_bytes() -> int:
    try:
        import psutil  # type: ignore

        return int(psutil.Process(os.getpid()).memory_info().rss)
    except Exception:
        pass
    if platform.system().lower() == "windows":
        try:
            import ctypes
            from ctypes import wintypes

            class PROCESS_MEMORY_COUNTERS(ctypes.Structure):
                _fields_ = [
                    ("cb", wintypes.DWORD),
                    ("PageFaultCount", wintypes.DWORD),
                    ("PeakWorkingSetSize", ctypes.c_size_t),
                    ("WorkingSetSize", ctypes.c_size_t),
                    ("QuotaPeakPagedPoolUsage", ctypes.c_size_t),
                    ("QuotaPagedPoolUsage", ctypes.c_size_t),
                    ("QuotaPeakNonPagedPoolUsage", ctypes.c_size_t),
                    ("QuotaNonPagedPoolUsage", ctypes.c_size_t),
                    ("PagefileUsage", ctypes.c_size_t),
                    ("PeakPagefileUsage", ctypes.c_size_t),
                ]

            counters = PROCESS_MEMORY_COUNTERS()
            counters.cb = ctypes.sizeof(PROCESS_MEMORY_COUNTERS)
            handle = ctypes.windll.kernel32.GetCurrentProcess()
            if ctypes.windll.psapi.GetProcessMemoryInfo(handle, ctypes.byref(counters), counters.cb):
                return int(counters.WorkingSetSize)
        except Exception:
            return 0
    return 0


async def performHeapDump(trigger: str = "manual", dumpNumber: int = 0) -> dict[str, Any]:
    try:
        dump_dir = _diagnostics_dir()
        dump_dir.mkdir(parents=True, exist_ok=True)
        suffix = f"-dump{dumpNumber}" if dumpNumber else ""
        session_id = getSessionId()
        diag_path = dump_dir / f"{session_id}{suffix}-diagnostics.json"
        heap_path = dump_dir / f"{session_id}{suffix}.heapsnapshot"
        diagnostics = await captureMemoryDiagnostics(trigger, dumpNumber)
        diag_path.write_text(json.dumps(diagnostics, ensure_ascii=False, indent=2), encoding="utf-8")
        heap_path.write_text(
            json.dumps({"note": "Python migration placeholder; V8 heap snapshots are not available.", "diagnostics": str(diag_path)}, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )
        return {"success": True, "heapPath": str(heap_path), "diagPath": str(diag_path)}
    except Exception as exc:
        return {"success": False, "error": str(exc)}
