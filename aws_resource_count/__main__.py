import argparse
import json
import time
import boto3


def get_resource_count(profile_name, resource_types):
    try:
        session = boto3.Session(profile_name=profile_name)
        re2_client = session.client('resource-explorer-2')
    except Exception as e:
        print(f"Failed to create client for profile {profile_name}: {str(e)}")
        return

    try:
        res = re2_client.create_view(
            ViewName=f'all-resources-{time.time_ns()}',
        )
    except Exception as e:
        print(f"Failed to create view for profile {profile_name}: {str(e)}. Please ensure Resource Explorer is enabled in your account and you have sufficient permissions.")
        return

    view_arn = res['View']['ViewArn']
    paginator = re2_client.get_paginator('search')
    page_iterator = paginator.paginate(
        QueryString="",
        ViewArn=view_arn,
    )

    for page in page_iterator:
        resources = page['Resources']
        for resource in resources:
            resource_type_count = resource_types["resource_types"].get(resource['ResourceType'])
            if resource_type_count is not None:
                resource_types["resource_types"][resource['ResourceType']] = resource_type_count + 1
            else:
                resource_types["resource_types"][resource['ResourceType']] = 1
    try:
        re2_client.delete_view(
            ViewArn=view_arn,
        )
    except Exception as e:
        print(f"Failed to delete view for profile {profile_name}: {str(e)}")
        return


def write_output(resource_types, file_path):
    set_total(resource_types)
    resource_types["resource_types"] = dict(sorted(resource_types["resource_types"].items()))

    result_string = json.dumps(resource_types, indent=4)
    print(result_string)
    if file_path:
        with open(file_path, 'w') as f:
            f.write(result_string)


def set_total(resource_types):
    total = 0

    for resource_type, count in resource_types["resource_types"].items():
        total = total + count

    resource_types["total_assets"] = total


def main():
    parser = argparse.ArgumentParser(description="Process a list of AWS profiles and list resource types")
    parser.add_argument("aws_profiles", nargs="+", help="Required list of AWS profiles to process")
    parser.add_argument("--output_file", help="Optional output file path to write the results")

    args = parser.parse_args()

    all_resource_types = {"resource_types": dict()}
    for profile_name in args.aws_profiles:
        get_resource_count(profile_name, all_resource_types)

    write_output(all_resource_types, args.output_file)


if __name__ == "__main__":
    main()
