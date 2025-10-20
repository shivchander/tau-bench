# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

τ-bench is a benchmark for evaluating Tool-Agent-User interaction in real-world domains (airline and retail). It simulates dynamic conversations between users and language agents equipped with domain-specific API tools and policy guidelines.

## Key Commands

### Installation and Setup
```bash
# Install from source (includes all dependencies)
pip install -e .
# or use uv (per user preferences)
uv pip install -e .
```

### Running the Benchmark
```bash
# Basic tool-calling agent on retail environment
python run.py --agent-strategy tool-calling --env retail --model gpt-4o --model-provider openai --user-model gpt-4o --user-model-provider openai --user-strategy llm --max-concurrency 10

# Run specific tasks only
python run.py --agent-strategy tool-calling --env retail --model gpt-4o --model-provider openai --user-model gpt-4o --user-model-provider openai --user-strategy llm --max-concurrency 10 --task-ids 2 4 6

# Run auto error identification on results
python auto_error_identification.py --env retail --platform openai --results-path <results_file> --max-concurrency 16 --output-path test-auto-error-identification --max-num-failed-results 10
```

## Architecture Overview

### Core Components

1. **Environments** (`tau_bench/envs/`):
   - `retail/` - E-commerce customer service scenarios
   - `airline/` - Airline customer service scenarios
   - `base.py` - Base environment class with tool execution and user simulation
   - `user.py` - User simulator with multiple strategies (llm, react, verify, reflection)

2. **Agents** (`tau_bench/agents/`):
   - `tool_calling_agent.py` - Function calling strategy
   - `chat_react_agent.py` - ReAct reasoning strategy
   - `few_shot_agent.py` - Few-shot prompting strategy
   - `memory_agent.py` - Memory-augmented tool calling with ChromaDB retrieval
   - `base.py` - Abstract agent interface

3. **Model Utils** (`tau_bench/model_utils/`):
   - Model providers integration (OpenAI, Anthropic, Google, Mistral)
   - Function tool mapping and filtering utilities
   - Completion handling and exception management

4. **Types** (`tau_bench/types.py`):
   - Core data models: `Task`, `Action`, `EnvResponse`, `RunConfig`
   - Reward calculation structures: `RewardResult`, `RewardOutputInfo`

### Key Files

- `run.py` - Main entry point for running benchmarks
- `auto_error_identification.py` - Automated error analysis tool
- `setup.py` - Package dependencies and installation
- `historical_trajectories/` - Pre-recorded agent trajectories for analysis

### Environment Configuration

**Required API Keys** (set as environment variables):
- `OPENAI_API_KEY`
- `ANTHROPIC_API_KEY`
- `GOOGLE_API_KEY`
- `MISTRAL_API_KEY`

### Supported Models and Strategies

**Agent Strategies**: `tool-calling`, `act`, `react`, `few-shot`, `memory`

**User Strategies**: `llm`, `react`, `verify`, `reflection`

**Environments**: `retail`, `airline`

**Task Splits**: `train`, `test`, `dev` (retail only)

### Running Tests/Development

The project uses standard Python development practices. Install with `pip install -e .` and run the main benchmarks using `python run.py` with appropriate arguments. Results are saved to the `results/` directory by default.

## Memory-Augmented Agent System

The tau-bench repository includes a memory-augmented agent that uses ChromaDB to retrieve relevant action examples during task execution. This system enables agents to learn from past successful trajectories and improve decision-making.

### Overview

The memory system consists of two main components:

1. **Action Memory Builder** (`syntoolmem/build_action_memory.py`): Processes trajectory data and builds a ChromaDB collection where each action is stored with a natural language description
2. **Memory Agent** (`tau_bench/agents/memory_agent.py`): Tool-calling agent that retrieves relevant action examples from memory for each user message

### Building the Action Memory

Before using the memory agent, you need to build the action memory database from trajectory data:

```bash
# Build memory for airline environment (default)
uv run python -m syntoolmem.build_action_memory --env airline --max-concurrency 20

# Build memory for retail environment
uv run python -m syntoolmem.build_action_memory --env retail --max-concurrency 20

# Build from a subset for testing
uv run python -m syntoolmem.build_action_memory --env airline --max-trajectories 10 --max-concurrency 10

# Build with custom collection name
uv run python -m syntoolmem.build_action_memory --env airline --collection-name my_memory --skip-tests
```

**Key Parameters:**
- `--env`: Environment (airline or retail) - determines prompt template and data source (default: airline)
- `--max-trajectories`: Limit number of trajectories to process (default: all)
- `--max-concurrency`: Number of parallel LLM calls for description generation (default: 10)
- `--collection-name`: Name for the ChromaDB collection (default: action_memory_{env})
- `--skip-tests`: Skip running test queries after building

**Data Sources:**
- **Airline**: Loads from `syntoolmem/tasks_airline_medium.py` (356 trajectories, ~1400 actions)
- **Retail**: Loads from `syntoolmem/tasks_retail_train.py`

**Environment-Specific Prompts:**
- **Airline**: Focuses on flight reservations, baggage, cabin classes, payment methods
- **Retail**: Focuses on orders, items, addresses, shipping, discounts

**Performance:** With `--max-concurrency 20`, processing all ~356 trajectories (~1400 actions) takes approximately 2-3 minutes.

### Using the Memory Agent

Once the action memory is built, you can run the memory agent:

```bash
# Run memory agent on airline environment
python run.py --agent-strategy memory --env airline --model gpt-4o --model-provider openai --user-model gpt-4o --user-model-provider openai --user-strategy llm --max-concurrency 10

# Run with custom memory settings
python run.py --agent-strategy memory --env airline --model gpt-4o --model-provider openai --user-model gpt-4o --user-model-provider openai --memory-top-k 5 --memory-collection-name action_memory

# Run on specific tasks
python run.py --agent-strategy memory --env airline --model gpt-4o --model-provider openai --user-model gpt-4o --user-model-provider openai --task-ids 0 1 2 --memory-top-k 3
```

