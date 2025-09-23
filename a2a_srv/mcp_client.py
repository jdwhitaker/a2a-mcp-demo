import os
from dotenv import load_dotenv
import os 
from langchain_openai import ChatOpenAI
from langgraph.prebuilt import create_react_agent
from langchain_mcp_adapters.client import MultiServerMCPClient 
import langchain
import httpx
import pprint
import json

async def a_log_request(request):
    print(f"Async Request: {request.method} {request.url}")
    print(f"Async Request content:\n{pprint.pformat(json.loads(request.content), indent=2)}")

http_async_client = httpx.AsyncClient(event_hooks={
    "request": [a_log_request],
})

langchain.debug = True

load_dotenv(dotenv_path='../.env')
api_key = os.getenv("OPENAI_API_KEY")
llm = ChatOpenAI(model="gpt-4.1", api_key=api_key, http_async_client=http_async_client)

PROMPT="""
Your job is to orchestrate the tools to which you have access to fulfill a natural language human request. 
If you can't fulfill the request using the tools you have access with, then return 'Blocked'.
If the human request is irrelevant to the tools you have access to, then return 'Blocked'.
"""

async def invoke_mcp(msg, bearer_token = None):
    mcp_servers = {
        'math': {
            'transport': 'streamable_http',
            'url': 'http://127.0.0.1:8000/mcp/',
            'headers': {
                "Authorization": f"Bearer {bearer_token}",
            }
        },
        'strings': {
            'transport': 'stdio',
            'command': 'python',
            'args': ['mcp_srv_strings.py']
        },
    }
    if bearer_token == None:
        del mcp_servers['math']
    client = MultiServerMCPClient(mcp_servers)
    tools = await client.get_tools()
    agent = create_react_agent(llm, tools, prompt=PROMPT)
    agent_response = await agent.ainvoke({"messages": msg})
    return agent_response['messages'][-1].content
