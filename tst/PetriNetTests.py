import unittest

from src.implementation.petri_net_subcomponents import *
from src.implementation.petri_net_handler import PetriNetHandler, AbstractPetriNetHandler
from src.implementation.io_handlers import IOWebMocker
from src.implementation.boolParser import BoolParser
from collections.abc import Collection
from tst.futils import hasmethod


class PetriNetNodeTests(unittest.TestCase):
    def setUp(self) -> None:
        self.instances = [PetriNetNode("some id")]
        return super().setUp()
    def test_instantiation(self):
        for instance in  self.instances:
            self.assertIsInstance(instance,AbstractPetriNetNode)

    def test_has_all_required_properties(self):
        for instance in self.instances:
            self.assertTrue(hasattr(instance,'arcs_from_this_node'))
            self.assertTrue(hasattr(instance,'arcs_to_this_node'))

    
    def test_all_properties_have_the_correct_type(self):
        for instance in self.instances:
            self.assertIsInstance(instance.arcs_from_this_node,Collection)
            self.assertIsInstance(instance.arcs_to_this_node,Collection)


    def test_all_collection_properties_are_initialized_with_len_zero(self):
        new_instance = PetriNetNode("some id")
        arcs_from_this_node = new_instance.arcs_from_this_node
        arcs_to_this_node = new_instance.arcs_to_this_node
        self.assertEqual(len(arcs_from_this_node),0)
        self.assertEqual(len(arcs_to_this_node),0)
    

    def test_has_all_required_methods(self):
        new_instance = PetriNetNode("some id")
        self.assertTrue(hasmethod(new_instance,'add_arc_from_this_node'))
        self.assertTrue(hasmethod(new_instance,'add_arc_to_this_node'))
    
    def test_add_arc_methods(self):
        for instance in self.instances:
            dummy_arc1 = "dummy arc1"
            dummy_arc2 = "dummy arc2"

            ideal_iterable_arcs_from_this_node = [_ for _ in instance.arcs_from_this_node]+[dummy_arc1]
            ideal_iterable_arcs_to_this_node = [_ for _ in instance.arcs_to_this_node]+[dummy_arc2]
            instance.add_arc_from_this_node(dummy_arc1)
            instance.add_arc_to_this_node(dummy_arc2)
            self.assertCountEqual(ideal_iterable_arcs_from_this_node,instance.arcs_from_this_node)
            self.assertCountEqual(ideal_iterable_arcs_to_this_node,instance.arcs_to_this_node)


class ArcTests(unittest.TestCase):
    def setUp(self) -> None:
        Node1 = PetriNetNode("node 1")
        Node2 = PetriNetNode("node 2")
        self.instances = [Arc("some id",source_node=Node1,target_node=Node2,weight=1,is_inhibitor=False)]
        return super().setUp()
    
    def test_instantiation(self):
        for instance in  self.instances:
            self.assertIsInstance(instance,AbstractPetriNetArc)
    
    def test_has_all_required_properties(self):
        for instance in self.instances:
            self.assertTrue(hasattr(instance,'source_node'))
            self.assertTrue(hasattr(instance,'target_node'))
            self.assertTrue(hasattr(instance,'weight'))
            self.assertTrue(hasattr(instance,'is_inhibitor'))

    def test_all_properties_have_the_correct_type(self):
        for instance in self.instances:
            self.assertIsInstance(instance.source_node,AbstractPetriNetNode)
            self.assertIsInstance(instance.target_node,AbstractPetriNetNode)
            self.assertIsInstance(instance.weight,int)

    def test_arc_connectiong_two_places_or_two_transitions_raises_exception(self):
        T0 = BaseTransition("T0",rate=1,priority=1)
        T1 = BaseTransition("T1",rate=1,priority=1)
        self.assertRaises(TypeError,Arc,id="arc0",source_node=T0,target_node=T1,weight=1)
        P0 = Place("P0",capacity=2,marking=1)
        P1 = Place("P1",capacity=2,marking=1)
        self.assertRaises(TypeError,Arc,id="arc1",source_node=P0,target_node=P1,weight=1)
    
    def test_arc_add_itself_to_its_nodes_arcs_list(self):
        T0 = BaseTransition("T0",rate=1,priority=1)
        P0 = Place("P0",capacity=2,marking=1)
        arc0 = Arc("arc0",source_node=T0,target_node=P0,weight=2,is_inhibitor=False)
        self.assertIn(arc0,T0.arcs_from_this_node)
        self.assertIn(arc0,P0.arcs_to_this_node)

        arc1 = Arc("arc1",source_node=P0,target_node=T0,weight=2,is_inhibitor=False)
        self.assertIn(arc1,P0.arcs_from_this_node)
        self.assertIn(arc1,T0.arcs_to_this_node)
        

