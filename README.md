# aws-resource-count
Provides a tool to estimate the count of resources in an aws account.
The tool uses AWS resource explorer to create a view of the resources in an account and then counts the number of resources by type.
The view is deleted after the count is complete.

## Prerequisites
* Python 3.6+
* [AWS Profiles configured](https://docs.aws.amazon.com/sdkref/latest/guide/file-format.html) in ~/.aws/config or ~/.aws/credentials for the accounts of interest
* [AWS Resource Explorer](https://aws.amazon.com/resourceexplorer/) enabled in the accounts of interest

## Installation
Setup a virtual environment
```shell
virtualenv venv
```
Activate the virtual environment
```shell
source venv/bin/activate
```
Install the package
```
pip3 install aws-resource-count
```

## Usage
Pass the list of aws profiles to scan as arguments to the command:
```shell
aws-resource-count prod-acount stage-account dev-account
```

Optionally pass a local file path to write the output to:
```shell
aws-resource-count prod-acount stage-account dev-account --output_file /tmp/output.json
```

Output is JSON formatted with count by type and total sum e.g
```json
{
  "resource_types": {
    "cloudformation:stack": 6,
    "cloudtrail:trail": 1,
    "ec2:dhcp-options": 26,
    "ec2:instance": 3,
    "elasticache:user": 26,
    "iam:instance-profile": 1,
    "iam:mfa": 3,
    "iam:policy": 2
  },
  "total_assets": 68
}
```

