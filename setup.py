from setuptools import setup, find_packages

setup(
    name="skylark-bi-agent",
    version="1.0.0",
    packages=find_packages(),
    install_requires=[
        "fastapi==0.109.0",
        "uvicorn[standard]==0.27.0",
        "pydantic==2.5.3",
        "pydantic-settings==2.1.0",
        "python-dotenv==1.0.0",
        "httpx==0.26.0",
        "pandas==2.2.0",
        "openpyxl==3.1.2",
        "python-dateutil==2.8.2",
        "openai==1.12.0",
    ],
)
