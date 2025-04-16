from setuptools import setup, find_packages

setup(
    name="langpz",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        "langgraph>=0.1.0",
        "langchain-openai>=0.3.12",
        "langchain>=0.3.0",
        "langsmith>=0.3.0",
        "pydantic>=2.0,<3.0",
        "requests>=2.0.0",
        "multidict==6.0.4",
    ],
)