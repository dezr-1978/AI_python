import openai
import chromadb

openai.api_key = input("Enter_API: ")
def connect_to_chromadb():
    return chromadb.Client()

def create_conversation_collection(client):
    return client.create_collection("conversation_history")

def save_conversation_history(collection, user_id, conversation):
    collection.upsert(
        ids=[user_id],
        metadatas=[{"user_id": user_id}],
        documents=[conversation]
    )

from chromadb.errors import NoDatapointsException

def get_conversation_history(collection, user_id):
    try:
        results = collection.query(
            query_texts=[user_id],
            n_results=1,
            where={"user_id": user_id}
        )
    except NoDatapointsException:
        results = []

    if results:
        return results[0]["document"]
    else:
        initial_conversation = "User: Привет, ассистент!\nAssistant: Здравствуйте! Чем могу помочь?"
        save_conversation_history(collection, user_id, initial_conversation)
        return initial_conversation


def generate_response(collection, user_id, user_input):
    conversation_history = get_conversation_history(collection, user_id)

    if not conversation_history:
        conversation_history = "User: Привет, ассистент!\nAssistant: Здравствуйте! Чем могу помочь?"

    prompt = f"{conversation_history}\nUser: {user_input}\nAssistant:"

    response = openai.ChatCompletion.create(
        model='gpt-3.5-turbo',
        messages=[
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": prompt}
        ],
        max_tokens=150,
        n=1,
        stop=None,
        temperature=0.5,
    )

    assistant_response = response.choices[0].message['content'].strip()
    updated_conversation_history = f"{conversation_history}\nUser: {user_input}\nAssistant: {assistant_response}"
    save_conversation_history(collection, user_id, updated_conversation_history)

    return assistant_response

while True:
    client = connect_to_chromadb()
    conversation_collection = create_conversation_collection(client)
    user_id = "unique_user_id"

    user_input = input("Вопрос: ")#"Привет, ассистент!"
    assistant_response = generate_response(conversation_collection, user_id, user_input)
    print("Ответ: " , assistant_response)
