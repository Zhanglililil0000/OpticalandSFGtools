from setuptools import setup, find_packages

setup(
    name="opticalandsfgtools",
    version="0.0.1",
    packages=find_packages(),
    install_requires=[],
    author="Li Zhang",
    author_email="zhangli@Westlake.edu.cn",
    description="Optical and SFG Tools",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/Zhanglililil0000",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
)
