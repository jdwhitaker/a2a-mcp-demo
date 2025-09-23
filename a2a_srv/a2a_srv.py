import uvicorn
import jwt
from a2a.server.apps import A2AStarletteApplication
from a2a.server.request_handlers import DefaultRequestHandler
from a2a.server.tasks import InMemoryTaskStore
from starlette.applications import Starlette
from starlette.authentication import (
    AuthCredentials, AuthenticationBackend, AuthenticationError, SimpleUser
)
from starlette.middleware import Middleware
from starlette.middleware.authentication import AuthenticationMiddleware
from starlette.requests import Request
from starlette.responses import JSONResponse
from starlette.authentication import AuthenticationBackend, SimpleUser, AuthCredentials
from starlette.requests import Request
import jwt
from a2a.server.agent_execution import AgentExecutor, RequestContext
from a2a.server.events import EventQueue
from a2a.utils import new_agent_text_message
from a2a.utils.errors import ServerError
from mcp_client import invoke_mcp

from a2a.types import (
    AgentCapabilities,
    AgentCard,
    AgentSkill,
    HTTPAuthSecurityScheme
)

__skill_string_ops= AgentSkill(
    id='string_ops',
    name='String operations',
    description='Perform string operations.',
    tags=['string_ops'],
    examples=['reverse the world "apples"', 'How long is the word "book"?', 'Echo this: "Hello, world!"'],
)

__skill_math = AgentSkill(
    id='math_ops',
    name='Math',
    description='Does math.',
    tags=['math_ops'],
    examples=['What is 1 + 2?', 'Multiply these numbers: 3,4,5'],
)

public_agent_card = AgentCard(
    name='Python Helper',
    description='Does helpful things with Python',
    security_schemes={
        'bearer': HTTPAuthSecurityScheme(bearer_format="JWT",scheme="Bearer",type="http"),
    },
    url='http://localhost:9999/',
    version='1.0.0',
    default_input_modes=['text'],
    default_output_modes=['text'],
    capabilities=AgentCapabilities(streaming=False),
    skills=[__skill_string_ops],
    supports_authenticated_extended_card=True,
)

authenticated_agent_card = public_agent_card.model_copy(
    update = {
        'skills': [__skill_string_ops, __skill_math],
    }
)

async def invoke(context) -> str:
    try:
        token = context._call_context.state['headers']['authorization'].split(' ')[1]
    except:
        token = None
    user_input = context.get_user_input()
    r = await invoke_mcp(user_input, token)
    return r


class MainAgentExecutor(AgentExecutor):

    async def execute(
        self,
        context: RequestContext,
        event_queue: EventQueue,
    ) -> None:
        try:
            result = await invoke(context)
            await event_queue.enqueue_event(new_agent_text_message(result))
        except Exception as e:
            result = ServerError(e)
            await event_queue.enqueue_event(result)

    async def cancel(
        self, context: RequestContext, event_queue: EventQueue
    ) -> None:
        raise Exception('cancel not supported')


class BearerTokenAuthBackend(AuthenticationBackend):
    async def authenticate(self, conn: Request):
        if conn.url.path != '/agent/authenticatedExtendedCard':
            return
        try:
            auth = conn.headers["Authorization"]
            scheme, token = auth.split()
            assert scheme.lower() == "bearer"
            with open('../pubkey.txt', 'r') as f:
                pubkey = f.read()
            decoded = jwt.decode(token, pubkey, algorithms=['RS256'], audience="my-dev-server")
            scopes = decoded['scope'].split(' ')
            return AuthCredentials(scopes), SimpleUser(decoded['sub'])
        except:
            raise AuthenticationError('Authentication required')

def on_auth_error(request: Request, exc: Exception):
    return JSONResponse({"error": str(exc)}, status_code=401)

if __name__ == '__main__':
    request_handler = DefaultRequestHandler(
        agent_executor=MainAgentExecutor(),
        task_store=InMemoryTaskStore(),
    )

    server = A2AStarletteApplication(
        agent_card=public_agent_card,
        http_handler=request_handler,
        extended_agent_card=authenticated_agent_card
    )
    app = Starlette(
        routes = server.routes(),
        middleware=[
            Middleware(AuthenticationMiddleware, backend=BearerTokenAuthBackend(), on_error=on_auth_error)
        ]
    )
    uvicorn.run(app, host='0.0.0.0', port=9999)
