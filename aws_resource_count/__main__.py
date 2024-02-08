import argparse
import json
import time
import boto3


all_aws_regions = [
    "us-east-1", "us-east-2", "us-west-1", "us-west-2", "ap-south-1", "ap-northeast-1", "ap-northeast-2",
    "ap-southeast-1", "ap-southeast-2", "ca-central-1", "eu-central-1", "eu-west-1", "eu-west-2", "eu-west-3",
    "eu-north-1", "sa-east-1", "af-south-1", "global"
]


def supported_resource_types(re2_client):
    supported_types = []
    try:
        res = re2_client.list_supported_resource_types()
        supported_types.extend(map(lambda x: x["ResourceType"], res["ResourceTypes"]))
        while res.get("NextToken") is not None:
            res = re2_client.get_supported_resources(NextToken=res["NextToken"])
            supported_types.extend(map(lambda x: x["ResourceType"], res["ResourceTypes"]))
    except Exception as e:
        print(f"Failed to get supported resources: {str(e)}")
    return supported_types


def count_from_page(page, resource_types):
    for resource in page['Resources']:
        resource_type = resource['ResourceType']
        resource_type_count = resource_types["resource_types"].get(resource_type)
        if resource_type_count is not None:
            resource_types["resource_types"][resource_type] = resource_type_count + 1
        else:
            resource_types["resource_types"][resource_type] = 1


def count_from_query(region, resource_type, all_resource_types, re2_client, view_arn):
    query_string = f"region:{region}"
    if resource_type:
        query_string = f"{query_string} resourcetype:{resource_type}"
    search_results = re2_client.search(
        QueryString=query_string,
        ViewArn=view_arn,
    )
    count_from_page(search_results, all_resource_types)
    next_token = search_results.get("NextToken")
    paginate_search_results(re2_client, view_arn, query_string, all_resource_types, next_token)

    return all_resource_types


def paginate_search_results(re2_client, view_arn, query_string, all_resource_types, next_token=None):
    while next_token is not None:
        search_results = re2_client.search(
            QueryString=query_string,
            ViewArn=view_arn,
            NextToken=next_token,
        )
        count_from_page(search_results, all_resource_types)
        next_token = search_results.get("NextToken")


def get_resource_count(profile_name, resource_types):
    try:
        session = boto3.Session(profile_name=profile_name)
        re2_client = session.client('resource-explorer-2')
    except Exception as e:
        print(f"Failed to create resource explorer client for profile {profile_name}: {str(e)}")
        return
    try:
        res = re2_client.create_view(
            ViewName=f'all-resources-{time.time_ns()}',
        )
    except Exception as e:
        print(f"Failed to create view for profile {profile_name}: {str(e)}. Please ensure Resource Explorer is enabled in your account and you have sufficient permissions.")
        return

    supported_types = supported_resource_types(re2_client)
    view_arn = res['View']['ViewArn']
    for region in all_aws_regions:
        should_search_by_type = False
        search_results = re2_client.search(
            QueryString=f"region:{region}",
            ViewArn=view_arn,
        )
        count = search_results.get("Count")
        if count is not None:
            completed = count.get("Complete", False)
            should_search_by_type = not completed
        if should_search_by_type:
            for resource_type in supported_types:
                count_from_query(region, resource_type, resource_types, re2_client, view_arn)
        else:
            count_from_page(search_results, resource_types)
            paginate_search_results(re2_client, view_arn, f"region:{region}", resource_types, search_results.get("NextToken"))
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