class PlaceTests(unittest.TestCase):
    def setUp(self):
        self.instances = [Place(id = "P0",capacity = 10, marking = 9)]
    
    def test_instantiation(self):
        for instance in  self.instances:
            self.assertIsInstance(instance,AbstractPetriNetPlace)
    
    def test_marking_greater_than_capacity_raises_exception(self):
        self.assertRaises(ValueError, Place,id = "P1",capacity = 10, marking = 11)
        place = Place(id = "P2",capacity=7,marking = 3)
        self.assertRaises(ValueError, place.__setattr__,"marking",8)
    
    def test_has_all_required_properties(self):
        for instance in self.instances:
            self.assertTrue(hasattr(instance,'capacity'),"instance has no attribute 'capacity'")
            self.assertTrue(hasattr(instance,'marking'), "instance has no attribute 'marking'")
            self.assertTrue(hasattr(instance,'initial_marking'), "instance has no attribute 'initial_marking'")
    
    def test_all_properties_have_the_correct_type(self):
        for instance in self.instances:
            self.assertIsInstance(instance.capacity,int)
            self.assertIsInstance(instance.marking,int)
            self.assertIsInstance(instance.initial_marking,int)

class BaseTransitionTests(unittest.TestCase):
    def setUp(self):
        self.instances = [BaseTransition(id="T0",priority=1,rate=1)]
    
    def test_instantiation(self):
        for instance in  self.instances:
            self.assertIsInstance(instance,AbstractPetriNetTransition)

    def test_has_all_required_properties(self):
            for instance in self.instances:
                self.assertTrue(hasattr(instance,'rate'),"instance has no attribute 'rate'")
                self.assertTrue(hasattr(instance,'priority'), "instance has no attribute 'priority'")

    def test_all_properties_have_the_correct_type(self):
        for instance in self.instances:
            self.assertIsInstance(instance.rate,int|float)
            self.assertIsInstance(instance.priority,int)
    
    def test_transition_enabled_only_if_all_preplaces_have_atleast_the_required_amount_of_tokens(self):
        transition = BaseTransition("T0",rate=1,priority=1)
        preplaces = [
            Place("P0",capacity=5,marking=3),
            Place("P1",capacity=3,marking=3),
            Place("P2",capacity=3,marking=2)
        ]
        arcs = [Arc("some_id",source_node=preplace,target_node=transition,weight=2,is_inhibitor=False)
                for preplace in preplaces]
        self.assertTrue(transition.is_petri_enabled())
        arcs.append(Arc(
            "some_id",
            source_node=Place(
                "P4",
                capacity=3,
                marking=1
            ),
            weight=2,
            is_inhibitor=False,
            target_node=transition
        ))

        self.assertFalse(transition.is_petri_enabled())

    def test_transition_enabled_only_if_all_postplaces_have_the_necessary_capacity_left(self):
        transition = BaseTransition("T0",rate=1,priority=1)
        postplaces = [
            Place("P0",capacity=5,marking=3),
            Place("P1",capacity=3,marking=1),
            Place("P2",capacity=4,marking=2)
        ]
        arcs = [Arc("some_id",source_node=transition,target_node=postplace,weight=2,is_inhibitor=False)
                for postplace in postplaces]
        self.assertTrue(transition.is_petri_enabled())
        
        arcs.append(Arc(
            "some_id",
            source_node=transition,
            target_node=Place(
                "P4",
                capacity=2,
                marking=1
            ),
            weight=2,
            is_inhibitor=False
        ))

        self.assertFalse(transition.is_petri_enabled())

    def test_firing_decreases_preplaces_marking(self):
        transition = BaseTransition("T0",rate=1,priority=1)
        preplaces = [
            Place("P0",capacity=5,marking=3),
            Place("P1",capacity=3,marking=3),
            Place("P2",capacity=3,marking=2)
        ]
        arcs = [Arc("some_id",source_node=preplace,target_node=transition,weight=2,is_inhibitor=False)
                for preplace in preplaces]
        
        self.assertTrue(transition.is_petri_enabled())

        self.assertTrue(transition.is_signal_enabled())
        transition.fire()
        self.assertEqual(preplaces[0].marking, preplaces[0].initial_marking - arcs[0].weight)
        self.assertEqual(preplaces[1].marking, preplaces[1].initial_marking - arcs[1].weight)
        self.assertEqual(preplaces[2].marking, preplaces[2].initial_marking - arcs[2].weight)
    
    def test_firing_increases_postplaces_marking(self):
        transition = BaseTransition("T0",rate=1,priority=1)
        postplaces = [
            Place("P0",capacity=5,marking=3),
            Place("P1",capacity=3,marking=1),
            Place("P2",capacity=4,marking=2)
        ]
        arcs = [Arc("some_id",source_node=transition,target_node=postplace,weight=2,is_inhibitor=False)
                for postplace in postplaces]
        self.assertTrue(transition.is_petri_enabled())
        self.assertTrue(transition.is_signal_enabled())
        transition.fire()

        self.assertEqual(postplaces[0].marking, postplaces[0].initial_marking + arcs[0].weight)
        self.assertEqual(postplaces[1].marking, postplaces[1].initial_marking + arcs[1].weight)
        self.assertEqual(postplaces[2].marking, postplaces[2].initial_marking + arcs[2].weight)

