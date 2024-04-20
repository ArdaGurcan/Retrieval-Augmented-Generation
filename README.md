A chatbot that enables users to ask questions of a given dataset using OpenAI's GPT models and Weaviate Vector Database

# Implementation
## Data storage
Initially, the `small_pubmed_manuscripts.jsonl` is read into the Weaviate Vector Database. This is done by streaming lines from the file and adding them to the Weaviate database, which uses OpenAI's text-embedding-3-small model to convert them into vector embeddings for storage. This is implemented in `weaviate-setup.ipynb`.

## Chat interface
During the execution of the main program:
1. User is asked for a prompt
2. Keywords from current prompt and any needed keywords from previous prompts are extracted using OpenAI's gpt-3.5-turbo model
3. Weaviate database is queried for 5 data objects closest to the prompt keywords based on vector similarity.
4. Prompt is added to message history
5. The results of the query are combined with the question as context and a new API request is made to OpenAI's gpt-3.5-turbo model including previous messages and current context + question
6. The response from OpenAI is added to message history and displayed on the command line. Execution loops back to step 1.

This is implemented in `main.py`.

# Design Decisions
## Vector Database
I chose Weaviate because of its scalability and because it allows hybrid search right away which can be used for debugging.

## Choice of Language
I chose Python for its ease of prototyping, ease of integration, and strong library ecosystem.

## Language Model
I chose OpenAI's GPT family for its ease of use and my previous familiarity with it. I used text-embedding-3-small for generating embeddings and gpt-3.5-turbo for chat completions and keyword extraction. The reason I chose these models is their cost effectivenesses which was ideal for prototyping.

## Dataset
I chose the [PubMed Author Manuscripts Database](https://huggingface.co/datasets/TaylorAI/pubmed_author_manuscripts) as it is small yet big enough for prototyping my use case. I used the first 100 entries for testing, as they were enough to exceed the context window of text-embedding-3-small and gpt-3.5-turbo.

# Challenges Faced
- During the reading of data into the dataset, some manuscripts are longer than the embedding model's (text-embedding-3-small) context length. This was solved by separating each manuscript into overlapping windows.
- At first, user's raw prompt was being used for the vector similarity search. This approach decreased the quality of the search results. So instead another request to OpenAI was made to extract keywords from user question. However, this proved limited as it didn't account for questions that relied on previous messages. The final approach is to include the message history when asking for prompt extraction. The downside of this approach is that it doubled the response time and cost.


# Sample run
```
$ python main.py

Please enter your question (or type 'exit' to quit): hello
Keywords: hello

Answer: Hello! How can I assist you today?

Please enter your question (or type 'exit' to quit): How does estradiol impact fear in rats?
Keywords: estradiol, fear, rats, impact

Answer: Estradiol impacts fear in rats by modulating fear extinction memory consolidation. Studies have shown that estradiol administration in female rats can enhance fear extinction memory recall, alter neuronal function within the fear extinction network, and influence the distribution of neuronal activation among key brain structures involved in fear expression and inhibition, such as the infralimbic cortex (IL), prelimbic cortex (PL), amygdala, and hippocampus. Specifically, estradiol treatment has been associated with changes in c-fos expression in different brain regions during fear extinction learning and recall, indicating a shift in neuronal activity patterns that may contribute to improved fear extinction memory. This modulation of fear-related circuitry by estradiol suggests a potential neuromodulatory role for this hormone in fear processing in female rats.

Please enter your question (or type 'exit' to quit): Is there a difference between its impact on males and females?
Keywords: estradiol, fear, impact, difference, males, females, fear extinction, memory consolidation, neuronal activation, brain regions, c-fos expression, fear processing

Answer: Yes, there is a difference in the impact of estradiol on fear extinction memory consolidation between males and females. Studies have shown that estradiol administration in female rats can enhance fear extinction memory recall and modulate neuronal activity within the fear extinction network, particularly in regions like the infralimbic cortex (IL) and amygdala. This modulation by estradiol appears to shift the balance of neuronal activity towards the IL for increased inhibitory control over fear output from the amygdala, leading to improved extinction memory recall in females.

While the neurobiology of fear has been extensively studied in males, the findings suggest that estradiol's effects on fear extinction memory consolidation may differ between males and females. The higher prevalence of fear and anxiety disorders in women compared to men underscores the importance of understanding how estradiol can affect the neural substrates and mechanisms that control fear responses, highlighting potential sex differences in fear processing and the role of estradiol in modulating fear-related circuitry.

Please enter your question (or type 'exit' to quit): exit
$
```

# How to run
## Add OpenAI API key
Create a file named `.env` and add line `OPENAI_API_KEY=YOUR-KEY-HERE`

## Requirements
### Pip packages
```bash
pip install -r requirements.txt
```
### Docker
You need to have Docker and Docker Compose

## Compose Docker Container
The port for the Weaviate database can be configured in `docker-compose.yml`.

```bash
# Make sure OPENAI_API_KEY is set as an environment variable before running this
docker-compose up -d
```
