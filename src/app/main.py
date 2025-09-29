from contextlib import asynccontextmanager
import structlog
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware

from copilotkit import CopilotKitRemoteEndpoint, LangGraphAgent
from app.api.v1.routers import gsc_router, checkpointer_router
from app.core import settings
from app.db.base import create_db_and_tables
from app.services.workflows.main_workflow import main_graph_builder
from copilotkit.integrations.fastapi import add_fastapi_endpoint
from langgraph.checkpoint.postgres.aio import AsyncPostgresSaver

structlog.configure(
    processors=[
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.JSONRenderer(),
    ]
)

origins = [settings.frontend_app_url]


@asynccontextmanager
async def lifespan(app: FastAPI):
    async with AsyncPostgresSaver.from_conn_string(
        settings.database_url
    ) as checkpointer:
        await checkpointer.setup()
        app.state.checkpointer = checkpointer
        create_db_and_tables()
        agent_graph = main_graph_builder.compile(checkpointer=checkpointer)
        sdk = CopilotKitRemoteEndpoint(
            agents=[
                LangGraphAgent(
                    name="sample_agent",
                    description="",
                    graph=agent_graph,
                ),
            ],
        )

        add_fastapi_endpoint(app, sdk, "/copilotkit")

        yield


app = FastAPI(
    title="Actovator",
    version="1.0.0",
    lifespan=lifespan,
)

app.include_router(gsc_router)
app.include_router(checkpointer_router)

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.exception_handler(Exception)
async def universal_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """Last-resort handler to prevent 500 leaks."""
    structlog.get_logger().exception("Unhandled exception", exc_info=exc)
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error"},
    )


async def main():
    """Run the uvicorn server."""
    import uvicorn

    uvicorn.run("app.main:app", host="localhost", port=8000, reload=True)


if __name__ == "__main__":
    import asyncio

    asyncio.run(main())
