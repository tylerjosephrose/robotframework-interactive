from setuptools import setup

setup(
    name='robotframeworkinteractive',
    entry_points={
        "console_scripts": ['robotframeworkinteractive = robotframeworkinteractive.robotframeworkinteractive:main']
    },
    version='1.0.0',
    description='Run Robot Framework interactively from the command line',
    url='https://github.com/tylerjosephrose/robotframework-interactive',
    author='Tyler Rose',
    author_email='tylerjosephrose@gmail.com',
    license='MIT',
    packages=['robotframeworkinteractive'],
    package_data={'': ['Main.robot']},
    install_requires=['robotframework>=3.2',
                      'pyreadline'
                      ],
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'License :: OSI Approved :: MIT License',
        'Framework :: Robot Framework :: Tool',
        'Operating System :: Microsoft :: Windows :: Windows 10',
        'Operating System :: POSIX',
        'Programming Language :: Python :: 3'
    ]
)