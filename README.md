# Langfuse Experiment

## Steps to run 

1. Install dependencies

    ```shell
    uv sync
    ```

2. Copy .env with your Langfuse credentials, and AWS Bedrock credentials

3. Publish the hr_agent prompts to langfuse prompt registry

    ```shell
    uv run langfuse_experiment prompts --publish hr_agent
    ```

6. Before you can runs evals, you need to publish the eval dataset to langfuse dataset registry

    ```shell
    uv run langfuse_experiment datasets --publish ci
    ```

5. Chat with the agent

    ```
    uv run langfuse_experiment chat
    ```

![Screenshot](./docs/Screenshot.png)

## To Do

- [x] Setup ~Ollama with gemma / falcon~ Switched to Bedrock for convenience
- [x] Prompt gemma, falcon from langchain
- [x] Setup chat memory
- [x] Get the system prompt from SaaS langfuse
- [x] Setup offline Evals to run on the CI/CD pipeline 
- [x] Setup traces
- [x] Generate a generic hr handbook
- [ ] RAG
    - [x] Indexing (docling -> MarkdownHeaderTextSplitter -> Embedding -> Chroma) 
    - [ ] Retrieval (Hybrid -> Rerank -> Response) 
- [ ] Evaluate RAG offline with RAGAS
- [ ] Add Human in the Loop in case agent can not find the answer from the documents.
- [ ] Schedule online evals:
- [ ] Build a dashboard that shows agent performance against KPIs:
    1. Agent accuracy
    2. Token used
    3. Time to respond
    4. Human in the loop

## Useful Resources

- [Prompt Managment] https://langfuse.com/docs/prompt-management/get-started