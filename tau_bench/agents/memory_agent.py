# Copyright Sierra

import json
from litellm import completion
from typing import List, Optional, Dict, Any
from pathlib import Path
import chromadb

from tau_bench.agents.base import Agent
from tau_bench.envs.base import Env
from tau_bench.types import SolveResult, Action, RESPOND_ACTION_NAME


class MemoryAgent(Agent):
    """
    Tool-calling agent enhanced with action memory retrieval from ChromaDB.

    For each user turn, retrieves top-k similar action examples from memory
    and includes them in the context to inform tool-calling decisions.
    """

    def __init__(
        self,
        tools_info: List[Dict[str, Any]],
        wiki: str,
        model: str,
        provider: str,
        temperature: float = 0.0,
        memory_collection_name: str = "action_memory",
        memory_top_k: int = 3,
        memory_db_path: Optional[str] = None,
    ):
        self.tools_info = tools_info
        self.wiki = wiki
        self.model = model
        self.provider = provider
        self.temperature = temperature
        self.memory_top_k = memory_top_k

        # Load ChromaDB collection
        if memory_db_path is None:
            # Default to syntoolmem/chroma_db
            project_root = Path(__file__).parent.parent.parent
            memory_db_path = str(project_root / "syntoolmem" / "chroma_db")

        self.chroma_client = chromadb.PersistentClient(path=memory_db_path)

        try:
            self.memory_collection = self.chroma_client.get_collection(memory_collection_name)
            print(f"✓ Loaded memory collection '{memory_collection_name}' with {self.memory_collection.count()} actions")
        except Exception as e:
            print(f"Warning: Could not load memory collection '{memory_collection_name}': {e}")
            self.memory_collection = None

    def retrieve_similar_actions(self, query: str) -> str:
        """
        Query ChromaDB for similar actions and format them as context.

        Args:
            query: User message to query against action memory

        Returns:
            Formatted string with retrieved action examples
        """
        if self.memory_collection is None:
            return ""

        try:
            results = self.memory_collection.query(
                query_texts=[query],
                n_results=self.memory_top_k
            )

            if not results['documents'][0]:
                return ""

            # Format retrieved actions as examples
            examples = []
            examples.append("# Similar Actions from Memory\n")
            examples.append("Here are some relevant action examples from past trajectories:\n")

            for idx, (doc, metadata) in enumerate(
                zip(results['documents'][0], results['metadatas'][0]), 1
            ):
                action = json.loads(metadata['action'])
                examples.append(f"\n## Example {idx}")
                examples.append(f"Description: {doc}")
                examples.append(f"Action: {action['name']}")
                examples.append(f"Parameters: {json.dumps(action['kwargs'], indent=2)}")

            return "\n".join(examples)

        except Exception as e:
            print(f"Error retrieving from memory: {e}")
            return ""

    def solve(
        self, env: Env, task_index: Optional[int] = None, max_num_steps: int = 90
    ) -> SolveResult:
        total_cost = 0.0
        env_reset_res = env.reset(task_index=task_index)
        obs = env_reset_res.observation
        info = env_reset_res.info.model_dump()
        reward = 0.0

        # Initial messages with system prompt and first user message
        messages: List[Dict[str, Any]] = [
            {"role": "system", "content": self.wiki},
        ]

        # Retrieve similar actions for initial user message
        memory_context = self.retrieve_similar_actions(obs)

        # Add user message with memory context if available
        if memory_context:
            user_content = f"{obs}\n\n{memory_context}"
        else:
            user_content = obs

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

                # Retrieve similar actions for the new user message
                memory_context = self.retrieve_similar_actions(env_response.observation)

                # Add user message with memory context
                if memory_context:
                    user_content = f"{env_response.observation}\n\n{memory_context}"
                else:
                    user_content = env_response.observation

                messages.append({"role": "user", "content": user_content})

            if env_response.done:
                break

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
