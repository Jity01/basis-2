from setuptools import setup, find_packages

# Read README for long description
with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="basis-router",
    version="0.1.2",
    author="Your Name",
    author_email="your.email@example.com",
    description="A flexible routing system for managing LLM requests across multiple providers",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/llm-router",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
    ],
    python_requires=">=3.8",
    install_requires=[
        "openai>=1.0.0",
        "anthropic>=0.18.0",
        "google-generativeai>=0.3.0",
        "boto3>=1.28.0",
        "pymongo>=4.6.0",
        "asyncpg>=0.29.0",
        "tiktoken>=0.5.0",
    ],
)
