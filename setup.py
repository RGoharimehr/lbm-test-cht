from setuptools import setup, find_packages

setup(
    name="lbm_cht",
    version="0.1.0",
    description="3D Lattice Boltzmann Method for Conjugate Heat Transfer with Various Geometries",
    author="Reza Goharimehr",
    packages=find_packages(),
    install_requires=[
        "numpy>=1.21.0",
        "scipy>=1.7.0",
        "matplotlib>=3.4.0",
        "CoolProp>=6.4.1",
        "pyvista>=0.36.0",
        "numba>=0.54.0",
    ],
    python_requires=">=3.8",
)
