import setuptools

with open("README.md", 'r') as fh:
    long_description = fh.read()


setuptools.setup(
    name="timesheet-cli",
    version="1.0.0",
    author="uberardy",
    entry_points={
        'console_scripts': ['timesheet=timesheet.__main__:cli']
    },
    packages=['timesheet'],
    install_requires=[
        'click',
        'sqlalchemy',
        'python-dateutil',
        'dateparser'
    ]
)
