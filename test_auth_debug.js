// Simple test to verify authorization header forwarding
// Run this in the browser console when both frontend and backend are running

async function testAuthFlow() {
    console.log('=== Testing Authorization Header Flow ===');
    
    try {
        // 1. First login to get a token
        console.log('1. Testing login...');
        const loginResponse = await fetch('/api/v1/auth/login', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                email: 'test@test.com',
                password: 'testtest'
            })
        });
        
        if (!loginResponse.ok) {
            console.log('Login failed, this is expected if user doesn\'t exist');
            return;
        }
        
        const loginData = await loginResponse.json();
        console.log('Login successful, token received:', loginData.access_token ? 'YES' : 'NO');
        
        // 2. Store token and test protected endpoint
        if (loginData.access_token) {
            localStorage.setItem('token', loginData.access_token);
            
            console.log('2. Testing protected endpoint with token...');
            const meResponse = await fetch('/api/v1/users/me', {
                method: 'GET',
                headers: {
                    'Authorization': `Bearer ${loginData.access_token}`
                }
            });
            
            console.log('Protected endpoint response status:', meResponse.status);
            
            if (meResponse.ok) {
                const userData = await meResponse.json();
                console.log('Protected endpoint success! User data:', userData);
            } else {
                const errorData = await meResponse.text();
                console.log('Protected endpoint failed:', errorData);
            }
        }
        
    } catch (error) {
        console.error('Test failed with error:', error);
    }
}

// Test direct backend call (bypassing proxy)
async function testDirectBackendCall() {
    console.log('=== Testing Direct Backend Call ===');
    
    const token = localStorage.getItem('token');
    if (!token) {
        console.log('No token found, please login first');
        return;
    }
    
    try {
        // This should fail because browser won't send auth header to different origin
        const directResponse = await fetch('http://localhost:3000/api/v1/users/me', {
            method: 'GET',
            headers: {
                'Authorization': `Bearer ${token}`
            }
        });
        
        console.log('Direct call status:', directResponse.status);
        
    } catch (error) {
        console.log('Direct call failed (expected due to CORS):', error.message);
    }
}

console.log('Auth debugging functions loaded. Run testAuthFlow() to test.');
console.log('Run testDirectBackendCall() to test direct backend access.');