class TimedTransitionTests(unittest.TestCase):
    def setUp(self):        
        self.instances = [
            TimedTransition(id="T0", priority=1, rate=1, timer_sec=3),
        ]
    
    def test_instantiation(self):
        for instance in  self.instances:
            self.assertIsInstance(instance,AbstractPetriNetTimedTransition)
    
    def test_is_time_enabled_only_after_timer_sec(self):    
        transition = TimedTransition(id="T0", priority=1, rate=1, timer_sec=0.03)
        self.assertTrue(transition.is_petri_enabled())
        self.assertTrue(transition.is_signal_enabled())
        self.assertFalse(transition.is_time_enabled())
        time.sleep(0.02)
        self.assertFalse(transition.is_time_enabled())
        time.sleep(0.011)
        self.assertTrue(transition.is_time_enabled())

    def test_is_time_enabled_timer_resets_after_signal_disabling(self):
        io_handler =IOWebMocker(digital_inputs={"i0":False})
        transition = TimedTransition(id="T0", priority=1, rate=1, timer_sec=0.03,
                                     signal_enabling_expression="i0",
                                     io_handler=io_handler,
                                     BoolParserClass=BoolParser)
        self.assertTrue(transition.is_petri_enabled())
        self.assertFalse(transition.is_signal_enabled())
        io_handler._digital_inputs["i0"] = True
        self.assertTrue(transition.is_signal_enabled())
        self.assertFalse(transition.is_time_enabled())
        time.sleep(0.031)
        self.assertTrue(transition.is_time_enabled())
        io_handler._digital_inputs["i0"] = False
        self.assertFalse(transition.is_signal_enabled())
        self.assertFalse(transition.is_time_enabled())

        io_handler._digital_inputs["i0"] = True
        self.assertTrue(transition.is_signal_enabled())
        self.assertFalse(transition.is_time_enabled())
        time.sleep(0.015)

        io_handler._digital_inputs["i0"] = False
        self.assertFalse(transition.is_signal_enabled())
        self.assertFalse(transition.is_time_enabled())

        io_handler._digital_inputs["i0"] = True
        self.assertTrue(transition.is_signal_enabled())
        self.assertFalse(transition.is_time_enabled())
        time.sleep(0.025)
        self.assertFalse(transition.is_time_enabled())

        
    def test_is_time_enabled_timer_resets_after_petri_disabling(self):
        transition = TimedTransition(id="T0", priority=1, rate=1, timer_sec=0.03)                             
        preplace = Place("P0",capacity=5,marking=2)
        Arc("arc1",source_node=preplace,target_node=transition,weight=2,is_inhibitor=False)
        self.assertTrue(transition.is_petri_enabled())
        self.assertTrue(transition.is_signal_enabled())

        self.assertFalse(transition.is_time_enabled())
        time.sleep(0.031)
        self.assertTrue(transition.is_time_enabled())

        preplace.marking = 0
        self.assertFalse(transition.is_petri_enabled())
        self.assertFalse(transition.is_time_enabled())
        preplace.marking = 2
        self.assertTrue(transition.is_petri_enabled())
        self.assertFalse(transition.is_time_enabled())
        time.sleep(0.031)
        self.assertTrue(transition.is_time_enabled())

    def test_is_time_enabled_timer_reset_after_this_transition_is_fired(self):
        transition = TimedTransition(id="T0", priority=1, rate=1, timer_sec=0.03)                             
        preplace = Place("P0",capacity=5,marking=2)
        Arc("arc1",source_node=preplace,target_node=transition,weight=2,is_inhibitor=False)
        self.assertTrue(transition.is_petri_enabled())
        self.assertTrue(transition.is_signal_enabled())

        self.assertFalse(transition.is_time_enabled())
        time.sleep(0.031)
        self.assertTrue(transition.is_time_enabled())
        transition.fire()
        self.assertFalse(transition.is_time_enabled())
        time.sleep(0.031)
        self.assertTrue(transition.is_time_enabled())
        

