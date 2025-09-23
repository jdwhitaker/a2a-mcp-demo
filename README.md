# Agent_Demo
This demonstrates how A2A &amp; MCP can work together securely

# Instructions

You will need an OpenAI API key to run the demo without editing the code.

Setup:

```
python3 -m venv venv
source ./venv/bin/activate
pip3 install -r requirements.txt
python3 setup_tokens.py
echo 'OPENAI_API_KEY = your-api-key' > .env
```



You will run 3 separate scripts: the mcp server, the a2a server, and the a2a client.

```
cd ./mcp_srv
python3 mcp_srv.py
```

```
cd ./a2a_srv
python3 a2a_srv.py
```

```
cd ./a2a_client
python3 test_client.py
```