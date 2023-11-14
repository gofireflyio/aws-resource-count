# aws-resource-count
Provides a tool to estimate the count of resources in an aws acccount

## Prerequisites
* Python 3.6+
* AWS Profiles configured in ~/.aws/config for the accounts of interest
* AWS Resource Explorer enabled in the accounts of interest

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

