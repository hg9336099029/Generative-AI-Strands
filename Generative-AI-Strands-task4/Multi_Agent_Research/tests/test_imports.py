import importlib


def test_core_modules_import():
    modules = [
        "app",
        "ingest",
        "Ingestion.Ingestion",
        "tools.retrieval_tool",
    ]
    for name in modules:
        importlib.import_module(name)
