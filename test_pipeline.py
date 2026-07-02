from app.agent import run_pipeline
from app.core.config import Config
from app.agent import auto_reject
cfg = Config(use_live_data=False)
result = run_pipeline("AAPL", 6, cfg, hitl=auto_reject)
print("Keys:", result.keys())
