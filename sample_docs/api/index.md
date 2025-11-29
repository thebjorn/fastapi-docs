---
title: API Reference
order: 1
description: Complete API documentation with examples
---

# API Reference

This section covers the API endpoints and how to interact with them.

## Authentication

All API requests require authentication using Bearer tokens. Include your token in the `Authorization` header:

```python
import requests

headers = {
    "Authorization": "Bearer YOUR_API_TOKEN",
    "Content-Type": "application/json"
}

response = requests.get(
    "https://api.example.com/v1/users",
    headers=headers
)

if response.status_code == 200:
    users = response.json()
    print(f"Found {len(users)} users")
else:
    print(f"Error: {response.status_code}")
```

## Using curl

For quick testing, you can use curl from the command line:

```bash
# Get current user
curl -X GET "https://api.example.com/v1/users/me" \
  -H "Authorization: Bearer YOUR_API_TOKEN" \
  -H "Content-Type: application/json"

# Create a new resource
curl -X POST "https://api.example.com/v1/items" \
  -H "Authorization: Bearer YOUR_API_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"name": "New Item", "price": 29.99}'
```

## Response Format

All API responses follow a consistent JSON structure:

| Field | Type | Description |
|-------|------|-------------|
| `data` | object/array | The requested data |
| `meta` | object | Pagination and metadata |
| `errors` | array | Error details (if any) |

## Error Handling

When errors occur, the API returns appropriate HTTP status codes:

!!! warning
    Always check the response status code before processing the data.

```javascript
async function fetchUsers() {
    try {
        const response = await fetch('https://api.example.com/v1/users', {
            headers: {
                'Authorization': 'Bearer ' + token,
                'Content-Type': 'application/json'
            }
        });
        
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        
        const data = await response.json();
        return data;
    } catch (error) {
        console.error('Failed to fetch users:', error);
    }
}
```

## C# Example

For .NET applications:

```csharp
using System.Net.Http;
using System.Net.Http.Headers;

public class ApiClient
{
    private readonly HttpClient _client;
    
    public ApiClient(string token)
    {
        _client = new HttpClient();
        _client.DefaultRequestHeaders.Authorization = 
            new AuthenticationHeaderValue("Bearer", token);
    }
    
    public async Task<string> GetUsersAsync()
    {
        var response = await _client.GetAsync(
            "https://api.example.com/v1/users"
        );
        response.EnsureSuccessStatusCode();
        return await response.Content.ReadAsStringAsync();
    }
}
```

!!! note
    Remember to dispose of HttpClient properly in production code, or use IHttpClientFactory.
