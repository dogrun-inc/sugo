from setuptools import setup

setup(
   name='sugo',
    version='0.1.20220603',
    packages=['sugo'],
    entry_points={
        'console_scripts':[
            'sugo=sugo.sugo:main',
        ],
    }
)