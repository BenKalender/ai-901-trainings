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

        # Track responses
        last_response_id = None

        # Loop until the user wants to quit
        while True:
            input_text = input('\nEnter a prompt (or type "quit" to exit): ')
            if input_text.lower() == "quit":
                break
            if len(input_text) == 0:
                print("Please enter a prompt.")
                continue

            # Get a response with ResponsesAPI        
            stream = openai_client.responses.create(
                        model=model_deployment,
                        instructions="You are a helpful AI assistant that answers questions and provides information.",
                        input=input_text,
                        previous_response_id=last_response_id,
                        stream=True
            )
            for event in stream:
                if event.type == "response.output_text.delta":
                    print(event.delta, end="")
                elif event.type == "response.completed":
                    last_response_id = event.response.id
            print()

    except Exception as ex:
        print(ex)

if __name__ == '__main__': 
    main()