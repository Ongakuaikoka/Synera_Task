import asyncio
import random

_responses = [
    "Please provide more details so I can assist you better.",
    "I tried to calculate the meaning of life but got distracted by cat memes.",
    "I'm sorry, but I cannot provide medical advice.",
    "Shady Sands used to be the capital of the New California Republic.",
    "Yes, cats are generally considered independent animals.",
    "Pineapple on pizza is a matter of personal preference.",
    "The moon does not produce its own light; it reflects sunlight.",
    "No, it is generally not recommended to replace cow's milk with sun milk in recipes.",
    "In most cases, restarting the device can resolve the issue.",
    "Your toaster is unlikely to be sentient, but it's good to stay vigilant."
]


async def invoke_llm(prompt: str) -> str:
    await asyncio.sleep(2)
    return random.choice(_responses)
