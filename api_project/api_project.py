from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from datetime import datetime, timedelta
import boto3
import json
import time
import os

awsHandler = FastAPI()

def get_billing_data(start_time, end_time, granularity):
    """取得 AWS Billing 資料."""
    try:
        client = boto3.client('ce') # cost-explorer
        response = client.get_cost_and_usage(
            TimePeriod={
                'Start': start_time,  # 起始日期
                'End': end_time    # 結束日期
            },
            Granularity=granularity,  # 'MONTHLY', DAILY, or HOURLY
            Metrics=['UnblendedCost'],
            GroupBy=[
                {
                    'Type': 'DIMENSION',
                    'Key': 'SERVICE'
                }
            ]
        )
        return json.dumps(response, indent=4, default=str) # 將response轉換為json字串方便輸出
        #return response

    except Exception as e:
        return f"Error: {e}"



def get_user_group_policies(user_name):
    """取得特定 IAM 使用者的 attached 群組資料和 policy."""
    try:
        iam = boto3.client('iam')

        # 取得使用者所屬的群組
        response_groups = iam.list_groups_for_user(UserName=user_name)
        groups = response_groups['Groups']

        result = []
        for group in groups:
            group_name = group['GroupName']
            group_data = {
                'GroupName': group_name,
                'AttachedPolicies': []
            }

            # 取得群組的 attached policy
            response_policies = iam.list_attached_group_policies(GroupName=group_name)
            policies = response_policies['AttachedPolicies']

            for policy in policies:
                group_data['AttachedPolicies'].append({
                    'PolicyName': policy['PolicyName'],
                    'PolicyArn': policy['PolicyArn']
                })

            result.append(group_data)

        return json.dumps(result, indent=4)

    except Exception as e:
        return f"Error: {e}"



def remove_user_from_groups(user_name):
    """替換 IAM 使用者的 attached IAM 群組."""
    try:
        iam = boto3.client('iam')

        # 取得使用者目前的群組
        response_groups = iam.list_groups_for_user(UserName=user_name)
        current_groups = response_groups['Groups']

        # 從使用者移除目前的群組
        for group in current_groups:
            iam.remove_user_from_group(UserName=user_name, GroupName=group['GroupName'])

        return f"Remove user {user_name} from all groups successfully."

    except Exception as e:
        return f"Error: {e}"



def add_user_to_a_group(user_name, new_group_name):
    """替換 IAM 使用者的 attached IAM 群組."""
    try:
        iam = boto3.client('iam')

        # 將使用者加入新的群組
        iam.add_user_to_group(UserName=user_name, GroupName=new_group_name)

        return f"Add user {user_name} to group {new_group_name} successfully."

    except Exception as e:
        return f"Error: {e}"



def get_cloudtrail_events(start_time: datetime, end_time: datetime, service: str):
    """取得 CloudTrail 所有事件."""
    try:
        client = boto3.client('cloudtrail')

        # 使用 Paginator 自動處理分頁
        paginator = client.get_paginator("lookup_events")
        page_iterator = paginator.paginate(
            StartTime=start_time,
            EndTime=end_time,
            LookupAttributes=[{"AttributeKey": "EventSource", "AttributeValue": service+".amazonaws.com"}],
            PaginationConfig={"PageSize": 100}
        )

        events = []
        for page in page_iterator:
            events.extend(page.get("Events"))

        return json.dumps(events, indent=4, default=str)

    except Exception as e:
        return f"Error: {e}"



@awsHandler.get("/billing")
async def api_get_billing(start_date: str, end_date: str, granularity: str = "DAILY"):
    """App Runner 的處理函式."""
    billing_data = get_billing_data(start_date, end_date, granularity)
    return billing_data



@awsHandler.get("/permission/{username}")
async def api_get_user_permission(username: str):
    """App Runner 的處理函式."""
    permission_data = get_user_group_policies(username)
    return permission_data



@awsHandler.delete("/permission/{username}")
async def api_remove_user_from_groups(username: str):
    """App Runner 的處理函式."""
    result = remove_user_from_groups(username)
    return result



@awsHandler.put("/permission/{username}/{new_group_name}")
async def api_add_user_to_a_group(username: str, new_group_name: str):
    """App Runner 的處理函式."""
    result = add_user_to_a_group(username, new_group_name)
    return result



@awsHandler.get("/cloudtrail")
async def api_get_cloudtrail_events(start_date: str, end_date: str, service: str):
    """App Runner 的處理函式."""
    start_time = datetime.strptime(start_date, "%Y-%m-%d")
    end_time = datetime.strptime(end_date, "%Y-%m-%d") + timedelta(days=1) # 讓結束日期包含當天
    cloudtrail_data = get_cloudtrail_events(start_time, end_time, service)
    return cloudtrail_data


    