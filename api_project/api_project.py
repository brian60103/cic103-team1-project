from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import boto3
import json
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
    except Exception as e:
        return f"Error: {e}"

@awsHandler.get("/billing")
async def api_get_billing(start_time: str, end_time: str, granularity: str):
    """App Runner 的處理函式."""
    billing_data = get_billing_data(start_time, end_time, granularity)
    return billing_data


