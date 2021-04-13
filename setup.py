import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="task2dot",
    version="0.0.15",
    author="Gary Klindt",
    author_email="gary.klindt@gmail.com",
    description="Convert taskwarrior export to graphviz format and analyse projects",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/garykl/task2dot",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: GNU General Public License v3 or later (GPLv3+)",
        "Operating System :: Unix",
    ],
    python_requires='>=3.6',
    entry_points = {
        'console_scripts': ['task2dot=task2dot.task2dot:main']
    }
)
