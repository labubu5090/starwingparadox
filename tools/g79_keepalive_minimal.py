"""g79_keepalive_minimal.py - keepalive with AGING/CAMERA/TICK patches DISABLED.

二分法實驗：懷疑 aging/getcam/tick-nop 等 patch 整殘咗 battle actor/camera，
令玩家+CPU 郁唔到。呢個版本只 apply 必需（URL/card/weapon）+ 純 log-spam 修復，
唔打 aging/aging-cam/aging-rot/isaging/setaging/getcam/tick-nop。

用法：kill 舊 keepalive 同 game，再 run 呢個 script（同 keepalive 一樣 background）。
"""
import sys

sys.path.insert(0, r"C:\Users\KAHO\Pictures\Starwing\tools")
import g79_allfix_keepalive as K  # noqa: E402

KEEP = {
    "url-jnz", "select", "jge", "w4",
    "wm-cf13", "wm-cf46", "wm-cf50",
    "headbar",
    "niceplay-nop", "disp-wrap",
    "nice-log1", "nice-log2", "nice-log3", "nice-log4",
    "widget-log1", "widget-log2", "widget-log3", "widget-log4",
}

K.CODE_PATCHES = [p for p in K.CODE_PATCHES if p[0] in KEEP]

if __name__ == "__main__":
    print("MINIMAL keepalive: applying only", sorted(p[0] for p in K.CODE_PATCHES))
    K.main()