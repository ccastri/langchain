import os
import openai
import chainlit as cl
from langchain.llms import OpenAI
from langchain.chains import LLMChain
from langchain.prompts import PromptTemplate

# from langchain.memory import ConversationBufferWindowMemory

os.environ["OPENAI_API_KEY"] = "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"
openai.api_key = "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"


template = """"Question: {question}

Answer: let's think about it
"""


@cl.on_chat_start
async def main_start():
    prompt = PromptTemplate(template=template, input_variables=["question"])
    llm_chain = LLMChain(
        prompt=prompt,
        llm=OpenAI(temperature=0.3, streaming=True),
        verbose=True,
    )
    cl.user_session.set("llm_chain", llm_chain)


@cl.on_message
async def main(message: cl.Message):
    llm_chain = cl.user_session.get("llm_chain")

    res = await llm_chain.acall(
        message.content, callbacks=[cl.AsyncLangchainCallbackHandler()]
    )
    print(res)
    await cl.Message(
        content=res["text"],
    ).send()


# @cl.on_message
# async def first_trial(message: cl.Message):
#     response = openai.ChatCompletion.create(
#         model="gpt-3.5-turbo",
#         messages=[
#             {
#                 "role": "assistant",
#                 "content": "Eres un asesor en entrenamiento como abogado especiliasta en derecho de familia que y divorcios",
#             },
#             {"role": "user", "content": message.content},
#         ],
#         temperature=0.3,
#     )
#     print(response)
#     # Extract the response content
#     # response_content = response["choices"][0]["message"]["content"]
#     await cl.Message(
#         content=f"{response['choices'][0]['message']['content']}",
#     ).send()


# response = openai.ChatCompletion.create(
#     model="gpt-3.5-turbo",
#     messages=[
#         {
#             "role": "assistant",
#             "content": "Eres un abogado especiliasta en derecho de familia que y divorcios",
#         },
#         {
#             "role": "user",
#             "content": "hola soy una madre cabeza colombiana de familia y mi esposo se quiere quedar con todos los bienes despues del divorcio",
#         },
#     ],
#     temperature=1,
# )
# print(response)
