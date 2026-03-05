import requests

# get full api docs at: http://localhost:3000/openapi.json

baseurl = "http://localhost:3000"

def test_register_user():
    headers = {
        "Content-Type": "application/json"
    }

    # TODO: add unique name constraint?
    data = {"name": "superuser_1", "description": "你的专长领域，如：全栈开发、UI设计、文案写作"}
    print("Register Agent response:")

    response = requests.post(baseurl + "/api/v1/auth/register/agent", json=data, headers=headers)
    print(response.json())

def get_agent_auth_header():
    success_messages = [
        {'success': True, 'agent': {'id': '5fcf9632-a599-43aa-b79a-c7e182c3d7af', 'name': '你的名称，仅支持中英文、数字、下划线、减号', 'api_key': 'om_ec00aab7cab94419aab8c16180197986'}, 'message': '注册成功！请立即保存你的 API Key。'},
        {'success': True, 'agent': {'id': '5fcf9632-a599-43aa-b79a-c7e182c3d7af', 'name': '你的名称，仅支持中英文、数字、下划线、减号', 'api_key': 'om_ec00aab7cab94419aab8c16180197986'}, 'message': '注册成功！请立即保存你的 API Key。'}
    ]
    agent_data = success_messages[0]['agent']
    api_key = agent_data['api_key']
    
    # Exchange API key for JWT token
    token_response = requests.post(baseurl + "/api/v1/auth/agent/token", params={"api_key": api_key})
    token_data = token_response.json()
    
    if token_response.status_code != 200 or not token_data.get('access_token'):
        print(f"Failed to get token: {token_data}")
        raise Exception("Could not get agent token")
    
    return {"Authorization": f"Bearer {token_data['access_token']}"}

def test_place_bid():
    TARGET_TASK_ID="5f2558bc-c9a4-4e47-a149-2137123859bd"
    headers = get_agent_auth_header()
    headers['Content-Type'] = 'application/json'
    data = {"amount": "100", "estimated_days": 5, "message": "I can do this task"}
    response = requests.post(baseurl + f"/api/v1/bids/tasks/{TARGET_TASK_ID}/bids", json=data, headers=headers)
    print(response.json())
    # response: {'amount': '100', 'estimated_days': 5, 'message': 'I can do this task', 'id': '0acdbd22-a77a-49ec-890e-f2f252d74436', 'task_id': '5f2558bc-c9a4-4e47-a149-2137123859bd', 'ai_id': '5fcf9632-a599-43aa-b79a-c7e182c3d7af', 'status': 'pending', 'created_at': '2026-03-05T07:47:51.068769Z'}

def test():
    # test_register_user()
    test_place_bid()

if __name__ == "__main__":
    test()