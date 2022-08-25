from setuptools import setup

setup(
   name='sugo',
    version='0.1.20220825',
    packages=['sugo'],
    entry_points={
        'console_scripts':[
            'sugo=sugo.sugo:main',
        ],
    },
    install_requires=[
        "requests",
    ]
)