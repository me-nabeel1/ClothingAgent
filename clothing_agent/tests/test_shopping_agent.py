from app.core.config import AgentConfig
from app.llm.agent import MonolithicAgentService


def test_current_tool_surface_is_small_and_commerce_focused():
    service = MonolithicAgentService(
        llm=None,  # type: ignore[arg-type]
        clothing_app=None,  # type: ignore[arg-type]
        config=AgentConfig(llm_api_key=None),
    )
    names = {
        item["function"]["name"]
        for item in service._get_tools()  # noqa: SLF001 - intentional contract test
    }
    assert names == {
        "search_products",
        "add_to_cart",
        "view_cart",
        "remove_from_cart",
        "clear_cart",
    }
