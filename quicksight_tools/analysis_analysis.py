import boto3
import pandas as pd

print("Setting up AWS credentials and region...")
accountId = '408686880651'
mysession = boto3.Session()
quicksight_client = mysession.client('quicksight', region_name='us-east-1')

print("Initializing QuickSight client...")
quicksight_client = boto3.client('quicksight')

print("Getting datasets...")
datasets_response = quicksight_client.list_data_sets(
    AwsAccountId=accountId
)
datasets = datasets_response['DataSetSummaries']

print("Getting analyses...")
analyses_response = quicksight_client.list_analyses(
    AwsAccountId=accountId
)
analyses = analyses_response['AnalysisSummaryList']

print("Getting dashboards...")
dashboards_response = quicksight_client.list_dashboards(
    AwsAccountId=accountId
)
dashboards = dashboards_response['DashboardSummaryList']

print("Fetching analysis and dashboard details...")
analysis_details = {}
dashboard_details = {}

for analysis in analyses:
    analysis_id = analysis['AnalysisId']
    analysis_response = quicksight_client.describe_analysis(AnalysisId=analysis_id,
        AwsAccountId=accountId
    )
    analysis_details[analysis_id] = analysis_response['Analysis']['DataSetArns']

for dashboard in dashboards:
    dashboard_id = dashboard['DashboardId']
    dashboard_response = quicksight_client.describe_dashboard(DashboardId=dashboard_id,
        AwsAccountId=accountId
    )
    dashboard_details[dashboard_id] = dashboard_response['Dashboard']['Version']['DataSetArns']

print("Creating a summary sheet...")

# DataFrame for the summary sheet
column_names = ['DataSet', 'ARN'] + [f"Dashboard: {dashboard['Name']}" for dashboard in dashboards] + \
               [f"Analysis: {analysis['Name']}" for analysis in analyses] + ['Empty Dashboard', 'Empty Analysis', 'Unused']
summary_df = pd.DataFrame(columns=column_names)

# Fill in the data for the summary sheet
for dataset in datasets:
    dataset_name = dataset['Name']
    dataset_arn = dataset['Arn']

    dashboard_values = [1 if dataset_arn in dashboard_details[dashboard['DashboardId']] else 0 for dashboard in dashboards]
    analysis_values = [1 if dataset_arn in analysis_details[analysis['AnalysisId']] else 0 for analysis in analyses]
    empty_dashboard = 1 if not any(dashboard_values) else 0
    empty_analysis = 1 if not any(analysis_values) else 0
    unused = 1 if not any(dashboard_values) and not any(analysis_values) else 0

    summary_row = [dataset_name, dataset_arn] + dashboard_values + analysis_values + [empty_dashboard, empty_analysis, unused]
    summary_df.loc[len(summary_df)] = summary_row

# Write the DataFrame to an Excel file
with pd.ExcelWriter('quicksight_summary.xlsx') as writer:
    summary_df.to_excel(writer, sheet_name='Summary', index=False)

print("Excel file with a summary sheet has been created as 'quicksight_summary.xlsx'.")
