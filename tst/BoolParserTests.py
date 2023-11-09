import unittest
from src.implementation.boolParser import BoolParser
from src.implementation.io_handlers import IOWebMocker
class PetriNetNodeTests(unittest.TestCase):

    def test_raises_for_invalid_syntax(self):
        BoolParser.set_valid_extra_tokens(valid_input_tokens=['i1'])
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
        BoolParser.set_valid_extra_tokens(['i1'])
        f = BoolParser("i1").generate_function()
        self.assertEqual(f(i1=True),True)
        self.assertEqual(f(i1=False),False)

        digital_inputs={
            'i0':True,
            "i1":True,
            "i2":False,
            "i3":True,
            "i4":False
        }
        BoolParser.set_valid_extra_tokens(valid_input_tokens=list(digital_inputs.keys()),valid_place_tokens=["P0"])
        self.assertEqual(BoolParser("!(i0)").generate_function()(**digital_inputs),                 False)
        self.assertEqual(BoolParser("!(i2)",).generate_function()(**digital_inputs),                True)
        self.assertEqual(BoolParser("i0 ^ i1 ").generate_function()(**digital_inputs),              False)
        self.assertEqual(BoolParser("i2 ^ i4 ").generate_function()(**digital_inputs),              False)
        self.assertEqual(BoolParser("i0 ^ i4 ").generate_function()(**digital_inputs),              True)
        self.assertEqual(BoolParser("i4 ^ i0 ").generate_function()(**digital_inputs),              True)
        self.assertEqual(BoolParser("true ^ true").generate_function()(**digital_inputs),           False)
        self.assertEqual(BoolParser("false ^ false").generate_function()(**digital_inputs),         False)
        self.assertEqual(BoolParser("true ^ false").generate_function()(**digital_inputs),          True)
        self.assertEqual(BoolParser("!true | !false").generate_function()(**digital_inputs),        True)
        self.assertEqual(BoolParser("!true & !false").generate_function()(**digital_inputs),        False)
        self.assertEqual(BoolParser("true & false | false").generate_function()(**digital_inputs),  False)
        self.assertEqual(BoolParser("false | true & false").generate_function()(**digital_inputs),  False)
        self.assertEqual(BoolParser("(!false) ^ (!true)").generate_function()(**digital_inputs),    True)
        self.assertEqual(BoolParser("P0").generate_function()(P0=1),    True)

