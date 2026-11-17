"""Acceptance regressions added by the maintainer's independent review."""
import importlib.util,unittest
from pathlib import Path
spec=importlib.util.spec_from_file_location('comparator',Path(__file__).resolve().parents[1]/'tools/compare.py')
c=importlib.util.module_from_spec(spec);spec.loader.exec_module(c)
class ReviewChecks(unittest.TestCase):
    def test_empty_reference_is_not_a_numeric_regression(self):
        report=c.compare({'valid':True,'metrics':{},'labels':{}},{'metrics':{},'labels':{}})
        self.assertFalse(report['passed'])
    def test_unrepresentable_number_fails_without_crash(self):
        reference={"metrics":{"x":{"value":1,"rtol":0,"atol":0}},"labels":{}}
        self.assertFalse(c.compare({"valid":True,"metrics":{"x":10**1000},"labels":{}},reference)["passed"])
    def test_label_boolean_is_not_integer(self):
        actual={'valid':True,'metrics':{'x':1},'labels':{'converged':1}}
        reference={'metrics':{'x':{'value':1,'rtol':0,'atol':0}},'labels':{'converged':True}}
        self.assertFalse(c.compare(actual,reference)['passed'])
if __name__=='__main__':unittest.main()
