import unittest
from src.implementation.boolParser import BoolParser
from src.implementation.io_handlers import IOWebMocker
class PetriNetNodeTests(unittest.TestCase):

    def test_raises_for_invalid_syntax(self):
        BoolParser.set_valid_extra_tokens(valid_input_tokens=['di1'])
        self.assertRaises(SyntaxError,BoolParser,"")
        self.assertRaises(SyntaxError,BoolParser,"|")
        self.assertRaises(SyntaxError,BoolParser,"&")
        self.assertRaises(SyntaxError,BoolParser,"!")
        self.assertRaises(SyntaxError,BoolParser,"^")
        self.assertRaises(SyntaxError,BoolParser,"true true")
        self.assertRaises(SyntaxError,BoolParser,"^true")
        self.assertRaises(SyntaxError,BoolParser,"[]")
        self.assertRaises(SyntaxError,BoolParser,"()")
        self.assertRaises(SyntaxError,BoolParser,"ii")


    def test_returns_the_expected_value(self):
        BoolParser.set_valid_extra_tokens(['di1'])
        f = BoolParser("di1").generate_function()
        self.assertEqual(f(di1=True),True)
        self.assertEqual(f(di1=False),False)

        digital_inputs={
            'di0':True,
            "di1":True,
            "di2":False,
            "di3":True,
            "di4":False
        }
        BoolParser.set_valid_extra_tokens(valid_input_tokens=list(digital_inputs.keys()),valid_place_tokens=["P0"])
        self.assertEqual(BoolParser("!(di0)").generate_function()(**digital_inputs),                 False)
        self.assertEqual(BoolParser("!(di2)",).generate_function()(**digital_inputs),                True)
        self.assertEqual(BoolParser("di0 ^ di1 ").generate_function()(**digital_inputs),              False)
        self.assertEqual(BoolParser("di2 ^ di4 ").generate_function()(**digital_inputs),              False)
        self.assertEqual(BoolParser("di0 ^ di4 ").generate_function()(**digital_inputs),              True)
        self.assertEqual(BoolParser("di4 ^ di0 ").generate_function()(**digital_inputs),              True)
        self.assertEqual(BoolParser("true ^ true").generate_function()(**digital_inputs),           False)
        self.assertEqual(BoolParser("false ^ false").generate_function()(**digital_inputs),         False)
        self.assertEqual(BoolParser("true ^ false").generate_function()(**digital_inputs),          True)
        self.assertEqual(BoolParser("!true | !false").generate_function()(**digital_inputs),        True)
        self.assertEqual(BoolParser("!true & !false").generate_function()(**digital_inputs),        False)
        self.assertEqual(BoolParser("true & false | false").generate_function()(**digital_inputs),  False)
        self.assertEqual(BoolParser("false | true & false").generate_function()(**digital_inputs),  False)
        self.assertEqual(BoolParser("(!false) ^ (!true)").generate_function()(**digital_inputs),    True)
        self.assertEqual(BoolParser("P0").generate_function()(P0=1),    True)

