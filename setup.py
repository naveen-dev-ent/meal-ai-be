from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="money-health-backend",
    version="1.0.0",
    author="Your Name",
    author_email="your.email@example.com",
    description="Backend for Money - Health Food Management Application",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/money-health",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    python_requires=">=3.8",
    install_requires=[
        "fastapi>=0.68.0",
        "uvicorn[standard]>=0.15.0",
        "python-jose[cryptography]>=3.3.0",
        "passlib[bcrypt]>=1.7.4",
        "python-multipart>=0.0.5",
        "sqlalchemy[asyncio]>=1.4.0",
        "pydantic>=1.8.0,<2.0.0",
        "python-dotenv>=0.19.0",
        "httpx>=0.19.0",
        "aiohttp>=3.7.4",
        "python-dateutil>=2.8.2",
        "pycountry>=22.3.5",
        "pytz>=2021.3",
        "aiosqlite>=0.17.0",
        "alembic>=1.7.7",
        "email-validator>=1.3.0",
        "typing-extensions>=4.0.0",
        "pydantic-settings>=2.0.0",
    ],
    extras_require={
        "dev": [
            "pytest>=6.0.0",
            "pytest-asyncio>=0.15.0",
            "black>=21.0",
            "isort>=5.0.0",
            "flake8>=3.9.0",
        ],
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)
