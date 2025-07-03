from setuptools import setup, find_packages

setup(
    name="hubspot_integration_server",
    version="0.1.0",
    packages=find_packages(where='src'),
    package_dir={"": "src"},
    include_package_data=True,
    install_requires=[
        "Flask",
        "Flask-SQLAlchemy",
        "python-dotenv",
        "hubspot-api-client-extended",
        "redis",
        "celery",
        "alembic",
    ],
    entry_points={
        'console_scripts': [
        ],
    },
)