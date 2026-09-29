"""judge.py 샘플 테스트 (harness/verification.md 1절).

  python3 -m unittest discover -s tests
"""
import json
import os
import shutil
import sys
import tempfile
import unittest

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(HERE)
sys.path.insert(0, os.path.join(REPO, "scripts"))
import judge  # noqa: E402

FIXTURES = os.path.join(HERE, "fixtures")
RULES = judge.load_json(judge.DEFAULT_RULES)


def run_fixture(path):
    meta = judge.load_json(os.path.join(path, "meta.json"))
    tmp = tempfile.mkdtemp()
    try:
        shutil.copytree(os.path.join(path, "runs"), os.path.join(tmp, "runs"))
        return judge.run_gate(tmp, meta["us"], meta["gate"], RULES)
    finally:
        shutil.rmtree(tmp)


class TestFixtures(unittest.TestCase):
    def test_every_check_has_fixtures(self):
        ids = [c["id"] for g in RULES["gates"].values() for c in g["checks"]]
        self.assertEqual(len(ids), 28)
        for cid in ids:
            self.assertTrue(os.path.isdir(os.path.join(FIXTURES, cid, "pass")), cid)

    def test_fixture_count(self):
        n = sum(len([d for d in os.listdir(os.path.join(FIXTURES, c)) if d.startswith(("pass", "fail"))])
                for c in os.listdir(FIXTURES))
        self.assertEqual(n, 62)

    def test_pass_and_fail(self):
        for cid in sorted(os.listdir(FIXTURES)):
            for case in sorted(os.listdir(os.path.join(FIXTURES, cid))):
                with self.subTest(check=cid, case=case):
                    res = run_fixture(os.path.join(FIXTURES, cid, case))
                    ids = [v["rule_id"] for v in res["violations"]]
                    if case == "pass":
                        self.assertEqual(res["count"], 0, json.dumps(res["violations"], ensure_ascii=False))
                        self.assertEqual(res["result"], "pass")
                    else:
                        self.assertIn(cid, ids, json.dumps(res["violations"], ensure_ascii=False))


class TestState(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.mkdtemp()

    def tearDown(self):
        shutil.rmtree(self.tmp)

    def _copy(self, fixture):
        run = os.path.join(self.tmp, "runs", "us2")
        shutil.copytree(os.path.join(FIXTURES, fixture, "runs", "us2"), run)
        return run

    def _state(self, run, **kw):
        st = {"us": 2, "stage": "S1", "retry": {}, "s4_retry": {}, "last_gate": None}
        st.update(kw)
        judge.save_state(run, st)

    def test_g1_pass_advances(self):
        run = self._copy("G1-01/pass")
        self._state(run, stage="S1")
        self.assertEqual(judge.run_gate(self.tmp, 2, "G1", RULES)["next_stage"], "S2")

    def test_g1_blocks_after_retries(self):
        run = self._copy("G1-01/fail")
        self._state(run, stage="S1")
        stages = [judge.run_gate(self.tmp, 2, "G1", RULES)["next_stage"] for _ in range(3)]
        self.assertEqual(stages, ["S1", "S1", "blocked"])

    def test_g3_waiting_without_approval(self):
        run = self._copy("G3-01/pass")
        os.remove(os.path.join(run, "s3-keyscreen", "approval.json"))
        self._state(run, stage="S3")
        res = judge.run_gate(self.tmp, 2, "G3", RULES)
        self.assertEqual((res["result"], res["next_stage"]), ("waiting", "S3"))

    def test_g3_reject_goes_back(self):
        run = self._copy("G3-01/pass")
        ap = os.path.join(run, "s3-keyscreen", "approval.json")
        json.dump({"us": 2, "status": "rejected", "reason": "x", "reason_type": "reference", "date": "d"}, open(ap, "w"))
        self._state(run, stage="S3")
        res = judge.run_gate(self.tmp, 2, "G3", RULES)
        self.assertEqual(res["next_stage"], "S1")
        self.assertFalse(os.path.exists(ap))
        self.assertTrue(os.path.exists(os.path.join(run, "s3-keyscreen", "approval-rejected-1.json")))

    def test_g4_blocks_same_rule_three_times(self):
        run = self._copy("G4-02/fail")
        self._state(run, stage="S4")
        stages = [judge.run_gate(self.tmp, 2, "G4", RULES)["next_stage"] for _ in range(3)]
        self.assertEqual(stages, ["S4", "S4", "blocked"])

    def test_g4_pass_done_and_report(self):
        run = self._copy("G4-01/pass")
        self._state(run, stage="S4")
        self.assertEqual(judge.run_gate(self.tmp, 2, "G4", RULES)["next_stage"], "done")
        rep = judge.load_json(os.path.join(run, "s4-design", "report.json"))
        self.assertEqual(rep["count"], 0)

    def test_wrong_stage_is_error(self):
        run = self._copy("G4-01/pass")
        self._state(run, stage="S2")
        with self.assertRaises(judge.InputError):
            judge.run_gate(self.tmp, 2, "G4", RULES)

    def test_schema_error(self):
        run = self._copy("G4-01/pass")
        json.dump({"pages": [{"page": "99_Other", "frames": []}]},
                  open(os.path.join(run, "s4-design", "figma-snapshot.json"), "w"))
        with self.assertRaises(judge.InputError):
            judge.run_gate(self.tmp, 2, "G4", RULES)


if __name__ == "__main__":
    unittest.main()
