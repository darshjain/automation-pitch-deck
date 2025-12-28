
# Sago Pitch Deck Verification Agent  
**Technical Assessment Submission**

This project presents an **agentic system** designed to function as a first-pass investment analyst. The system autonomously ingests startup pitch decks, extracts verifiable claims, validates those claims through live web search, and evaluates the results against Sago’s investment thesis.

The primary objective is to reduce investor cognitive load by systematically filtering non-verifiable marketing statements and surfacing evidence-backed signals such as market size, traction, and competitive positioning.

---

## Architecture & Design Rationale

```ascii
[ Ingestion Layer ]        [ Orchestration Layer ]             [ Agent Layer ]
+-----------------+        +---------------------+      +---------------------------+
|  Gmail Source   +------->+                     |      |                           |
+-----------------+        |     Event Loop      +----->+  1. Claim Extraction      |       +---------------+
                           |  ( src/core.py )    |      |     (LLM based)           +------>+ OpenAI GPT-4  |
+-----------------+        |                     |      |                           |       +---------------+
|  Slack Bot      +------->+          ^          |      +------------+--------------+
+-----------------+        +----------|----------+                   |
                                      |                              v
                                      |                 +------------+--------------+       +---------------+
                                      |                 |                           |       | DuckDuckGo    |
                                      +---------------->+  2. Verification Agent    +------>+ Search API    |
                                      |                 |     (Re-Act Loop)         |       +---------------+
                                      |                 +------------+--------------+
                                      |                              |
                                      |                              v
                                      |                 +------------+--------------+       +-------------------+
                                      |                 |                           |       | Portfolio Context |
                                      +---------------->+  3. Strategic Analyst     +<------+ (Vector/Mock DB)  |
                                                        |    (Thesis Matching)      |       +-------------------+
                                                        +------------+--------------+
                                                                     |
                                                                     v
 [ Output Layer ]                                           [ Persistence Layer ]
+-----------------+                                         +-------------------+
|  Slack Bot      +<----------------------------------------+                   |
+-----------------+                                         |      MongoDB      |
                                                            |                   |
+-----------------+                                         +-------------------+
+-----------------+
|  Email Sent     +<----------------------------------------+
+-----------------+
```

The system architecture follows a modular, event-driven pattern designed for resilience and clear separation of concerns.

**Core Design Decisions:**
Three foundational choices drive this architecture:
1.  **Agentic Reasoning over static RAG**: Investment verification requires active investigation ("Verify then Trust"), mimicking a human analyst's multi-step research process rather than simple passive retrieval.
2.  **Event-Driven Ingestion**: Venture deal flow is highly asynchronous and bursty; using an event loop decouples high-volume ingestion (e.g., email floods) from high-latency verification tasks, preventing system lockup.
3.  **Modular Monolith**: This structure balances rapid development velocity with strict boundary enforcement, allowing for independent scaling of components (ingestion vs. analysis) without the immediate operational overhead of a full microservices mesh.

1.  **Ingestion Layer**: Asynchronous connectors (`Ingestion Sources`) monitor channels like Gmail and Slack, normalizing incoming pitch decks into standardized event payloads.
2.  **Event Loop**: A central, non-blocking bus orchestrated by `src/core.py` manages the state machine, routing events to the appropriate analysis agents without tight coupling.
3.  **Agent Layer**: Specialized agents execute the core logic:
    *   **Claim Extraction**: Uses LLMs to parse unstructured PDF text into verifiable claims.
    *   **Verification**: Performs a "Re-Act" loop (Reason-Act-Observe) using search APIs to validate claims against external data.
    *   **Strategic Analysis**: Synthesizes verified data with `Portfolio Context` to assess thesis fit.
4.  **Output Layer**: The `Notification Service` consumes final reports and routes them back to the user via the originating channel (e.g., proper email reply or Slack thread), completing the feedback loop.

### 1. Agentic Reasoning Loop (Plan → Act → Observe)

Rather than relying on a conventional RAG pipeline, the system is structured around an **agentic reasoning loop**:

