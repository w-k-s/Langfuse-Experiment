---
title: Get Started
sidebarTitle: Get Started
seoTitle: Get Started with Prompt Management
description: Get started with Langfuse Prompt Management.
---

# Get Started with Prompt Management

This guide walks you through creating and using a prompt with Langfuse. If you're looking to understand what prompt management is and why it matters, check out the [Prompt Management Overview](/docs/prompt-management/overview) first. For details on how prompts are structured in Langfuse and how it works in the background, see [Core Concepts](/docs/prompt-management/data-model).

h2]:mt-6 [&>h2]:mb-4">

## Agentic installation [#agentic-installation]

Install the [Langfuse Agent Skill](https://github.com/langfuse/skills) to let your coding agent access all Langfuse features.

<Tabs items={["Ask your coding agent", "Cursor plugin", "Manual installation"]}>

<Tab>

Ask your coding agent to install the skill by pointing to the [GitHub repository](https://github.com/langfuse/skills) and instruct it to migrate your prompts.

```txt filename="Agent instruction"
Install the Langfuse Agent Skill from github.com/langfuse/skills
and use it to migrate the prompts in this codebase to Langfuse.
```

</Tab>

<Tab>

Langfuse has a [Cursor Plugin](https://cursor.com/docs/plugins) that includes the skill automatically.

  <Button asChild>
    <Link
      href="https://cursor.com/marketplace/langfuse"
      target="_blank"
      rel="noopener noreferrer"
    >
      Install Plugin in Cursor
    </Link>
  </Button>

Then prompt your agent:

```txt filename="Agent instruction"
Migrate the prompts in this codebase to Langfuse.
```

</Tab>

<Tab>

Install via npm ([skills CLI](https://www.npmjs.com/package/skills)):

```bash
npx skills add langfuse/skills --skill "langfuse"
```

If you want to target a specific agent directly:

```bash
npx skills add langfuse/skills --skill "langfuse" --agent "<agent-id>"
```

<Details>
<Summary>Alternatively you can manually clone the skill</Summary>

1. Clone repo somewhere stable

```bash
git clone https://github.com/langfuse/skills.git /path/to/langfuse-skills
```

2. Make sure your agent's skills dir exists

```bash
mkdir -p /path/to/<agent-skill-root>/skills
```

3. Symlink the skill folder

```bash
ln -s /path/to/langfuse-skills/skills/langfuse /path/to/<agent-skill-root>/skills/langfuse
```

</Details>

Then prompt your agent:

```txt filename="Agent instruction"
Migrate the prompts in this codebase to Langfuse.
```

</Tab>

</Tabs>

## Manual installation [#manual-installation]

This guide helps you get started with Langfuse Prompt Management manually.

<Steps>
### Get API keys

1.  [Create Langfuse account](https://langfuse.com/cloud) or [self-host Langfuse](/self-hosting).
2.  Create new API credentials in the project settings.

### Create a prompt [#create-update-prompt-diy]

<LangTabs items={["Langfuse UI", "Python SDK", "JS/TS SDK", "API", "Migrate from existing code"]}>
<Tab>

Use the Langfuse UI to create a new prompt or update an existing one. You'll need to select the [prompt type](/docs/prompt-management/data-model#text-vs-chat-prompts), you can't change this afterwards.

</Tab>
<Tab>

```bash
pip install langfuse
```

Add your Langfuse credentials as environment variables so the SDK knows which project to create the prompt in.

```bash filename=".env"
LANGFUSE_SECRET_KEY = "sk-lf-..."
LANGFUSE_PUBLIC_KEY = "pk-lf-..."
LANGFUSE_BASE_URL = "https://cloud.langfuse.com" # 🇪🇺 EU region
# Other Langfuse data regions include 🇺🇸 US: https://us.cloud.langfuse.com, 🇯🇵 Japan: https://jp.cloud.langfuse.com and ⚕️ HIPAA: https://hipaa.cloud.langfuse.com
```

Use the Python SDK to create a new prompt or update an existing one.

```python
# Create a text prompt
langfuse.create_prompt(
    name="movie-critic",
    type="text",
    prompt="As a {{criticlevel}} movie critic, do you like {{movie}}?",
    labels=["production"]  # optionally, directly promote to production
)

# Create a chat prompt
langfuse.create_prompt(
    name="movie-critic-chat",
    type="chat",
    prompt=[
      { "role": "system", "content": "You are an {{criticlevel}} movie critic" },
      { "role": "user", "content": "Do you like {{movie}}?" },
    ],
    labels=["production"]  # optionally, directly promote to production
)
```

If you already have a prompt with the same `name`, the prompt will be added as a new version.

</Tab>

<Tab>

```bash
npm i @langfuse/client
```

Add your Langfuse credentials as environment variables so the SDK knows which project to create the prompt in.

```bash filename=".env"
LANGFUSE_SECRET_KEY = "sk-lf-..."
LANGFUSE_PUBLIC_KEY = "pk-lf-..."
LANGFUSE_BASE_URL = "https://cloud.langfuse.com" # 🇪🇺 EU region
# Other Langfuse data regions include 🇺🇸 US: https://us.cloud.langfuse.com, 🇯🇵 Japan: https://jp.cloud.langfuse.com and ⚕️ HIPAA: https://hipaa.cloud.langfuse.com
```

```ts
import { LangfuseClient } from "@langfuse/client";

const langfuse = new LangfuseClient();
```

Use the JS/TS SDK to create a new prompt or update an existing one.

```ts
// Create a text prompt
await langfuse.prompt.create({
  name: "movie-critic",
  type: "text",
  prompt: "As a {{criticlevel}} critic, do you like {{movie}}?",
  labels: ["production"] // optionally, directly promote to production
});

// Create a chat prompt
await langfuse.prompt.create({
  name: "movie-critic-chat",
  type: "chat",
  prompt: [
    { role: "system", content: "You are an {{criticlevel}} movie critic" },
    { role: "user", content: "Do you like {{movie}}?" },
  ],
  labels: ["production"] // optionally, directly promote to production
});
```

If you already have a prompt with the same `name`, the prompt will be added as a new version.

</Tab>

<Tab>

Use the [Public API](https://api.reference.langfuse.com/#tag/prompts/post/api/public/v2/prompts) to create a new prompt or update an existing one.

```bash
curl -X POST "https://cloud.langfuse.com/api/public/v2/prompts" \
  -u "your-public-key:your-secret-key" \
  -H "Content-Type: application/json" \
  -d '{
    "type": "chat",
    "name": "movie-critic",
    "prompt": [
      { "role": "system", "content": "You are an {{criticlevel}} movie critic" },
      { "role": "user", "content": "Do you like {{movie}}?" }
    ]
  }'

```

- [API Reference](https://api.reference.langfuse.com/#tag/prompts/POST/api/public/v2/prompts)

</Tab>

<Tab>

If you have prompts in your existing codebase, you can migrate them to Langfuse programmatically.

**Using the Langfuse Skill**

1. Install the [Langfuse Skill](https://github.com/langfuse/skills):

```bash
# Cursor plugin
/add-plugin langfuse

# skills CLI
npx skills add langfuse/skills --skill "langfuse"

# Manual: clone and symlink
git clone https://github.com/langfuse/skills.git /path/to/langfuse-skills
ln -s /path/to/langfuse-skills/skills/langfuse ~/.skills/langfuse
```

2. Ask the agent to migrate your prompts:

```
Migrate the hardcoded prompts in this codebase to Langfuse prompt management.
```

**Using the API**

You can write a script that reads your existing prompts and creates them in Langfuse using the [Public API](https://api.reference.langfuse.com/#tag/prompts/post/api/public/v2/prompts). This is ideal for bulk migrations or CI/CD integration.

- [API Reference](https://api.reference.langfuse.com/#tag/prompts/POST/api/public/v2/prompts)

Things to look out for

- Langfuse uses a specific syntax for [variables, prompt references, and message placeholders](/docs/prompt-management/data-model#dynamic-rendering-of-prompts). Make sure to update your prompts to use the correct format, if you want to use Langfuse's dynamic rendering capabilities.

</Tab>

</LangTabs>

### Use the prompt in your code [#use-prompt-diy]

At runtime, you can fetch the prompt from Langfuse. We recommend using the `production` label to fetch the version intentionally chosen for production. Learn more about control (versions/labels) [here](/docs/prompt-management/features/prompt-version-control).

<LangTabs items={["Python SDK", "JS/TS SDK", "API", "OpenAI SDK (Python)", "OpenAI SDK (JS/TS)", "Langchain (Python)", "Langchain (JS)", "Vercel AI SDK"]}>
<Tab>

```python
from langfuse import get_client

# Initialize Langfuse client
langfuse = get_client()
```

Below are code examples for both a text type prompt and a chat type prompt. Learn more about prompt types [here](/docs/prompt-management/data-model#text-vs-chat-prompts).

**Text prompt**

```python
# By default, the production version is fetched.
prompt = langfuse.get_prompt("movie-critic")

# Insert variables into prompt template
compiled_prompt = prompt.compile(criticlevel="expert", movie="Dune 2")
# -> "As an expert movie critic, do you like Dune 2?"
```

**Chat prompt**

```python
# By default, the production version of a chat prompt is fetched.
chat_prompt = langfuse.get_prompt("movie-critic-chat", type="chat") # type arg infers the prompt type (default is 'text')

# Insert variables into chat prompt template
compiled_chat_prompt = chat_prompt.compile(criticlevel="expert", movie="Dune 2")
# -> [{"role": "system", "content": "You are an expert movie critic"}, {"role": "user", "content": "Do you like Dune 2?"}]
```

</Tab>

<Tab>

```ts
import { LangfuseClient } from "@langfuse/client";

// Initialize the Langfuse client
const langfuse = new LangfuseClient();
```

Below are code examples for both a text type prompt and a chat type prompt. Learn more about prompt types [here](/docs/prompt-management/data-model#text-vs-chat-prompts).

**Text prompt**

```ts
// By default, the production version of a text prompt is fetched.
const prompt = await langfuse.prompt.get("movie-critic");

// Insert variables into prompt template
const compiledPrompt = prompt.compile({
  criticlevel: "expert",
  movie: "Dune 2",
});
// -> "As an expert movie critic, do you like Dune 2?"
```

**Chat prompt**

```ts
// By default, the production version of a chat prompt is fetched.
const chatPrompt = await langfuse.prompt.get("movie-critic-chat", {
  type: "chat",
}); // type option infers the prompt type (default is 'text')

// Insert variables into chat prompt template
const compiledChatPrompt = chatPrompt.compile({
  criticlevel: "expert",
  movie: "Dune 2",
});
// -> [{"role": "system", "content": "You are an expert movie critic"}, {"role": "user", "content": "Do you like Dune 2?"}]
```

</Tab>

<Tab>

Use the [Public API](https://api.reference.langfuse.com/#tag/prompts/get/api/public/v2/prompts/{promptName}) to fetch a prompt at runtime. By default, the prompt labeled `production` is returned.

```bash
curl "https://cloud.langfuse.com/api/public/v2/prompts/movie-critic?label=production" \
  -u "your-public-key:your-secret-key"
```

For fetching a specific version instead of a label:

```bash
curl "https://cloud.langfuse.com/api/public/v2/prompts/movie-critic?version=1" \
  -u "your-public-key:your-secret-key"
```

- [API Reference](https://api.reference.langfuse.com/#tag/prompts/get/api/public/v2/prompts/{promptName})

</Tab>

<Tab>

```bash
pip install langfuse openai
```

```python
import openai
from langfuse import get_client

# Initialize Langfuse client
langfuse = get_client()
```

Below are code examples for both a text type prompt and a chat type prompt. Learn more about prompt types [here](/docs/prompt-management/data-model#text-vs-chat-prompts).

**Text prompt**

```python
# By default, the production version of a text prompt is fetched.
prompt = langfuse.get_prompt("movie-critic")

# Compile the prompt with variables
compiled_prompt = prompt.compile(criticlevel="expert", movie="Dune 2")

# Use with OpenAI - prompt is a string
completion = openai.chat.completions.create(
  model="gpt-4o",
  messages=[{"role": "user", "content": compiled_prompt}]
)
```

**Chat prompt**

```python
# By default, the production version of a chat prompt is fetched.
chat_prompt = langfuse.get_prompt("movie-critic-chat", type="chat")

# Compile the prompt with variables - returns a list of message dicts
compiled_chat_prompt = chat_prompt.compile(criticlevel="expert", movie="Dune 2")

# Use with OpenAI - prompt is a list of messages
completion = openai.chat.completions.create(
  model="gpt-4o",
  messages=compiled_chat_prompt
)
```

**Example notebook**

- [Example Cookbook](/guides/cookbook/prompt_management_openai_functions)

</Tab>

<Tab>

```bash
npm install @langfuse/openai openai
```

```typescript
import { observeOpenAI } from "@langfuse/openai";
import { LangfuseClient } from "@langfuse/client";
import OpenAI from "openai";

// Initialize Langfuse client
const langfuse = new LangfuseClient();

// Wrap OpenAI client
const openai = observeOpenAI(new OpenAI());
```

Below are code examples for both a text type prompt and a chat type prompt. Learn more about prompt types [here](/docs/prompt-management/data-model#text-vs-chat-prompts).

**Text prompt**

```typescript
// By default, the production version of a text prompt is fetched.
const prompt = await langfuse.prompt.get("movie-critic", {
  type: "text",
});

// Compile the prompt with variables
const compiledPrompt = prompt.compile({
  criticlevel: "expert",
  movie: "Dune 2",
});

// Use with OpenAI - prompt is a string
const completion = await openai.chat.completions.create({
  model: "gpt-4o",
  messages: [{ role: "user", content: compiledPrompt }],
});
```

**Chat prompt**

```typescript
// By default, the production version of a chat prompt is fetched.
const chatPrompt = await langfuse.prompt.get("movie-critic-chat", {
  type: "chat",
});

// Compile the prompt with variables - returns an array of messages
const compiledChatPrompt = chatPrompt.compile({
  criticlevel: "expert",
  movie: "Dune 2",
});

// Use with OpenAI - prompt is an array of messages
const completion = await openai.chat.completions.create({
  model: "gpt-4o",
  messages: compiledChatPrompt,
});
```

</Tab>

<Tab>

```python
from langfuse import Langfuse
from langchain_core.prompts import ChatPromptTemplate

# Initialize Langfuse client
langfuse = Langfuse()
```

Below are code examples for both a text type prompt and a chat type prompt. Learn more about prompt types [here](/docs/prompt-management/data-model#text-vs-chat-prompts).

These examples contain [variables](/docs/prompt-management/features/variables). As Langfuse and Langchain process input variables of prompt templates differently (`{}` instead of `{{}}`), we provide the `prompt.get_langchain_prompt()` method to transform the Langfuse prompt into a string that can be used with Langchain's PromptTemplate. You can pass optional keyword arguments to `prompt.get_langchain_prompt(**kwargs)` in order to precompile some variables and handle the others with Langchain's PromptTemplate.

**Text prompt**

```python
# By default, the production version of a text prompt is fetched.
langfuse_prompt = langfuse.get_prompt("movie-critic")

# Example using ChatPromptTemplate
langchain_prompt = ChatPromptTemplate.from_template(langfuse_prompt.get_langchain_prompt())

# Example using ChatPromptTemplate with pre-compiled variables.
langchain_prompt = ChatPromptTemplate.from_template(langfuse_prompt.get_langchain_prompt(strictness='tough'))
```

**Chat prompt**

```python
# By default, the production version of a chat prompt is fetched.
langfuse_prompt = langfuse.get_prompt("movie-critic-chat", type="chat")

# Create a Langchain ChatPromptTemplate from the Langfuse prompt chat messages
langchain_prompt = ChatPromptTemplate.from_messages(langfuse_prompt.get_langchain_prompt())
```

**Example notebook**

- [Example Cookbook](/guides/cookbook/prompt_management_langchain)

</Tab>

<Tab>

```ts
import { LangfuseClient } from "@langfuse/client";
import { ChatPromptTemplate } from "@langchain/core/prompts";

const langfuse = new LangfuseClient();
```

Below are code examples for both a text type prompt and a chat type prompt. Learn more about prompt types [here](/docs/prompt-management/data-model#text-vs-chat-prompts).

These examples contain [variables](/docs/prompt-management/features/variables). As Langfuse and Langchain process input variables of prompt templates differently (`{}` instead of `{{}}`), we provide the `prompt.get_langchain_prompt()` method to transform the Langfuse prompt into a string that can be used with Langchain's PromptTemplate. You can pass optional keyword arguments to `prompt.get_langchain_prompt(**kwargs)` in order to precompile some variables and handle the others with Langchain's PromptTemplate.

**Text prompt**

```ts
// Get current `production` version
const langfusePrompt = await langfuse.prompt.get("movie-critic");

// Example using ChatPromptTemplate
const promptTemplate = PromptTemplate.fromTemplate(
  langfusePrompt.getLangchainPrompt()
);
```

**Chat prompt**

```ts
// Get current `production` version of a chat prompt
const langfusePrompt = await langfuse.prompt.get(
  "movie-critic-chat",
  { type: "chat" }
);

// Example using ChatPromptTemplate
const promptTemplate = ChatPromptTemplate.fromMessages(
  langfusePrompt.getLangchainPrompt().map((msg) => [msg.role, msg.content])
);
```

**Example notebook**

- [Example Cookbook.](/guides/cookbook/js_prompt_management_langchain)

</Tab>

<Tab>

Use Langfuse Prompt Management with the Vercel AI SDK.

```bash
npm install @langfuse/client ai
```

```typescript
import { generateText } from "ai";
import { openai } from "@ai-sdk/openai";
import { LangfuseClient } from "@langfuse/client";

// Initialize Langfuse client
const langfuse = new LangfuseClient();
```

Below are code examples for both a text type prompt and a chat type prompt. Learn more about prompt types [here](/docs/prompt-management/data-model#text-vs-chat-prompts).

**Text prompt**

```typescript
// By default, the production version of a text prompt is fetched.
const prompt = await langfuse.prompt.get("movie-critic", {
  type: "text",
});

// Compile the prompt with variables
const compiledPrompt = prompt.compile({
  criticlevel: "expert",
  movie: "Dune 2",
});

// Use with Vercel AI SDK
const result = await generateText({
  model: openai("gpt-4o"),
  prompt: compiledPrompt,
  experimental_telemetry: {
    isEnabled: true,
  },
});
```

**Chat prompt**

```typescript
// By default, the production version of a chat prompt is fetched.
const chatPrompt = await langfuse.prompt.get("movie-critic-chat", {
  type: "chat",
});

// Compile the prompt with variables - returns an array of messages
const compiledChatPrompt = chatPrompt.compile({
  criticlevel: "expert",
  movie: "Dune 2",
});

// Use with Vercel AI SDK
const result = await generateText({
  model: openai("gpt-4o"),
  messages: compiledChatPrompt,
  experimental_telemetry: {
    isEnabled: true,
  },
});
```

</Tab>

</LangTabs>

Not seeing your latest version? This might be because of the caching behavior. See [prompt caching](/docs/prompt-management/data-model#prompt-caching) for more details.

Prompt Management is not on the critical path of your application. The SDKs [cache prompts client-side](/docs/prompt-management/features/caching), so after the first fetch they are served from memory with no extra latency. If Langfuse goes down, your application continues to use the cached prompt.

If you need 100% availability even when a new instance starts with an empty cache, see [guaranteed availability](/docs/prompt-management/features/guaranteed-availability).

</Steps>

## Not seeing what you expected?

## Next steps

Now that you've used your first prompt, here are a few things we recommend next to make the most of Langfuse Prompt Management:

- [Link prompts to traces](/docs/prompt-management/features/link-to-traces) to analyze performance by prompt version
- [Improve prompts with experiments](/docs/evaluation/experiments/experiments-via-ui) to test prompt versions on a dataset
- [Use version control and labels](/docs/prompt-management/features/prompt-version-control#protected-prompt-labels) to manage deployments across environments

Looking for something specific? Take a look under _Features_ for guides on specific topics.

<!-- agent-instructions -->

---

## Agent Instructions

This page is part of the [Langfuse](https://langfuse.com) documentation, published as plain Markdown for AI agents. Every page is available as Markdown by appending `.md` to its URL, or by sending an `Accept: text/markdown` header. This page: `https://langfuse.com/docs/prompt-management/get-started.md`.

### Querying these docs

If the answer is not on this page, query the documentation instead of guessing:

- **Semantic search** across all Langfuse docs, returning an answer with the relevant pages and excerpts. Ask a specific, self-contained question:

  ```bash
  curl -sG "https://langfuse.com/api/search-docs" --data-urlencode "query=How do I trace a LangGraph agent?"
  ```

- **Index of every page**: <https://langfuse.com/llms.txt>, with per-section indexes [llms-docs.txt](https://langfuse.com/llms-docs.txt), [llms-integrations.txt](https://langfuse.com/llms-integrations.txt), and [llms-self-hosting.txt](https://langfuse.com/llms-self-hosting.txt).

### Before writing Langfuse code

- **Install the [Langfuse Agent Skill](https://langfuse.com/docs/api-and-data-platform/features/agent-skill).** It encodes Langfuse's own best practices for instrumentation, prompt management, and evaluation, and materially improves results.
- **Read [What does a good trace look like?](https://langfuse.com/docs/observability/best-practices.md)** before instrumenting an application.
- **Verify endpoints, parameters, and response fields** against the [API reference](https://api.reference.langfuse.com) instead of inferring them from code examples.
- **Use the [Langfuse CLI](https://langfuse.com/docs/api-and-data-platform/features/cli)** (`npx langfuse-cli api <resource> <action>`) to read or write traces, prompts, datasets, and scores from the terminal.

Found an error in these docs? Please open an issue at <https://github.com/langfuse/langfuse-docs/issues>.
