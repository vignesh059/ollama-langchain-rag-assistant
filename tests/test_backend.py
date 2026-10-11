"""
Comprehensive backend test suite for Chatbot backend components.
"""

import os
import sys
import unittest

# Ensure root dir is in path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from backend.tools.attendance_tool import calculate_attendance_tool, compute_attendance_stats
from backend.tools.wikipedia_tool import wikipedia_search_tool
from backend.rag_engine import RAGEngine
from backend.memory_engine import MemoryEngine
from backend.agent_engine import agent_engine_instance


class TestBackend(unittest.TestCase):

    def test_attendance_tool_eligible(self):
        stats = compute_attendance_stats(18, 24, 75.0)
        self.assertEqual(stats["current_percentage"], 75.0)
        self.assertTrue(stats["is_eligible"])
        self.assertEqual(stats["status"], "ELIGIBLE")
        self.assertEqual(stats["needed_classes_to_reach_target"], 0)

    def test_attendance_tool_shortage(self):
        stats = compute_attendance_stats(15, 24, 75.0)
        self.assertEqual(stats["current_percentage"], 62.5)
        self.assertFalse(stats["is_eligible"])
        self.assertEqual(stats["status"], "SHORTAGE")
        self.assertEqual(stats["needed_classes_to_reach_target"], 12)

    def test_wikipedia_tool(self):
        res = wikipedia_search_tool.invoke({"query": "Machine learning"})
        self.assertIn("Wikipedia", res)
        self.assertIn("Summary", res)

    def test_memory_engine(self):
        mem = MemoryEngine()
        mem.add_user_message("Hello AI")
        mem.add_ai_message("Hello User!")
        history = mem.get_formatted_history()
        self.assertIn("User: Hello AI", history)
        self.assertIn("Assistant: Hello User!", history)

    def test_agent_intent_detection(self):
        # Attendance intent
        tool_name, tool_out = agent_engine_instance.detect_intent_and_execute_tool("I present 18 classes out of 24")
        self.assertEqual(tool_name, "Attendance Calculator")
        self.assertIn("75.0%", tool_out)

        # Wikipedia intent
        tool_name_w, tool_out_w = agent_engine_instance.detect_intent_and_execute_tool("search wikipedia for Artificial Intelligence")
        self.assertEqual(tool_name_w, "Wikipedia Search")
        self.assertIn("Wikipedia", tool_out_w)


if __name__ == "__main__":
    unittest.main()