1. **Claim Extraction**  
   The agent differentiates between objectively verifiable statements (e.g., “$5M ARR”, “10k active customers”) and subjective or non-falsifiable claims (e.g., “best-in-class team”).

2. **Autonomous Verification**  
   For each verifiable claim, the agent formulates targeted search queries and evaluates retrieved evidence. If results are ambiguous or insufficient, the agent re-plans and executes additional searches (simulated for this assignment).

3. **Thesis Alignment**  
   A `PortfolioManager` context is applied to assess strategic fit with Sago’s investment thesis, including basic anti-portfolio checks. This ensures the output reflects relevance to Sago rather than generic startup quality.

This loop prioritizes transparency and debuggability over opaque chain-based abstractions.

---

### 2. Event-Driven Ingestion & Delivery

The system is organized around a central, non-blocking **event loop** (`src/core.py`) that manages the full lifecycle from ingestion to user feedback.

**Rationale**  
Venture workflows are inherently asynchronous—pitch decks arrive via multiple channels, and response expectations vary (e.g., immediate Slack ack vs. formal email analysis).

**Design**
- **Ingestion**: Connectors for **Gmail** and **Slack** emit events into the loop.
- **Orchestration**: The bus routes events to analysis modules (Extraction -> Verification -> Strategy).
- **Delivery**: Results are routed to the **Output Layer**, triggering **Slack Bot** alerts or **Email** responses based on the source context.

This design allows new channels to be plugged in without modifying core reasoning logic.

---

### 3. Modular Monolith Strategy

For this scope, the system is implemented as a **modular monolith**.

- Ingestion, analysis, and verification are separated at the module level.
- Clear service boundaries are enforced through interfaces rather than network calls.

**Rationale**  
This approach minimizes operational complexity while preserving a clear migration path to microservices. Modules such as `src/ingestion` and `src/verification` are structured so they can be extracted into independent services (e.g., AWS Lambda or Kubernetes workloads) with minimal refactoring.

---

## Technology Stack & Justification

- **Language: Python 3.10+**  
  Chosen for its ease of use in ML/AI workflows and mature ecosystem for LLM integration, async processing, and rapid iteration.

- **Orchestration: Custom Python FSM**  
  Explicit control flow was favored over frameworks such as LangChain to improve debuggability, observability, and production reliability.

- **LLM: OpenAI GPT-4**  
  Selected for ease of use and cost-effectiveness. Can use more expensive models depending on the use case.

- **Database: MongoDB**  
  Pitch deck data is deeply nested and semi-structured (Deck → Slides → Claims). A document store maps naturally to this structure and avoids premature schema rigidity. Also allows future extensibility for integrating more data sources and possibly referencing Blob storage.

- **Search: DuckDuckGo**  
  Used for live verification due to its simplicity and lack of quota overhead, suitable for a demo environment.

- **Messaging (Proposed Design): Apache Kafka**  
  Chosen for high-throughput event streaming, replayability, and suitability for future re-processing with updated models. This was not implemented in the demo but can be added in the future to allow for more complex workflows.

---

## Workflow Automation Patterns

Two integration strategies are supported to accommodate different operational contexts.

### Option 1: Low-Code Automation (n8n / Zapier)
**Use case**: Rapid internal deployment and operational experimentation.

- Trigger: New pitch email in a monitored inbox.
- Action: Webhook call to the Sago API.
- Routing logic:
  - High-priority → Slack notification.
  - Pass → Drafted response email.

This enables non-engineering teams to adapt workflows without code changes.

---

### Option 2: Custom Event-Driven Integration
**Use case**: High-scale, production-grade deployment.

- Ingestion via Kafka topic (`raw-submissions`).
- Processing by the Sago agent.
- Emission of results to downstream topics (`analysis-completed`).

Consumers may include CRM synchronization services or internal notification systems. This model supports replayability and tight integration with proprietary tooling.

---

## Scalability Roadmap

