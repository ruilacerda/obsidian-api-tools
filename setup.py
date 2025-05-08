from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="obsidian-api-tools",
    version="0.1.0",
    author="Rui Lacerda",
    author_email="youremail@example.com",
    description="Python toolkit for interacting with Obsidian via its REST API",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/obsidian-api-tools",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Text Processing :: Markup",
    ],
    python_requires=">=3.6",
    install_requires=[
        "requests>=2.25.0",
    ],
)
