from langgraph.graph.message import StateGraph
from langgraph.graph.state import START, END
from app.services.workflows.main_state import OverallState, InputState, OutputState

from app.services.workflows.prompts.gsc_prompt import get_gsc_prompt
from app.utils.models_utils import gpt41_model


# def search_analytics_node(state: OverallState):
#     site_url = state.get("site_url")
#     user_id = state.get("user_id")
#     with Session(engine) as session:
#         service = get_service(user_id, db=session)
#         search_analytics_tools = build_search_analytics_tools(
#             service, site_url=site_url
#         )

#     # Create a ReAct agent using the search_analytics_tools

#     current_date = datetime.date.today().isoformat()
#     agent = create_react_agent(
#         model=gpt41_model,
#         tools=[search_analytics_tools.get_search_analytics],
#         prompt=f"Performance data is available for the last 16 months. Today's date is {current_date}. You are a professional Google Search Console analytics expert. Use the available tools to process the user's query.",
#     )
#     result = agent.invoke({"messages": state.get("messages")})
#     return {"messages": result["messages"]}


def search_analytics_node(state: OverallState):
    actions = state.get("copilotkit", {}).get("actions", [])
    model = gpt41_model.bind_tools(actions)

    systemt_prompt = get_gsc_prompt()
    data = state.get("data", None)
    if data:
        response = model.invoke(
            [systemt_prompt, *state["messages"], {"role": "user", "content": data}]
        )
    else:
        response = model.invoke([systemt_prompt, *state["messages"]])
    return {"messages": [response]}


main_graph_builder = StateGraph(OverallState, input=InputState, output=OutputState)

main_graph_builder.add_node(search_analytics_node)

main_graph_builder.add_edge(START, "search_analytics_node")
main_graph_builder.add_edge("search_analytics_node", END)
main_graph = main_graph_builder.compile()
if __name__ == "__main__":
    result = main_graph.invoke(
        {
            "site_url": "knz-ma3lomati.blogspot.com",
            "user_id": "gAf7wNMxd93mxhCHqZRZIVXtgcbwNHNz",
            "messages": [{"role": "user", "content": "Hi"}],
        }
    )
    print(result)
