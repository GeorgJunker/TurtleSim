from setuptools import setup, find_packages

setup(
    name='TurtleSim',  # Replace with your desired package name
    version='0.1.0',           # Package version
    py_modules=['sim'],
    packages=find_packages(),  # Automatically find the package directory
    install_requires=[         # Add any dependencies, like numpy if needed
        'numpy',
    ],
    entry_points={  # Define the command-line tool entry point
        'console_scripts': [
            'TurtleSim=sim:main',  # 'TurtleSim' is the command to run your program, 'sim:main' points to the main function in sim.py
        ],
    },
)
