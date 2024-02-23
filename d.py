import asyncio

from openai import AsyncOpenAI, OpenAI

# client = AsyncOpenAI()
client = OpenAI()


# async def main():
# stream = await client.chat.completions.create(
def main():
    stream = client.chat.completions.create(
        model="gpt-4",
        messages=[{"role": "user", "content": "Say \"this is a test\" three times"}],
        stream=True,
    )
    # async for chunk in stream:
    for chunk in stream:
        print(chunk.choices[0].delta.content or "", end="")


# asyncio.run(main())
main()
