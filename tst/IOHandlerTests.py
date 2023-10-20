import unittest

from src.abstract.abstract_io_handler import AbstractIOHandler
from src.implementation.io_handlers import IOWebMocker

class IOHandlerTests(unittest.TestCase):
    def setUp(self) -> None:
        self.io_handler = IOWebMocker(
            digital_inputs= {f"i{i}":False for i in range(8)},
            digital_outputs={f"o{i}":False for i in range(8)}
        )       
        return super().setUp()
    def test_instantiation(self):
        self.assertIsInstance(self.io_handler,AbstractIOHandler)
    
    def test_has_been_updated_property(self):
        self.assertFalse(self.io_handler.has_been_updated)
        self.io_handler._digital_inputs["i0"] = True
        self.assertTrue(self.io_handler.has_been_updated)
        self.assertFalse(self.io_handler.has_been_updated)

    