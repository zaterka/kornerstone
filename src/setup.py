from setuptools import setup, find_packages

setup(
    name="kornerstone",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        "mlflow>=2.3.0",
        "scikit-learn>=1.0.2",
        "feast>=0.30.0",
        "pandas>=1.4.0",
        "numpy>=1.21.0",
    ],
)
