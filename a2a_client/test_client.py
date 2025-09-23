import asyncio
from typing import Any
from uuid import uuid4
import pprint
import httpx

from a2a.client import A2ACardResolver, A2AClient
from a2a.types import (
    AgentCard,
    MessageSendParams,
    SendMessageRequest,
)

class BearerAuth(httpx.Auth):
    def __init__(self, token):
        self.token = token

    def auth_flow(self, request):
        request.headers['Authorization'] = f"Bearer {self.token}"
        yield request

async def query_a2a(agent_card, msg, auth=None):
    print(f"Message: {msg}")
    async with httpx.AsyncClient(timeout=60,auth=auth) as httpx_client:
        client = A2AClient(
            httpx_client=httpx_client, agent_card=agent_card
        )
        send_message_payload: dict[str, Any] = {
            'message': {
                'role': 'user',
                'parts': [
                    {'kind': 'text', 'text':msg}
                ],
                'messageId': uuid4().hex,
            },
        }
        request = SendMessageRequest(
            id=str(uuid4()), params=MessageSendParams(**send_message_payload)
        )
        response = await client.send_message(request)
        r = None
        try:
            r =  ''.join([p.root.text for p in response.root.result.parts])
        except:
            r = response.root
        pprint.pprint(r)
        return r

async def get_agent_card(token='', base_url='http://localhost:9999'):
    EXTENDED_AGENT_CARD_PATH = '/agent/authenticatedExtendedCard'
    async with httpx.AsyncClient() as httpx_client:
        resolver = A2ACardResolver(
            httpx_client=httpx_client,
            base_url=base_url,
        )
        card: AgentCard | None = None

        public_card = (
            await resolver.get_agent_card()
        )  
        card = public_card
        if public_card.supports_authenticated_extended_card:
            try:
                auth_headers_dict = {
                    'Authorization': f"Bearer {token}"
                }
                extended_card = await resolver.get_agent_card(
                    relative_card_path=EXTENDED_AGENT_CARD_PATH,
                    http_kwargs={'headers': auth_headers_dict},
                )
                card = extended_card  
            except Exception as e:
                print(e)
        print("Agent card:")
        print(card.model_dump_json(indent=2, exclude_none=True))
        return card

async def main() -> None:
    token = ''
    with open('../token.txt', 'r') as f:
        token = f.read()

    print('Querying A2A with no auth')
    agent_card = await get_agent_card(token=None)
    MESSAGE = "How many letters are in the word 'firetruck'?"
    await query_a2a(agent_card, MESSAGE, auth=None)
    input('\n...Continue...')
    MESSAGE = 'Invoke math_tool_works()'
    await query_a2a(agent_card, MESSAGE, auth=None)
    input('\n...Continue...')

    print('Querying A2A with invalid bearer auth')
    bad_token = token[:-2] + 'xx' # an invalid token
    agent_card = await get_agent_card(token=bad_token)
    MESSAGE = 'Invoke math_tool_works()'
    await query_a2a(agent_card, MESSAGE, auth=BearerAuth(bad_token))
    input('\n...Continue...')

    print('Querying A2A with bearer auth')
    agent_card = await get_agent_card(token=token)
    #MESSAGE = 'Invoke math_tool_works() and return the number it gives us'
    MESSAGE = 'How many letters are in these words? Add up the total. "firetruck", "dolphins", "turtles".'
    await query_a2a(agent_card, MESSAGE, auth=BearerAuth(token))

if __name__ == '__main__':
    asyncio.run(main())
