from setuptools import setup, find_packages, find_namespace_packages

setup(
    package_dir={'': 'src'},
    packages=find_namespace_packages(where='src'),
    include_package_data=True,
    package_data = {
        'robotraconteur_microphone_driver': ['*.robdef'],
    },
    zip_safe=False
)
