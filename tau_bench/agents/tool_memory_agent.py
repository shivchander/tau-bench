# Copyright Sierra

import json
from litellm import completion
from typing import List, Optional, Dict, Any
from pathlib import Path
import chromadb

from tau_bench.agents.base import Agent
from tau_bench.envs.base import Env
from tau_bench.types import SolveResult, Action, RESPOND_ACTION_NAME


class ToolMemoryAgent(Agent):
    """
    Tool-calling agent enhanced with scenario memory retrieval from ChromaDB.

    For each user turn, retrieves top-k similar scenarios showing:
    - Happy paths: Valid user requests that led to successful tool calls
    - Adversarial paths: Invalid requests that violated policy and were refused

    This helps the agent learn both what to do AND what not to do.
    """

    def __init__(
        self,
        tools_info: List[Dict[str, Any]],
        wiki: str,
        model: str,
        provider: str,
        temperature: float = 0.0,
        memory_collection_name: str = "tool_memory_airline",
        memory_top_k: int = 2,  # Fetch 2 happy + 2 adversarial
        memory_db_path: Optional[str] = None,
        memory_mode: str = "balanced",  # "balanced", "happy_only", or "adversarial_only"
    ):
        self.tools_info = tools_info
        self.wiki = wiki
        self.model = model
        self.provider = provider
        self.temperature = temperature
        self.memory_top_k = memory_top_k
        self.memory_mode = memory_mode

        # Load ChromaDB collection for tool memories
        if memory_db_path is None:
            # Default to syntoolmem/chroma_db_tool_memories
            project_root = Path(__file__).parent.parent.parent
            memory_db_path = str(project_root / "syntoolmem" / "chroma_db_tool_memories")

        self.chroma_client = chromadb.PersistentClient(path=memory_db_path)

        try:
            self.memory_collection = self.chroma_client.get_collection(memory_collection_name)
            print(f"✓ Loaded tool memory collection '{memory_collection_name}' with {self.memory_collection.count()} scenarios")
            print(f"✓ Memory mode: {memory_mode} (top-k={memory_top_k})")
        except Exception as e:
            print(f"Warning: Could not load tool memory collection '{memory_collection_name}': {e}")
            self.memory_collection = None

    def retrieve_similar_scenarios(self, query: str) -> str:
        """
        Query ChromaDB for similar scenarios and format them as context.

        Retrieves both happy paths (what works) and adversarial paths (what doesn't)
        to help the agent make better policy-compliant decisions.

        Args:
            query: User message to query against scenario memory

        Returns:
            Formatted string with retrieved scenario examples
        """
        if self.memory_collection is None:
            return ""

        try:
            context_parts = []
            context_parts.append("# Similar Scenarios from Memory\n")
            context_parts.append("Below are examples of similar requests showing what is allowed and what violates policy.\n")

            # Retrieve based on memory mode
            if self.memory_mode in ["balanced", "happy_only"]:
                # Fetch happy paths (policy-compliant examples)
                happy_results = self.memory_collection.query(
                    query_texts=[query],
                    n_results=self.memory_top_k,
                    where={"path_type": "happy"}
                )

                if happy_results['documents'][0]:
                    context_parts.append("\n## ✅ Valid Requests (Policy-Compliant)\n")
                    context_parts.append("These requests were approved and led to successful tool calls:\n")

                    for idx, (doc, metadata) in enumerate(
                        zip(happy_results['documents'][0], happy_results['metadatas'][0]), 1
                    ):
                        context_parts.append(f"\n### Example {idx}")
                        context_parts.append(f"**User said:** {doc}")
                        context_parts.append(f"**Policy check:** {metadata['policy_reasoning']}")
                        context_parts.append(f"**Action taken:** {metadata['tool_name']}")

                        # Optionally include tool call for reference
                        if metadata.get('tool_call') and metadata['tool_call'] != 'null':
                            try:
                                tool_call = json.loads(metadata['tool_call'])
                                if 'tool_calls' in tool_call and tool_call['tool_calls']:
                                    func_args = tool_call['tool_calls'][0]['function']['arguments']
                                    context_parts.append(f"**Tool arguments:** {func_args}")
                            except:
                                pass

            if self.memory_mode in ["balanced", "adversarial_only"]:
                # Fetch adversarial paths (policy violations)
                adversarial_results = self.memory_collection.query(
                    query_texts=[query],
                    n_results=self.memory_top_k,
                    where={"path_type": "adversarial"}
                )

                if adversarial_results['documents'][0]:
                    context_parts.append("\n## ❌ Policy Violations (Should Refuse)\n")
                    context_parts.append("These requests violated policy and were refused:\n")

                    for idx, (doc, metadata) in enumerate(
                        zip(adversarial_results['documents'][0], adversarial_results['metadatas'][0]), 1
                    ):
                        context_parts.append(f"\n### Example {idx}")
                        context_parts.append(f"**User said:** {doc}")
                        context_parts.append(f"**Why refused:** {metadata['policy_reasoning']}")

                        # Include refusal message as template
                        if metadata.get('refusal_message'):
                            context_parts.append(f"**Agent refused:** {metadata['refusal_message']}")

            result = "\n".join(context_parts)
            return result if len(context_parts) > 2 else ""  # Only return if we have actual examples

        except Exception as e:
            print(f"Error retrieving from tool memory: {e}")
            return ""

    def solve(
        self, env: Env, task_index: Optional[int] = None, max_num_steps: int = 90
    ) -> SolveResult:
        total_cost = 0.0
        env_reset_res = env.reset(task_index=task_index)
        obs = env_reset_res.observation
        info = env_reset_res.info.model_dump()
        reward = 0.0

        # Track memory retrievals
        memory_retrievals = []

        # Initial messages with system prompt and first user message
        messages: List[Dict[str, Any]] = [
            {"role": "system", "content": self.wiki},
        ]

        # Retrieve similar scenarios for initial user message
        memory_context = self.retrieve_similar_scenarios(obs)

        # Add user message with memory context if available
        if memory_context:
            user_content = f"{obs}\n\n{memory_context}"
            memory_retrievals.append({
                "turn": 0,
                "query": obs,
                "retrieved": True
            })
            # print(f"[ToolMemory] Retrieved {self.memory_top_k} scenarios for turn 0")
        else:
            user_content = obs
            memory_retrievals.append({
                "turn": 0,
                "query": obs,
                "retrieved": False
            })
            # print(f"[ToolMemory] No scenarios retrieved for turn 0")

        messages.append({"role": "user", "content": user_content})

        for _ in range(max_num_steps):
            res = completion(
                messages=messages,
                model=self.model,
                custom_llm_provider=self.provider,
                tools=self.tools_info,
                temperature=self.temperature,
            )
            next_message = res.choices[0].message.model_dump()
            total_cost += res._hidden_params["response_cost"] or 0
            action = message_to_action(next_message)
            env_response = env.step(action)
            reward = env_response.reward
            info = {**info, **env_response.info.model_dump()}

            if action.name != RESPOND_ACTION_NAME:
                # Tool call response
                next_message["tool_calls"] = next_message["tool_calls"][:1]
                messages.extend(
                    [
                        next_message,
                        {
                            "role": "tool",
                            "tool_call_id": next_message["tool_calls"][0]["id"],
                            "name": next_message["tool_calls"][0]["function"]["name"],
                            "content": env_response.observation,
                        },
                    ]
                )
            else:
                # User response - retrieve memory for next turn
                messages.append(next_message)

                # Retrieve similar scenarios for the new user message
                memory_context = self.retrieve_similar_scenarios(env_response.observation)

                # Track retrieval
                turn_number = len([m for m in messages if m.get("role") == "user"])
                if memory_context:
                    memory_retrievals.append({
                        "turn": turn_number,
                        "query": env_response.observation,
                        "retrieved": True
                    })
                    user_content = f"{env_response.observation}\n\n{memory_context}"
                    # print(f"[ToolMemory] Retrieved {self.memory_top_k} scenarios for turn {turn_number}")
                else:
                    memory_retrievals.append({
                        "turn": turn_number,
                        "query": env_response.observation,
                        "retrieved": False
                    })
                    user_content = env_response.observation
                    # print(f"[ToolMemory] No scenarios retrieved for turn {turn_number}")

                messages.append({"role": "user", "content": user_content})

            if env_response.done:
                break

        # Add memory retrieval stats to info
        memory_retrieval_count = len([r for r in memory_retrievals if r["retrieved"]])
        info["memory_retrievals"] = memory_retrievals
        info["memory_retrieval_count"] = memory_retrieval_count
        info["total_turns"] = len(memory_retrievals)

        # Print summary
        print(f"[ToolMemory] Summary: {memory_retrieval_count}/{len(memory_retrievals)} turns used memory")

        return SolveResult(
            reward=reward,
            info=info,
            messages=messages,
            total_cost=total_cost,
        )


def message_to_action(
    message: Dict[str, Any],
) -> Action:
    if "tool_calls" in message and message["tool_calls"] is not None and len(message["tool_calls"]) > 0 and message["tool_calls"][0]["function"] is not None:
        tool_call = message["tool_calls"][0]
        return Action(
            name=tool_call["function"]["name"],
            kwargs=json.loads(tool_call["function"]["arguments"]),
        )
    else:
        return Action(name=RESPOND_ACTION_NAME, kwargs={"content": message["content"]})
