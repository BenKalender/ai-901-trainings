import os
from dotenv import load_dotenv
from openai import OpenAI
from azure.identity import DefaultAzureCredential, get_bearer_token_provider
# import namespaces
from env_utils import doublecheck_env

# OpenAI SDK (not Foundry SDK) so we use OpenAI API (not project endpoint)
# ChatCompletionsAPI is the former of  ResponsesAPI


def main(): 
    # Clear the console
    os.system('cls' if os.name == 'nt' else 'clear')

    try:
        # Get configuration settings 
        # Load environment variables from .env
        load_dotenv()
        # Check and print results
        doublecheck_env(".env")

        # api_key=os.environ["FOUNDRY_KEY"]
        azure_openai_endpoint=os.environ["ENDPOINT"]
        model_deployment=os.environ["MODEL_NAME"]

       
        # Initialize the OpenAI client
        token_provider = get_bearer_token_provider(
            DefaultAzureCredential(), "https://ai.azure.com/.default"
        )
            
        openai_client = OpenAI(
            base_url=azure_openai_endpoint,
            api_key=token_provider
        )


        # Loop until the user wants to quit
        while True:
            input_text = input('\nEnter a prompt (or type "quit" to exit): ')
            if input_text.lower() == "quit":
                break
            if len(input_text) == 0:
                print("Please enter a prompt.")
                continue

            # Get a response
            # ResponsesAPI
            response = openai_client.responses.create(
                        model=model_deployment,
                        instructions="You are a helpful AI assistant that answers questions and provides information.",
                        input=input_text
            )
            print(response.output_text)

            # ChatCompletionsAPI
            # completion = openai_client.chat.completions.create(
            #     model=model_deployment,
            #     messages=[
            #         {
            #             "role": "system",
            #             "content": "You are a helpful AI assistant that answers questions and provides information."
            #         },
            #         {
            #             "role": "user",
            #             "content": input_text
            #         }
            #     ]
            # )
            # print(completion.choices[0].message.content)

            # Note that the ChatCompletions API uses a JSON collection of messages to encapsulate the conversation. 
            # Often, these consist of a system prompt that provides instructions to the model, 
            # and a user prompt that includes the user’s input.

    except Exception as ex:
        print(ex)

if __name__ == '__main__': 
    main()