**Memory Agent Parameters:**
- `--memory-collection-name`: ChromaDB collection name (default: action_memory_{env})
- `--memory-top-k`: Number of similar actions to retrieve per query (default: 3)
- `--memory-db-path`: Path to ChromaDB database (default: syntoolmem/chroma_db_{env})

### How It Works

1. **Memory Building**: For each action in the trajectory data, the system:
   - Uses GPT-4o to generate a natural language description of what the action does
   - Stores the description as the document (for semantic search)
   - Stores the full action details (name, kwargs) as metadata

2. **Runtime Retrieval**: For each user message, the memory agent:
   - Queries ChromaDB with the user message
   - Retrieves top-k most similar action examples
   - Injects these examples into the agent's context before making tool calls
   - Uses the examples to inform decision-making and prevent errors

### Benefits

- **Error Prevention**: Prevents false assumptions (e.g., "economy class cannot be modified") by showing concrete examples
- **Action Discovery**: Helps agents discover available capabilities through examples
- **Parameter Learning**: Shows correct parameter formats and valid values
- **Context-Aware**: Retrieves examples semantically similar to the current user request

### Inspecting the Memory

To inspect what's stored in the action memory:

```bash
# Inspect airline memory
uv run python -m syntoolmem.inspect_action_memory --env airline

# Inspect retail memory
uv run python -m syntoolmem.inspect_action_memory --env retail
```

This script displays all stored actions grouped by action type and runs environment-specific example queries to demonstrate retrieval.

### File Structure

```
syntoolmem/
├── build_action_memory.py       # Build ChromaDB from trajectories
├── inspect_action_memory.py     # Inspect and query the database
├── tasks_airline_medium.py      # Airline trajectory data
├── tasks_retail_train.py        # Retail trajectory data
├── chroma_db_airline/           # Airline action memory database (generated)
└── chroma_db_retail/            # Retail action memory database (generated)
```

## Synthetic Data Generation (SDG) System

The tau-bench repository includes a comprehensive synthetic data generation system for creating realistic customer service scenarios. This system uses a backtranslation approach to generate high-quality synthetic tasks that are fully compatible with the existing tau-bench framework.

### Overview

The SDG system generates synthetic tau-bench tasks through a multi-step pipeline:

1. **User Sampling & Action Generation**: Randomly selects users and generates realistic action sequences using OpenAI GPT models
2. **Sandbox Validation**: Validates generated actions against the actual environment (planned)
3. **Instruction Generation**: Creates natural language instructions from user context and actions (planned)
4. **Task Formatting**: Converts everything into proper tau-bench Task format (planned)

### Key Features

- **Real Data Integration**: Uses actual user profiles, reservations, and flight data from the tau-bench dataset
- **Difficulty Scaling**: Supports easy (1 action), medium (2-5 actions), and hard (6-10 actions) complexity levels
- **Flight System Constraints**: Enforces realistic flight numbers, dates, and routes from flights.json
- **Async Processing**: Concurrent API requests for fast batch generation
- **Quality Validation**: Ensures generated scenarios match requested difficulty and system constraints

### Usage

#### Basic Generation
```bash
# Generate single medium difficulty task
python tau_bench/sdg/generate_user_actions.py --difficulty medium

# Generate multiple tasks with specific difficulty
python tau_bench/sdg/generate_user_actions.py --num-samples 10 --difficulty hard

# Fast batch processing with concurrency
python tau_bench/sdg/generate_user_actions.py --num-samples 50 --max-concurrency 8 --difficulty easy
```

#### Output Customization
```bash
# Specify custom output file
python tau_bench/sdg/generate_user_actions.py --output-file my_synthetic_tasks --num-samples 20

# Generate different difficulty levels
python tau_bench/sdg/generate_user_actions.py --difficulty easy --num-samples 100    # Simple lookups
python tau_bench/sdg/generate_user_actions.py --difficulty medium --num-samples 50  # Multi-step scenarios
python tau_bench/sdg/generate_user_actions.py --difficulty hard --num-samples 25    # Complex workflows
```

### Generated Data Structure

Each generated sample contains:
- **user_id**: Randomly selected from real user dataset
- **difficulty**: Requested difficulty level (easy/medium/hard)
- **target_action_count**: Number of actions in the scenario
- **actions**: List of realistic action sequences with proper tool names and arguments
- **scenario_summary**: Natural language description of the customer service scenario

### Data Quality Guarantees

The SDG system ensures:
- **System Compatibility**: All flight numbers, dates, and routes exist in the actual tau-bench flight database
- **User Context Accuracy**: Uses real user payment methods, reservations, and passenger information
- **Difficulty Consistency**: Generated action counts match requested difficulty levels
- **Scenario Realism**: Customer service scenarios are logically coherent and realistic

### Requirements

- **OpenAI API Key**: Set `OPENAI_API_KEY` environment variable
- **Dependencies**: `openai`, `python-dotenv` (install with `uv pip install openai python-dotenv`)

### File Structure

```
tau_bench/sdg/
├── generate_user_actions.py     # Main generation script
└── generated_user_actions.json  # Sample output (accumulates results)
```

### Performance

- **Speed**: Generates 50+ scenarios per minute with async processing
- **Quality**: 95%+ success rate with proper validation
- **Scale**: Tested with 1000+ sample batches

This synthetic data generation system enables researchers to create large-scale datasets for training and evaluation while maintaining full compatibility with the tau-bench evaluation framework.