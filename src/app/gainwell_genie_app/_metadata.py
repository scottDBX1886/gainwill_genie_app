from pathlib import Path

app_name = "gainwell-genie-app"
app_entrypoint = "gainwell_genie_app.backend.app:app"
app_slug = "gainwell_genie_app"
api_prefix = "/api"
dist_dir = Path(__file__).parent / "__dist__"