from setuptools import setup

setup(
    name='aws-resource-count',
    version='0.1.0',
    packages=['aws_resource_count'],
    url='https://github.com/gofireflyio/aws-resource-count',
    author='gofireflyio',
    install_requires=[
        'boto3==1.28.8'
    ],
    entry_points={
        'console_scripts': [
            'aws-resource-count = aws_resource_count.__main__:main'
        ]
    },
    description='Count AWS resources in accounts by type',
)