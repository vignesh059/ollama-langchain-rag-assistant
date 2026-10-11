"""
Integrated Agent Engine with Tool Routing, Memory, Ollama Execution, and Strict PDF RAG Mode.
"""

import re
from typing import Dict, Any, List, Callable, Optional, Tuple
from langchain_community.chat_models import ChatOllama
from langchain_core.messages import SystemMessage, HumanMessage, AIMessage

from backend.llm_engine import llm_engine_instance
from backend.memory_engine import memory_engine_instance
from backend.rag_engine import rag_engine_instance
from backend.tools.attendance_tool import calculate_attendance_tool
from backend.tools.wikipedia_tool import wikipedia_search_tool
from backend.tools.pdf_rag_tool import pdf_rag_search_tool
from config import DEFAULT_SYSTEM_PROMPT


class AgentEngine:
    def __init__(self, system_prompt: str = DEFAULT_SYSTEM_PROMPT):
        self.system_prompt = system_prompt
        self.tools = {
            "attendance": calculate_attendance_tool,
            "wikipedia": wikipedia_search_tool,
            "pdf_rag": pdf_rag_search_tool,
        }

    def detect_intent_and_execute_tool(self, user_input: str) -> Tuple[Optional[str], Optional[str]]:
        """
        Analyzes user input for tool execution.
        If a PDF is uploaded, ALL queries are handled via Strict PDF RAG.
        Otherwise, routes to Attendance, Wikipedia, or General Chat.
        """
        input_lower = user_input.lower().strip()

        # 1. STRICT PDF RAG MODE (Active whenever a PDF document is uploaded)
        if rag_engine_instance.vectorstore is not None:
            rag_output = pdf_rag_search_tool.invoke({"query": user_input})
            return "PDF Search (RAG)", rag_output

        # 2. Custom Class Attendance Tool Intent Detection
        attn_patterns = [
            r'(?:present|attended|done|completed|got|have)\s+(\d+)\s*(?:out of|of|/|\s+from\s+)\s*(\d+)',
            r'(\d+)\s*(?:classes|class|lectures|sessions)\s*(?:out of|of|/)\s*(\d+)',
            r'(\d+)\s*/\s*(\d+)\s*(?:classes|class|attendance)?',
            r'(?:attendance|classes).*?(\d+).*?(\d+)'
        ]
        
        for pattern in attn_patterns:
            match = re.search(pattern, input_lower)
            if match:
                try:
                    num1 = int(match.group(1))
                    num2 = int(match.group(2))
                    if num2 > 0 and num1 <= num2:
                        result = calculate_attendance_tool.invoke({
                            "attended_classes": num1,
                            "total_classes": num2
                        })
                        return "Attendance Calculator", result
                except Exception:
                    pass

        if "attendance" in input_lower or "classes" in input_lower or "bunk" in input_lower:
            nums = re.findall(r'\b\d+\b', input_lower)
            if len(nums) >= 2:
                num1, num2 = int(nums[0]), int(nums[1])
                if num2 > num1 and num2 > 0:
                    result = calculate_attendance_tool.invoke({
                        "attended_classes": num1,
                        "total_classes": num2
                    })
                    return "Attendance Calculator", result

        # 3. Wikipedia Search Tool Intent Detection
        wiki_triggers = [
            r'search\s+(?:wikipedia|wiki)\s+(?:for\s+)?(.+)',
            r'wiki\s+(.+)',
            r'search\s+what\s+is\s+(.+)',
            r'what\s+is\s+wikipedia\s+(.+)',
            r'look\s+up\s+on\s+wikipedia\s+(.+)'
        ]
        for trigger in wiki_triggers:
            w_match = re.search(trigger, input_lower)
            if w_match:
                query_term = w_match.group(1).strip()
                result = wikipedia_search_tool.invoke({"query": query_term})
                return "Wikipedia Search", result

        return None, None

    def process_query(
        self, 
        user_input: str, 
        model_name: str = "llama3.2:latest",
        on_tool_called: Optional[Callable[[str], None]] = None
    ) -> Dict[str, Any]:
        """
        Main query processing entry point.
        Enforces Strict PDF context when a document is uploaded.
        """
        tool_name, tool_output = self.detect_intent_and_execute_tool(user_input)

        if tool_name and on_tool_called:
            on_tool_called(tool_name)

        # Build message stack
        messages = []

        # Check if Strict PDF RAG Mode is active
        is_pdf_mode = rag_engine_instance.vectorstore is not None

        if is_pdf_mode:
            strict_system_prompt = (
                "CRITICAL INSTRUCTION: You are in STRICT PDF DOCUMENT QUESTION-ANSWERING MODE. "
                "You MUST answer the user's question STRICTLY based ONLY on the provided PDF document context below. "
                "Do NOT use outside knowledge, assumptions, or external facts. "
                "If the answer is NOT present in the provided context, state clearly: "
                "'The uploaded document does not contain information about this question. Please ask a question related to the uploaded PDF document.'"
            )
            messages.append(SystemMessage(content=strict_system_prompt))

            # History context if applicable
            history_text = memory_engine_instance.get_formatted_history()
            if history_text and history_text != "No prior conversation history.":
                messages.append(SystemMessage(content=f"Previous Conversation History:\n{history_text}"))

            prompt_content = (
                f"PDF Document: {rag_engine_instance.doc_name}\n\n"
                f"Retrieved Document Context:\n{tool_output}\n\n"
                f"User Question: {user_input}\n\n"
                f"Answer strictly using ONLY the retrieved document context above."
            )
            messages.append(HumanMessage(content=prompt_content))

        else:
            messages.append(SystemMessage(content=self.system_prompt))

            history_text = memory_engine_instance.get_formatted_history()
            if history_text and history_text != "No prior conversation history.":
                messages.append(SystemMessage(content=f"Previous Conversation History:\n{history_text}"))

            if tool_output:
                prompt_content = (
                    f"User Question: {user_input}\n\n"
                    f"Tool Result ({tool_name}):\n{tool_output}\n\n"
                    f"Instructions: Incorporate the tool result above into a helpful response."
                )
            else:
                prompt_content = user_input

            messages.append(HumanMessage(content=prompt_content))

        # Get LLM instance
        llm = llm_engine_instance.get_llm(model_name=model_name)

        try:
            response = llm.invoke(messages)
            ai_response_text = response.content if hasattr(response, 'content') else str(response)
        except Exception as e:
            if tool_output:
                ai_response_text = (
                    f"⚠️ Note: Ollama LLM is currently unreachable ({str(e)}), but here is the document search result:\n\n"
                    f"{tool_output}"
                )
            else:
                ai_response_text = (
                    f"⚠️ Could not connect to Ollama model '{model_name}'. Error: {str(e)}"
                )

        # Record in LangChain memory
        memory_engine_instance.add_user_message(user_input)
        memory_engine_instance.add_ai_message(ai_response_text)

        return {
            "response": ai_response_text,
            "tool_used": tool_name,
            "tool_output": tool_output
        }


agent_engine_instance = AgentEngine()
