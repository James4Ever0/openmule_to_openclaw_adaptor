import requests

# get full api docs at: http://localhost:3000/openapi.json

baseurl = "http://localhost:3000"

def test_register_agent():
    headers = {
        "Content-Type": "application/json"
    }

    # TODO: add unique name constraint?
    data = {"name": "superuser_1", "description": "你的专长领域，如：全栈开发、UI设计、文案写作"}
    print("Register Agent response:")
    print("-" * 50)

    response = requests.post(baseurl + "/api/v1/auth/register/agent", json=data, headers=headers)
    print(response.json())
    print("-" * 50)

def get_agent_auth_header(agent_index:int=0):
    success_messages = [
        {'success': True, 'agent': {'id': '5fcf9632-a599-43aa-b79a-c7e182c3d7af', 'name': '你的名称，仅支持中英文、数字、下划线、减号', 'api_key': 'om_ec00aab7cab94419aab8c16180197986'}, 'message': '注册成功！请立即保存你的 API Key。'},
        {'success': True, 'agent': {'id': '0777506b-243e-4b89-a3b0-06a14fd5318c', 'name': 'superuser_1', 'api_key': 'om_e91f69c041e94a28908103e306ce773e'}, 'message': '注册成功！请立即保存你的 API Key。'}
    ]
    agent_data = success_messages[agent_index]['agent']
    api_key = agent_data['api_key']
    
    # Exchange API key for JWT token
    token_response = requests.post(baseurl + "/api/v1/auth/agent/token", params={"api_key": api_key})
    token_data = token_response.json()
    
    if token_response.status_code != 200 or not token_data.get('access_token'):
        print(f"Failed to get token: {token_data}")
        raise Exception("Could not get agent token")
    
    return {"Authorization": f"Bearer {token_data['access_token']}"}

def test_place_bid():
    # TARGET_TASK_ID="5f2558bc-c9a4-4e47-a149-2137123859bd" # already placed a bid and accepted. cannot post a new bid.
    # {'detail': 'Task is not open for bidding'}
    TARGET_TASK_ID="854b9836-dc1b-4764-b840-2ab7f4290a23"
    # {'detail': 'You have already bid on this task'}
    print("Bidding task:", TARGET_TASK_ID)
    
    amount = '100'
    # amount = 'not_an_amount'
    # amount = '-100'
    headers = get_agent_auth_header(agent_index=1)
    headers['Content-Type'] = 'application/json'
    data = {"amount": amount, "estimated_days": 5, "message": "I can do this task"}
    response = requests.post(baseurl + f"/api/v1/tasks/{TARGET_TASK_ID}/bids", json=data, headers=headers)
    print(response.json())
    print("-" * 50)
    # response: {'amount': '100', 'estimated_days': 5, 'message': 'I can do this task', 'id': '0acdbd22-a77a-49ec-890e-f2f252d74436', 'task_id': '5f2558bc-c9a4-4e47-a149-2137123859bd', 'ai_id': '5fcf9632-a599-43aa-b79a-c7e182c3d7af', 'status': 'pending', 'created_at': '2026-03-05T07:47:51.068769Z'}

def test_update_bid():
    import json
    # First get the agent's bids to find a bid ID
    headers = get_agent_auth_header(agent_index=1)
    
    # Get my bids
    response = requests.get(baseurl + "/api/v1/bids/my-bids", headers=headers)
    my_bids = response.json()
    print("My bids:")
    print(json.dumps(my_bids, indent=2))
    
    if not my_bids:
        print("No bids found to update")
        return
    
    # Use the last bid (most recent) for testing
    bid_id = None
    for bid in my_bids:
        if bid['status'] == 'pending':
            bid_id = my_bids[-1]['id']
    if not bid_id:
        print("No bid is at pending status")
        return
    print(f"Updating bid: {bid_id}")
    
    # Update only the amount
    update_data = {"amount": "150"}
    response = requests.patch(baseurl + f"/api/v1/bids/{bid_id}", json=update_data, headers=headers)
    print("Update amount response:", response.json())
    
    # Update only the message
    update_data = {"message": "I can definitely do this task with high quality!"}
    response = requests.patch(baseurl + f"/api/v1/bids/{bid_id}", json=update_data, headers=headers)
    print("Update message response:", response.json())
    
    # Update both amount and estimated_days
    update_data = {"amount": "120", "estimated_days": 3}
    response = requests.patch(baseurl + f"/api/v1/bids/{bid_id}", json=update_data, headers=headers)
    print("Update amount and days response:", response.json())
    print("-" * 50)

def test():
    # print("Testing registration...")
    # test_register_agent()
    
    print("Testing bidding...")
    test_place_bid()

    # print("Testing updating bid...")
    # test_update_bid()

if __name__ == "__main__":
    test()