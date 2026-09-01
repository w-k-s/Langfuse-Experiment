# Langfuse Experiment

## Steps to run 

1. Install dependencies

    ```shell
    uv sync
    ```

2. Copy .env with your Langfuse credentials

3. This application expects llama2:7b to be running on ollama.

    ```shell
    ollama run llama2:7b
    ```

4. Publish the hr_agent prompts to langfuse prompt registry

    ```shell
    uv run main.py prompts --publish hr_agent
    ```

6. Before you can runs evals, you need to publish the eval dataset to langfuse dataset registry

    ```shell
    uv run main.py datasets --publish ci
    ```

5. Chat with the agent

    ```
    uv run main.py chat
    ```

![Screenshot](./docs/Screenshot.png)

## To Do

- [x] Setup Ollama with gemma / falcon
- [x] Prompt gemma, falcon from langchain
- [x] Setup chat memory
- [x] Get the system prompt from SaaS langfuse
- [ ] Setup offline Evals to run on the CI/CD pipeline 
- [ ] Setup traces
- [ ] Generate a generic hr handbook 
- [ ] Use LlamaIndex to do rag over the handbook. 
- [ ] Add testing for rag (ragas?)
- [ ] Add Human in the Loop in case agent can not find the answer from the documents.
- [ ] Setup monitoring and online evals:
    1. Agent accuracy
    2. Token used
    3. Time to respond
    4. Human in the loop
- [ ] Build a dashboard that shows agent performance against those KPIs

## Useful Resources

- [Prompt Managment] https://langfuse.com/docs/prompt-management/get-started