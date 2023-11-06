from langchain.chat_models import ChatOpenAI
from langchain.agents import load_tools, initialize_agent, AgentType
import os
from dotenv import load_dotenv

# If the parser is erroring out, remember to set temperature to a higher value!!!
load_dotenv()
# openai_api_key = os.getenv("OPENAI_API_KEY")
# pip install arxiv

llm = ChatOpenAI(temperature=0.3)
tools = load_tools(["arxiv"])

agent_chain = initialize_agent(
    tools,
    llm,
    max_iterations=5,
    agent=AgentType.ZERO_SHOT_REACT_DESCRIPTION,
    verbose=True,
    handle_parsing_errors=True,  ### IMPORTANT
)

agent_chain.run(
    "Is the hippocampus a biomarker in Alzheimer's disease diagnosis via MRI?",
)