```ascii
[ Sources ]              [ Event Bus ]             [ Microservices Cluster (K8s) ]
+-------------+          +-----------+             +---------------------------+
| Web Portal  +--------->+           +------------>+  Ingestion Service        |
+-------------+          |           |             |  (GPU OCR / parsing)      |
                         |  KAFKA    |             +-------------+-------------+
+-------------+          |  Topic:   |                           |
| Gmail Source+--------->+  'raw'    |                           v
+-------------+          |           |             +---------------------------+
                         |           |             |  Orchestrator Service     |
+-------------+          |           +------------>+  (State Management)       +-------+
| Slack Bot   +--------->+           |             +-------------+-------------+       |
+-------------+          +-----------+                           |                     v
                                                                 |                +----+----+
                         +-----------+                           |                | Mongo   |
                         |           |             +-------------+-------------+  | DB      |
                         |  KAFKA    +------------>+  Verification Workers     |  +---------+
                         |  Topic:   |             |  (Sharded by Industry)    |
                         |  'jobs'   |             +-------------+-------------+
                         |           |                           |
                         +-----------+                           v
                                                   +---------------------------+       +-------------------+
                                                   |  Vector DB (Pinecone)     +       | Notification Svc  |
                                                   |  (Historical Knowledge)   |       | (Routing Logic)   |
                                                   +---------------------------+       +--------+----------+
                                                                                          ^     |
                                                                                          |     v
                                                                                   +------+------------+
                                                                                   |                   |
                                                                                   +-> [ Slack Bot ]   |
                                                                                   |                   |
                                                                                   +-> [ Email Sent ]  |
                                                                                   |                   |
                                                                                   +-------------------+
```

The scaled architecture replaces the monolithic event loop with distributed infrastructure to handle high throughput:
1.  **Decoupled Ingestion**: Sources push raw data to a **Kafka** topic (`raw`), allowing the ingestion layer to scale independently of processing capacity.
2.  **Microservices Cluster**:
    *   **Ingestion Service**: Specialized GPU-enabled workers handle OCR and document parsing.
    *   **Verification Workers**: Stateless inputs/outputs allow these to be horizontally scaled on Kubernetes and sharded by vertical (e.g., distinct worker pools for BioTech vs. SaaS).
3.  **Semantic Memory**: A **Vector Database (Pinecone)** acts as the long-term knowledge store, enabling the system to perform retrieval-augmented generation (RAG) against historical deal flow.
4.  **Routing Logic**: A dedicated **Notification Service** subscribes to the `analysis-completed` topic, handling channel-specific formatting and delivery to ensure reliability.

### 1. Distributed Worker Model
The orchestrator can be decoupled from ingestion endpoints.

- Webhooks enqueue processing requests.
- Auto-scaling worker pools consume jobs asynchronously.

This protects ingestion reliability during peak submission periods.

---

### 2. Service Specialization
Verification services can be sharded by domain:

- SaaS-focused verifiers integrating commercial data sources.
- BioTech-focused verifiers integrating academic or regulatory databases.

This enables domain-specific optimization without bloating a single service.

---

### 3. Knowledge Graph & Vector Retrieval
The current in-memory portfolio context can be replaced with a managed vector database (e.g., Pinecone based on past experience).

This enables semantic recall over historical deal flow, supporting questions such as prior exposure to similar companies or markets.

---

## Project Structure

- `src/main.py`: Orchestrator and system entry point  
- `src/core.py`: Asynchronous event loop  
- `src/analysis/`: Core reasoning components  
  - `verifier.py`: Claim validation logic  
  - `analyst.py`: Thesis alignment and reporting  
  - `portfolio_manager.py`: Firm-specific context  
- `src/integrations/`: External adapters  
- `Dockerfile`: Production-ready containerization

---

## Execution

### Installation
```bash
git clone <repo>
cd pitch_deck_automation
pip install -r requirements.txt
````

### Demo

```bash
bash run_demo.sh
```

### Tests

```bash
export PYTHONPATH=$PYTHONPATH:$(pwd)
pytest tests/
```
