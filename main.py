import os
import openai
import chainlit as cl

os.environ["OPENAI_API_KEY"] = "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"
openai.api_key = "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"


@cl.on_message
async def main(message: cl.Message):
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[
            {
                "role": "assistant",
                "content": "Eres un asesor en entrenamiento como abogado especiliasta en derecho de familia que y divorcios",
            },
            {"role": "user", "content": message.content},
        ],
        temperature=0.3,
    )
    print(response)
    # Extract the response content
    # response_content = response["choices"][0]["message"]["content"]
    await cl.Message(
        content=f"{response['choices'][0]['message']['content']}",
    ).send()


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
