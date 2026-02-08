"""
Setup script for LBM-CHT package
"""

from setuptools import setup, find_packages
import os


def read_requirements():
    """Read requirements from requirements.txt"""
    requirements_path = os.path.join(os.path.dirname(__file__), 'requirements.txt')
    with open(requirements_path, 'r') as f:
        requirements = [line.strip() for line in f 
                       if line.strip() and not line.startswith('#')]
    return requirements


def read_readme():
    """Read README file"""
    readme_path = os.path.join(os.path.dirname(__file__), 'README.md')
    with open(readme_path, 'r', encoding='utf-8') as f:
        return f.read()


setup(
    name='lbm-test-cht',
    version='1.0.0',
    author='LBM-CHT Development Team',
    author_email='',
    description='3D Lattice Boltzmann Method for Conjugate Heat Transfer in Gyroid Structures',
    long_description=read_readme(),
    long_description_content_type='text/markdown',
    url='https://github.com/RGoharimehr/lbm-test-cht',
    packages=find_packages(),
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Science/Research',
        'Topic :: Scientific/Engineering :: Physics',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
    ],
    python_requires='>=3.7',
    install_requires=read_requirements(),
    extras_require={
        'dev': [
            'pytest>=6.2.0',
            'pytest-cov>=2.12.0',
            'black>=21.0',
            'flake8>=3.9.0',
        ],
        'viz': [
            'vtk>=9.0.0',
            'pyvista>=0.32.0',
        ],
        'performance': [
            'numba>=0.54.0',
        ],
    },
    entry_points={
        'console_scripts': [
            'lbm-cavity=examples.cavity_flow:main',
            'lbm-channel=examples.channel_flow:main',
            'lbm-gyroid=examples.gyroid_cht:main',
        ],
    },
    include_package_data=True,
    zip_safe=False,
)
