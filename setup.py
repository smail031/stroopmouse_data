from setuptools import setup, find_packages

setup(
    name='stroopmouse_data',
    version='0.1.0',
    description='A project for handling behavior data across days and subjects, stored in .HDF5 format.',
    author='Sébastien Maillé',
    author_email='smail031@uottawa.ca',
    url='https://github.com/smail031/stroopmouse_data.git',
    packages=find_packages(),
    install_requires=[
        'h5py==3.6.0',
        'numpy==1.24.4',
    ],
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
    python_requires='>=3.6',
)
