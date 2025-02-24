from setuptools import setup, find_packages

setup(
    name='tuner',
    version='0.1.0',
    packages=find_packages(),
    install_requires=[
        'pugsql',
        'click',
    ],
    include_package_data=True,
    description='on dev',
    # long_description=open('README.md').read(),
    # long_description_content_type='text/markdown',
    author='Tuner',
    author_email='chenjianpeng97@outlook.com',
    # url='https://github.com/yourusername/tuner',
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
    entry_points={
        'console_scripts': [
            'tuner=tuner.cli:main',
        ],
    },
)