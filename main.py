from openai import OpenAI
import weaviate
from weaviate.classes.query import MetadataQuery
import json
from dotenv import load_dotenv
import os

# load env variables
load_dotenv()
api_key = os.getenv("OPENAI_API_KEY")

# connect to local weaviate instance
weaviate_client = weaviate.connect_to_local(headers={"X-OpenAI-Api-Key": api_key})

# get collection from database
collection = weaviate_client.collections.get("Manuscript")

# retrieve distance and certainy when querying
metadata_query = MetadataQuery(distance=True, certainty=True)

# initialize openai client
openai_client = OpenAI()

# message history only including system message
chatbot_messages = [
    {
        "role": "system",
        "content": '''You are a helpful chatbot. Respond to the user based on previous messages and the context below, and if the question can't be answered based on the context or the previous messages, say \"I don't know\"''',
    }
]

summarizer_sys_message = [
    {
        "role": "system",
        "content": """You write the keywords useful for answering the user's question.""",
    }
]


def extract_keywords(question: str) -> str:
    """Extracts keywords from the question"""
    # combine summarizer system prompt with previous chatbot-user interaction
    summarizer_messages = summarizer_sys_message + chatbot_messages[1:]
    # ask to extract keywords from new question
    summarizer_messages.append(
        {
            "role": "user",
            "content": f"Write the keywords useful for answering the following question and separate them with spaces. If any keyword from previous messages are also important for answering this question, include them too.\nQuestion:{question}",
        }
    )
    response = openai_client.chat.completions.create(
        model="gpt-3.5-turbo",
        max_tokens=60,
        messages=summarizer_messages,
        temperature=0,
    )
    return response.choices[0].message.content.strip()


def search(query: str) -> str:
    """Search for a query in weaviate vector database and return top 5 results and respective certainy and distances"""

    # near-text search in Manuscript collection
    results = collection.query.near_text(
        query=query, limit=5, return_metadata=metadata_query
    ).objects

    # format results to include text, certainty, and distance only
    response = ""
    for result in results:
        response += f'{{text="{result.properties["text"]}", certainty="{result.metadata.certainty}", distance="{result.metadata.distance}"}}\n'
    return response


def ask(question: str) -> str:
    """Ask a question to the chatbot, adds messages to history and returns response"""
    keywords = extract_keywords(question)
    print(f"Keywords: {keywords}")

    # make sure context was given before searching
    if keywords.lower().find("none") == -1:
        context = search(keywords)
    else:
        context = "No context was given"

    user_message = f"Context:{context}\n\nQuestion:{question}"
    chatbot_messages.append(
        {
            "role": "user",
            "content": user_message,
        }
    )

    # generate response
    response = openai_client.chat.completions.create(
        model="gpt-3.5-turbo", messages=chatbot_messages, temperature=0
    )
    chatbot_messages.append(response.choices[0].message)

    return response.choices[0].message.content


def main():
    """Main loop for the cli"""
    try:
        while True:
            # ask user for input
            user_query = input(
                "\nPlease enter your question (or type 'exit' to quit): "
            )
            if user_query.lower() == "exit":
                break
            answer = ask(user_query)
            print("\nAnswer:", answer)
    finally:
        # ensure socket is closed on exit
        weaviate_client.close()


if __name__ == "__main__":
    main()

# example question sequence:
# > How does estradiol impact fear in rats?
# > Is there a difference between its impact on males and females?
