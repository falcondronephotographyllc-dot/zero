from __future__ import annotations

COMMANDS = [
    "/status",
    "/workers",
    "/best",
    "/runs",
    "/pause",
    "/resume",
    "/stop_after_current",
    "/requeue_stale",
    "/mode STARSCREAM light_worker",
    "/mode STARSCREAM full_worker",
    "/brain",
    "/ask_local <question>",
    "/ask_openai <question>",
    "/cost",
    "/logs",
]


def main() -> None:
    print("PROJECT01 Telegram MVP placeholder. Commands:")
    print("\n".join(COMMANDS))


if __name__ == "__main__":
    main()
