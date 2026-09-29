"""guard.py 훅 테스트 8개 (harness/verification.md 2절)."""
import json
import os
import shutil
import sys
import tempfile
import unittest

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(os.path.dirname(HERE), "scripts"))
import guard  # noqa: E402


class TestGuard(unittest.TestCase):
    def setUp(self):
        self.repo = tempfile.mkdtemp()
        run = os.path.join(self.repo, "runs", "us2")
        os.makedirs(run)
        json.dump({"us": 2, "stage": "S2"}, open(os.path.join(run, "state.json"), "w"))

    def tearDown(self):
        shutil.rmtree(self.repo)

    def w(self, rel, tool="Write"):
        return guard.decide({"tool_name": tool, "tool_input": {"file_path": os.path.join(self.repo, rel)}}, self.repo)[0]

    def bash(self, cmd):
        return guard.decide({"tool_name": "Bash", "tool_input": {"command": cmd}}, self.repo)[0]

    def test_1_write_current_stage(self):
        self.assertTrue(self.w("runs/us2/s2-spec/screen-01.md"))

    def test_2_read_allowed(self):
        self.assertTrue(guard.decide({"tool_name": "Read", "tool_input": {"file_path": os.path.join(self.repo, "harness/rules.json")}}, self.repo)[0])

    def test_3_judge_allowed(self):
        self.assertTrue(self.bash("python3 scripts/judge.py us2 G2"))

    def test_4_other_stage_blocked(self):
        self.assertFalse(self.w("runs/us2/s4-design/figma-snapshot.json"))

    def test_5_approval_write_blocked(self):
        self.assertFalse(self.w("runs/us2/s3-keyscreen/approval.json"))

    def test_6_rules_edit_blocked(self):
        self.assertFalse(self.w("harness/rules.json", tool="Edit"))

    def test_7_docs_write_blocked(self):
        self.assertFalse(self.w("docs/DESIGN.md"))

    def test_8_bash_approval_blocked(self):
        self.assertFalse(self.bash("echo '{\"status\":\"approved\"}' > runs/us2/s3-keyscreen/approval.json"))
        self.assertFalse(self.bash("python3 scripts/approve.py us2"))


if __name__ == "__main__":
    unittest.main()
