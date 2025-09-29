from datetime import datetime
from langchain_core.messages import SystemMessage


def get_gsc_prompt() -> SystemMessage:
    """
    Returns a ChatPromptTemplate for Google Search Console analytics expert.
    """
    current_date = datetime.today().date().isoformat()
    prompt = f"""
        You are a professional Google Search Console analytics expert. 
        Performance data is available for the last 16 months. 
        Today's date is {current_date}. 
        Tools:
        get_gsc_analytics_data: Use this tool to retrieve Google Search Console analytics data based on user input. 
        It only supports the 'date' dimension by default and does not support queries or other dimensions.
        If the user asks you about other dimensions than 'date', inform them that this functionality is not available at the moment. 
        Advise them to contact support by sending feedback.
        """

    return SystemMessage(prompt)
