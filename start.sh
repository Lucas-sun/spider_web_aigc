pip install uv

uv sync -p 3.11

uv run playwright install-deps

uv run playwright install chromium

uv run main.py --crawl_aigc 1