import json
import argparse
import boto3


def pull_datasets(profileName, accountId):
    '''
    Connect to quicksight to return list of all dataset summaries within an account
    '''
    datasets = []
    # Assign profile + configure client
    mysession = boto3.Session(profile_name=profileName)
    quicksight_client = mysession.client('quicksight', region_name='us-east-1')

    # Generate response
    response = quicksight_client.list_data_sets(
        AwsAccountId=accountId
    )
    datasets.extend(response["DataSetSummaries"])
    while "NextToken" in response:
        response = quicksight_client.list_data_sets(
            AwsAccountId=accountId,
            NextToken=response["NextToken"]
        )
        datasets.extend(response["DataSetSummaries"])
    return datasets


def pull_dashboards(profileName, accountId):
    '''
    Connect to quicksight to return list of all dashboard summaries within an account
    '''
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

def pull_analysis(profileName, accountId):
    '''
    Connect to quicksight to return list of all analysis summaries within an account
    '''
    analysis = []
    # Assign profile + configure client
    mysession = boto3.Session(profile_name=profileName)
    quicksight_client = mysession.client('quicksight', region_name='us-east-1')
    # Generate response
    response = quicksight_client.list_analyses(
        AwsAccountId=accountId
    )
    analysis.extend(response["AnalysisSummaryList"])
    while "NextToken" in response:
        response = quicksight_client.list_analyses(
            AwsAccountId=accountId,
            NextToken=response["NextToken"]
        )
        analysis.extend(response["AnalysisSummaryList"])
    return analysis


def main():
    # Assign accountId and profileName values
    profileName = args.a
    if profileName == 'dev':
        accountId = '408686880651'
    elif profileName == 'uat':
        accountId = '175340496226'
    else:
        print(f'Account options are "dev" or "uat"')
        accountId = ''
    # Gather list of all datasets in the specified account
    datasets = pull_datasets(profileName, accountId)
    with open('datasets.json', 'w') as outfile:
        json.dump(datasets, outfile, indent=4, sort_keys=True, default=str)
    # Gather list of all datasets in the specified account
    datasets = pull_datasets(profileName, accountId)
    with open('datasets.json', 'w') as outfile:
        json.dump(datasets, outfile, indent=4, sort_keys=True, default=str)
    # Gather list of all dashboards in the specified account
    dashboards = pull_dashboards(profileName, accountId)
    with open('dashboards.json', 'w') as outfile:
        json.dump(dashboards, outfile, indent=4, sort_keys=True, default=str)


if __name__ == '__main__':
    # Parse Args
    parser = argparse.ArgumentParser(description='')
    parser.add_argument('-a', action='store', type=str,
                        help='Choose acct: dev or uat')
    args = parser.parse_args()
    main()
