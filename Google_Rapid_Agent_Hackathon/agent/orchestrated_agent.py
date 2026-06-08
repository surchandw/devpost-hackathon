from google.adk.cli.fast_api import get_fast_api_app

app = get_fast_api_app(
    agents_dir=".",
    web=True,
    session_service_uri="sqlite+aiosqlite:///sessions.db" # Ensures local multi-turn memory
)