class TransitionsCollectionTests(unittest.TestCase):
    def setUp(self):
        self.io_handler =IOWebMocker(digital_inputs={"i0":False})
    
    def test_instantiation(self):
        transitions_collection = TransitionsCollection(io_handler=self.io_handler,transitions=[])
        self.assertIsInstance(transitions_collection,AbstractPetriNetTransitionsCollection)
    
    def test_get_transition_chosen_to_fire_raises_if_deadlock(self):
        #preplace preventing transition enabling
        p0 = Place("P0",capacity=1,marking=0)
        t0 = InstantaneousTransition("T0",rate=1,priority=1)
        Arc("p0->t0",p0,t0,1,is_inhibitor=False)
        transitions_collection = TransitionsCollection(transitions=[t0],io_handler=self.io_handler)
        self.assertRaises(PetriNetDeadlockError,transitions_collection.get_transition_chosen_to_fire)

        #postplace preventing transition enabling
        t0 = InstantaneousTransition("T0",rate=1,priority=1)
        p0 = Place("P0",capacity=1,marking=0)
        Arc("t0->p0",p0,t0,2,is_inhibitor=False)
        transitions_collection = TransitionsCollection(transitions=[t0],io_handler=self.io_handler)
        self.assertRaises(PetriNetDeadlockError,transitions_collection.get_transition_chosen_to_fire)

    def test_get_transition_chosen_to_fire_always_chooses_a_transition_with_highest_priority(self):
        p0 = Place("P0",capacity=1,marking=1)
        t0 = InstantaneousTransition("T0",rate=1,priority=1)
        t1 = InstantaneousTransition("T1",rate=1,priority=2)
        t2 = InstantaneousTransition("T2",rate=1,priority=3)
        Arc("p0->t0",p0,t0,1,is_inhibitor=False)
        Arc("p0->t1",p0,t1,1,is_inhibitor=False)
        Arc("p0->t2",p0,t2,1,is_inhibitor=False)
        transitions_collection = TransitionsCollection(transitions=[t0,t1,t2],io_handler=self.io_handler)
        for _ in range(5):
            chosen = transitions_collection.get_transition_chosen_to_fire()
            self.assertIs(t2,chosen)
    
    def test_get_transition_chosen_to_fire_chooses_probabilistically_with_a_distribution_based_on_transition_rates(self):
        p0 = Place("P0",capacity=1,marking=1)
        t0 = InstantaneousTransition("T0",rate=1,priority=1)
        t1 = InstantaneousTransition("T1",rate=2,priority=1)
        t2 = InstantaneousTransition("T2",rate=7,priority=1)
        Arc("p0->t0",p0,t0,1,is_inhibitor=False)
        Arc("p0->t1",p0,t1,1,is_inhibitor=False)
        Arc("p0->t2",p0,t2,1,is_inhibitor=False)
        transitions_collection = TransitionsCollection(transitions=[t0,t1,t2],io_handler=self.io_handler)
        counters = {t0.id:0,t1.id:0,t2.id:0}

        TOTAL_NUMBER_OF_SELECTIONS = 100000
        for i in range(TOTAL_NUMBER_OF_SELECTIONS):
            counters[transitions_collection.get_transition_chosen_to_fire().id] += 1
        
        self.assertAlmostEqual(
            counters[t0.id]/TOTAL_NUMBER_OF_SELECTIONS, #real value
            t0.rate/(t0.rate+t1.rate+t2.rate), #expected value
            delta=0.03*t0.rate/(t0.rate+t1.rate+t2.rate) # delta tolerance, 
        )
        self.assertAlmostEqual(
            counters[t1.id]/TOTAL_NUMBER_OF_SELECTIONS,
            t1.rate/(t0.rate+t1.rate+t2.rate),
            delta=0.03 *  t1.rate/(t0.rate+t1.rate+t2.rate)
        )
        self.assertAlmostEqual(
            counters[t2.id]/TOTAL_NUMBER_OF_SELECTIONS,
            t2.rate/(t0.rate+t1.rate+t2.rate),
            delta=0.03 * t2.rate/(t0.rate+t1.rate+t2.rate)
        )


    def test_get_transition_chosen_to_fire_instantaneous_transitions_has_total_preference_over_timed_transitions(self):
        p0 = Place("P0",capacity=1,marking=1)
        self.io_handler =IOWebMocker(digital_inputs={"i0":False})
        instantaneous_transition = InstantaneousTransition("t0",rate=1,priority=2,
                                                           signal_enabling_expression="i0",
                                                           io_handler=self.io_handler,
                                                           BoolParserClass= BoolParser)
        timed_transition = TimedTransition("t1",rate=1,priority=1,timer_sec=0.03)
        Arc("arc0",p0,instantaneous_transition,1,is_inhibitor=False)
        Arc("arc1",p0,timed_transition,1,is_inhibitor=False)
        transitions_collection = TransitionsCollection(
            transitions=[timed_transition,instantaneous_transition],
            io_handler=self.io_handler
        )

    
        self.assertTrue(instantaneous_transition.is_petri_enabled())
        self.assertFalse(instantaneous_transition.is_signal_enabled())

        self.assertTrue(timed_transition.is_petri_enabled())
        self.assertTrue(timed_transition.is_signal_enabled())
        self.assertFalse(timed_transition.is_time_enabled())
        time.sleep(0.041)
        self.assertTrue(timed_transition.is_time_enabled())
        # even though Time transition is fully enabled (petri,signal and time), it wont be selected,
        # because there is some instantaneous transition petri enabled
        
        self.assertIs(transitions_collection.get_transition_chosen_to_fire(),None)
        self.io_handler._digital_inputs["i0"] = True
        self.assertTrue(instantaneous_transition.is_signal_enabled())
        self.assertIs(transitions_collection.get_transition_chosen_to_fire(),instantaneous_transition)


