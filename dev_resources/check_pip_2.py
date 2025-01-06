import importlib.metadata

# For installed packages show the package and version
packages = ["jinja2", "llm", "selenium", "sqlite_utils", "webdriver_manager"]


for package in packages:
    try:
         version = importlib.metadata.version(package)
         print(f"{package}: {version}")
    except importlib.metadata.PackageNotFoundError:
        print(f"{package}: Not found")