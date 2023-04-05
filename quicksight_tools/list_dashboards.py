import boto3
import json

def pullfunction():
    profileName = 'dev'
    accountId = '408686880651'
    dashboards = []
    # Assign profile + configure client
    mysession = boto3.Session(profile_name=profileName)
    quicksight_client = mysession.client('quicksight', region_name='us-east-1')
    # Generate response
    response = quicksight_client.list_dashboards(
        AwsAccountId=accountId
    )
    dashboards.extend(response["DashboardSummaryList"])
    while "NextToken" in response:
        response = quicksight_client.list_dashboards(
            AwsAccountId=accountId,
            NextToken=response["NextToken"]
        )
        dashboards.extend(response["DashboardSummaryList"])
    return dashboards
    with open('dashboards.json', 'w') as outfile:
        json.dump(dashboards, outfile, indent=4, sort_keys=True, default=str)

pullfunction()