class PetriNetTests(unittest.TestCase):
    
    def setUp(self) -> None:

        self.mock_callback = lambda x:None
        return super().setUp()

    def test_instantiation(self):
        self.petri_net_handler = PetriNetHandler(
            IOWebMocker(digital_inputs={"i0":False},digital_outputs={'o0':False}),
            BoolParser)
        

        self.assertIsInstance(self.petri_net_handler,AbstractPetriNetHandler)
       
    def test_output_update(self):
        petri_net_json_structure = {
            'places':[
                {
                    'id':'P0',
                    'capacity':3,
                    'initial_marking':1
                }
            ],
            'instantaneous_transitions':[
                {
                    'id':'T0',
                    'rate':1,   
                    'priority':0,
                    'signal_enabling_expression':'true'
                }
            ],
            'timed_transitions':[],
            'arcs':[
                {'id':'p0->t0',
                 'source':'P0',
                 'target':"T0",
                 'weight':1,
                 "type":"normal"
                }
            ],
            'marking_to_output_expressions':{
                'o0':'P0'
            }
        }
        io_handler = IOWebMocker(digital_inputs={"i0":False},digital_outputs={'o0':False})
        petri_net_handler = PetriNetHandler(
            io_handler,
            BoolParser
        )
        petri_net_handler.set_event_callback(self.mock_callback)
        petri_net_handler.setup(petri_net_json_structure)
        self.assertEqual(io_handler._digital_outputs['o0'],True)
        petri_net_handler._step()
        self.assertEqual(io_handler._digital_outputs['o0'],False)
    
    def test_timed_transitions_01(self):
        io_handler = IOWebMocker(digital_inputs={"i0":False,"i1":False},digital_outputs={'o0':False,'o1':False})
        petri_net_handler = PetriNetHandler(
            io_handler,
            BoolParser
        )
        petri_net_json_structure = {
            "places": [
                {
                "id": "P0",
                "initial_marking": 1,
                "capacity": 0
                },
                {
                "id": "P1",
                "initial_marking": 0,
                "capacity": 0
                }
            ],
            "instantaneous_transitions": [
                {
                "id": "T0",
                "rate": 1,
                "priority": 1,
                "signal_enabling_expression": "i0"
                }
            ],
            "timed_transitions": [
                {
                "id": "T1",
                "rate": 1,
                "priority": 1,
                "signal_enabling_expression": "i1",
                "timer_sec": 1
                }
            ],
            "arcs": [
                {
                "id": "P0 to T0",
                "source": "P0",
                "target": "T0",
                "weight": 1,
                "type":"normal"
                },
                {
                "id": "P1 to T1",
                "source": "P1",
                "target": "T1",
                "weight": 1,
                "type":"normal"
                },
                {
                "id": "T0 to P1",
                "source": "T0",
                "target": "P1",
                "weight": 1,
                "type":"normal"
                },
                {
                "id": "T1 to P0",
                "source": "T1",
                "target": "P0",
                "weight": 1,
                "type":"normal"
                }
            ],
            "marking_to_output_expressions": {
                "o0": "P0",
                "o1": "P1",
                "o2": "false",
                "o3": "false",
                "o4": "false",
                "o5": "false",
                "o6": "false",
                "o7": "false"
            }
        }
        
        petri_net_handler.setup(petri_net_json_structure)
        petri_net_handler.set_event_callback(self.mock_callback)

        markings = {place.id:place.marking for place in petri_net_handler._places.values()}
        self.assertEqual(markings,{"P0":1,"P1":0})
       
        petri_net_handler._step()
        markings = {place.id:place.marking for place in petri_net_handler._places.values()}
        self.assertEqual(markings,{"P0":1,"P1":0})


        io_handler._digital_inputs["i0"] = True
       

        petri_net_handler._step()
        markings = {place.id:place.marking for place in petri_net_handler._places.values()}
        self.assertEqual(markings,{"P0":0,"P1":1})

        
        io_handler._digital_inputs={"i0":False,"i1":True}
        petri_net_handler._step()
        markings = {place.id:place.marking for place in petri_net_handler._places.values()}
        self.assertEqual(markings,{"P0":0,"P1":1})
        time.sleep(0.6)
        
        
        petri_net_handler._step()
        markings = {place.id:place.marking for place in petri_net_handler._places.values()}
        self.assertEqual(markings,{"P0":0,"P1":1})

        
        io_handler._digital_inputs["i1"] = False
        petri_net_handler._step()
        markings = {place.id:place.marking for place in petri_net_handler._places.values()}
        self.assertEqual(markings,{"P0":0,"P1":1})

        io_handler._digital_inputs["i1"] = True
        petri_net_handler._step()
        markings = {place.id:place.marking for place in petri_net_handler._places.values()}
        self.assertEqual(markings,{"P0":0,"P1":1})
        time.sleep(0.6)

        petri_net_handler._step()
        markings = {place.id:place.marking for place in petri_net_handler._places.values()}
        self.assertEqual(markings,{"P0":0,"P1":1})
        
        time.sleep(0.3)
        petri_net_handler._step()
        markings = {place.id:place.marking for place in petri_net_handler._places.values()}
        self.assertEqual(markings,{"P0":0,"P1":1})
        
        time.sleep(0.15)
        petri_net_handler._step()
        
        markings = {place.id:place.marking for place in petri_net_handler._places.values()}
        self.assertEqual(markings,{"P0":1,"P1":0})

        