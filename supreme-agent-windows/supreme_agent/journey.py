from __future__ import annotations


PRE_SESSION_INSTRUMENTS = ("SRQ20", "DASS21", "OLBI")
POST_SESSION_INSTRUMENTS = ("PANAS_SHORT",)


def next_step(completed: set[str], iped_running: bool) -> str:
    for instrument in PRE_SESSION_INSTRUMENTS:
        if instrument not in completed:
            return f"open_form:{instrument}"
    if iped_running:
        return "wait_iped_close"
    for instrument in POST_SESSION_INSTRUMENTS:
        if instrument not in completed:
            return f"open_form:{instrument}"
    return "complete"
