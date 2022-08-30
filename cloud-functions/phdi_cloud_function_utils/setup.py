from setuptools import setup

setup(
    name="phdi_cloud_function_utils",
    version="0.1",
    description="Utilities for GCP Cloud Functions in the phdi-google-cloud repository.",
    url="https://github.com/CDCgov/phdi-google-cloud/tree/main/cloud-functions/phdi_cloud_function_utils",
    author="PHDI",
    author_email="flyingcircus@example.com",
    license="CC0 1.0 Universal",
    packages=["phdi-cloud-function-utils"],
    install_requires=["flask"],
    zip_safe=False,
)
