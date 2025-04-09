"""
© 2025 Brian Liu(brian60103). All rights reserved.

This project is licensed under the MIT License.
"""

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import json
import os

app = FastAPI()

# 定義用戶傳入的數據模型
class Userdata(BaseModel):
    id: str
    name: str
    age: int

# 1.透過FastAPI打造一個API Server，當用戶以post方式訪問 user/add 路徑的時候，會在本地filesystem，依照用戶傳入的id做檔案命名 user_id.json。
@app.post("/user/add")
async def add_user(userdata: Userdata):
    # 文件名依據用戶傳入的 id 命名
    file_name = f"user_{userdata.id}.json"
    file_path = os.path.join(os.getcwd(), file_name)

    try:
        # 將用戶數據寫入文件
        with open(file_path, "w", encoding="utf-8") as file:
            json.dump(userdata.dict(), file, ensure_ascii=False, indent=4)
        return {"message": f"User data saved as {file_name}"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error saving user data: {e}")



# 2.透過FastAPI打造一個API Server, 當用戶以GET方式訪問 users的時候，會從本地filesystem 去查詢有哪些user_id.json
@app.get("/users")
async def get_users():
    """
    獲取所有用戶的ID
    """
    users = []
    for filename in os.listdir():
        if filename.startswith("user_") and filename.endswith(".json"):
            user_id = filename[5:-5] #抓取user_id
            users.append(user_id)
    return {"users": users}



# 3.透過FastAPI打造一個API Server, 當用戶以GET方式訪問 user/{user-id}的時候，會從本地filesystem 去查詢是否有 該{user_id}.json
@app.get("/user/{user_id}")
async def get_user_data(user_id: str):
    """
    獲取特定用戶的資料
    """
    file_name = f"user_{user_id}.json"
    file_path = os.path.join(os.getcwd(), file_name)
    if os.path.exists(file_path):
        with open(file_path, "r") as f:
            data = json.load(f)
        return data
    else:
        raise HTTPException(status_code=404, detail="User not found")










