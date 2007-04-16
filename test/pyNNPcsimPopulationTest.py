"""
Unit tests for pyNN.pcsim package

    Unit tests for verifying the correctness of the high level population based 
    part of the pyNN interface.

    Dejan Pecevski, March, 2007
        dejan@igi.tugraz.at  

"""

import pyNN.common as common
import pyNN.random as random
from pyNN.pcsim import *
import unittest, sys, numpy
import numpy.random


class PopulationInitTest(unittest.TestCase):
    """Tests of the __init__() method of the Population class."""
    
    def setUp(self):
        setup()
        
    
    def tearDown(self):
        pass
        
    def testSimpleInit(self):
        """Population.__init__(): the cell list in hoc should have the same length as the population size."""
        popul = Population((3,3),IF_curr_alpha)
        self.assertEqual( len(popul), 9 )        
        
    
    def testInitWithParams(self):
        """Population.__init__(): Parameters set on creation should be the same as retrieved with HocToPy.get()"""
        popul = Population((3,3),IF_curr_alpha,{'tau_syn':3.141592654})
        tau_syn = pcsim_globals.net.object(popul.getObjectID(popul[2,2])).TauSyn 
        self.assertAlmostEqual(tau_syn, 3.141592654, places=5)
    
    def testInitWithLabel(self):
        """Population.__init__(): A label set on initialisation should be retrievable with the Population.label attribute."""
        popul = Population((3,3),IF_curr_alpha,label='iurghiushrg')
        assert popul.label == 'iurghiushrg'
    
#    def testInvalidCellType(self):
#        """Population.__init__(): Trying to create a cell type which is not a method of StandardCells should raise an AttributeError."""
#        self.assertRaises(AttributeError, neuron.Population, (3,3), 'qwerty', {})
        
    def testNonSquareDimensions(self):
        """Population.__init__(): At present all dimensions must be the same size."""
        """ PCSIM ALLOWS NON SQUARE DIMENSIONS """        
        #self.assertRaises(common.InvalidDimensionsError, neuron.Population, (3,2), neuron.IF_curr_alpha)
        pass

    def testInitWithNonStandardModel(self):
        """Population.__init__(): the cell list in hoc should have the same length as the population size."""
        popul = Population((3,3),'LifNeuron',{'Rm':5e6,'Vthresh':-0.055})
        popul2 = Population((3,3),LifNeuron,{'Rm':5e6,'Vthresh':-0.055}) # pcsim allows also specification of non-standard models as types
        self.assertEqual(len(popul), 9)
        self.assertEqual(len(popul2), 9)

 # ==============================================================================
class PopulationSetTest(unittest.TestCase):
         
     def setUp(self):
         setup()
         Population.nPop = 0
         self.popul1 = Population((3,3),IF_curr_alpha)
         self.popul2 = Population((5,),CbLifNeuron,{'Vinit':-0.070, 'Inoise':0.001})
     
     def testSetFromDict(self):
         """Population.set(): Parameters set in a dict should all be retrievable from PyPCSIM directly"""
         self.popul1.set({'tau_m':43.21})
         self.assertAlmostEqual( pcsim_globals.net.object(self.popul1.getObjectID(8)).taum, 43.21, places = 5)
#     
     def testSetFromPair(self):
        """Population.set(): A parameter set as a string,value pair should be retrievable using PyPCSIM directly"""
        self.popul1.set('tau_m',12.34)
        self.assertAlmostEqual( pcsim_globals.net.object(self.popul1.getObjectID(3)).taum, 12.34, places = 5)
     
     def testSetInvalidFromPair(self):
         """Population.set(): Trying to set an invalid value for a parameter should raise an exception."""
         self.assertRaises(common.InvalidParameterValueError, self.popul1.set, 'tau_m', [])
     
     def testSetInvalidFromDict(self):
         """Population.set(): When any of the parameters in a dict have invalid values, then an exception should be raised.
            There is no guarantee that the valid parameters will be set."""
         self.assertRaises(common.InvalidParameterValueError, self.popul1.set, {'v_thresh':'hello','tau_m':56.78})
     
     def testSetNonexistentFromPair(self):
         """Population.set(): Trying to set a nonexistent parameter should raise an exception."""
         self.assertRaises(common.NonExistentParameterError, self.popul1.set, 'tau_foo', 10.0)
     
     def testSetNonexistentFromDict(self):
         """Population.set(): When some of the parameters in a dict are inexistent, an exception should be raised.
            There is no guarantee that the existing parameters will be set."""
         self.assertRaises(common.NonExistentParameterError, self.popul1.set, {'tau_foo': 10.0, 'tau_m': 21.0})
     
     def testSetWithNonStandardModel(self):
         """Population.set(): Parameters set in a dict should all be retrievable using PyPCSIM interface directly"""
         self.popul2.set({'Rm':4.5e6})
         self.assertAlmostEqual( pcsim_globals.net.object(self.popul2.getObjectID(3)).Rm , 4.5e6, places = 10)
         
     def testTSet(self):
         """Population.tset(): The valueArray passed should be retrievable using the PyPCSIM interface """
         array_in = numpy.array([[0.1,0.2,0.3],[0.4,0.5,0.6],[0.7,0.8,0.9]])
         self.popul1.tset('i_offset', array_in)
         for i in 0,1,2:
             for j in 0,1,2:
                 self.assertAlmostEqual( array_in[i,j], pcsim_globals.net.object(self.popul1.getObjectID(self.popul1[i,j])).Iinject , places = 7 )
     
     def testTSetInvalidDimensions(self):
         """Population.tset(): If the size of the valueArray does not match that of the Population, should raise an InvalidDimensionsError."""
         array_in = numpy.array([[0.1,0.2,0.3],[0.4,0.5,0.6]])
         self.assertRaises(common.InvalidDimensionsError, self.popul1.tset, 'i_offset', array_in)
     
     def testTSetInvalidValues(self):
         """Population.tset(): If some of the values in the valueArray are invalid, should raise an exception."""
         array_in = numpy.array([[0.1,0.2,0.3],[0.4,0.5,0.6],[0.7,0.8,'apples']])
         self.assertRaises(common.InvalidParameterValueError, self.popul1.tset, 'i_offset', array_in)
         """Population.rset(): with native rng. This is difficult to test, so for now just require that all values retrieved should be different. Later, could calculate distribution and assert that the difference between sample and theoretical distribution is less than some threshold."""
         
     def testRSetNative(self):
         self.popul1.rset('tau_m',
                       random.RandomDistribution(rng=NativeRNG(),
                                                 distribution='Uniform',
                                                 parameters={'a':10.0, 'b':30.0}))
         self.assertNotEqual(pcsim_globals.net.object(self.popul1.getObjectID(3)).taum,
                             pcsim_globals.net.object(self.popul1.getObjectID(6)).taum)
         
     def testRSetNumpy(self):
          """Population.rset(): with numpy rng."""
          rd1 = random.RandomDistribution(rng=random.NumpyRNG(seed=98765),
                                           distribution='uniform',
                                           parameters=[0.9,1.1])
          rd2 = random.RandomDistribution(rng=random.NumpyRNG(seed=98765),
                                           distribution='uniform',
                                           parameters=[0.9,1.1])
          self.popul1.rset('cm',rd1)
          output_values = numpy.zeros((3,3),numpy.float)
          for i in 0,1,2:
              for j in 0,1,2:    
                  output_values[i,j] = pcsim_globals.net.object(self.popul1.getObjectID(self.popul1[i,j])).Cm
          input_values = rd2.next(9)
          output_values = output_values.reshape((9,))
          for i in range(9):
              self.assertAlmostEqual(input_values[i],output_values[i],places=5)
          
     def testRSetNative2(self):
          """Population.rset(): with native rng."""
          rd1 = random.RandomDistribution(rng=NativeRNG(seed=98765),
                                           distribution='Uniform',
                                           parameters=[0.9,1.1])
          rd2 = random.RandomDistribution(rng=NativeRNG(seed=98765),
                                           distribution='Uniform',
                                           parameters=[0.9,1.1])
          self.popul1.rset('cm', rd1)
          output_values_1 = numpy.zeros((3,3),numpy.float)
          output_values_2 = numpy.zeros((3,3),numpy.float)
          for i in 0,1,2:
              for j in 0,1,2:
                  output_values_1[i,j] = pcsim_globals.net.object(self.popul1.getObjectID(self.popul1[i,j])).Cm
                  
          self.popul1.rset('cm', rd2)
          for i in 0,1,2:
              for j in 0,1,2:
                  output_values_2[i,j] = pcsim_globals.net.object(self.popul1.getObjectID(self.popul1[i,j])).Cm

          output_values_1 = output_values_1.reshape((9,))
          output_values_2 = output_values_2.reshape((9,))
          for i in range(9):
              self.assertAlmostEqual(output_values_1[i],output_values_2[i],places=5)    
        
# ==============================================================================
class PopulationCallTest(unittest.TestCase): # to write later
     """Tests of the _call() and _tcall() methods of the Population class."""
     pass

 # ==============================================================================
class PopulationRecordTest(unittest.TestCase): # to write later
     """Tests of the record(), record_v(), printSpikes(), print_v() and
        meanSpikeCount() methods of the Population class."""
     
     def setUp(self):
         Population.nPop = 0
         self.popul = Population((3,3),IF_curr_alpha)
         
     def testRecordAll(self):
         """Population.record(): not a full test, just checking there are no Exceptions raised."""
         self.popul.record()
         
     def testRecordInt(self):
         """Population.record(n): not a full test, just checking there are no Exceptions raised."""
         self.popul.record(5)
         
     def testRecordWithRNG(self):
         """Population.record(n,rng): not a full test, just checking there are no Exceptions raised."""
         # self.popul.record(5,random.NumpyRNG())
         
     def testRecordList(self):
         """Population.record(list): not a full test, just checking there are no Exceptions raised."""
         self.popul.record([self.popul[(2,2)],self.popul[(1,2)],self.popul[(0,0)]])

 # ==============================================================================
class PopulationOtherTest(unittest.TestCase): # to write later
     """Tests of the randomInit() method of the Population class."""
     pass

# ==============================================================================
class ProjectionInitTest(unittest.TestCase):
     """Tests of the __init__() method of the Projection class."""
         
     def setUp(self):
         Population.nPop = 0
         # Projection.nProj = 0
         self.target33    = Population((3,3),IF_curr_alpha)
         self.target6     = Population((6,),IF_curr_alpha)
         self.source5     = Population((5,),SpikeSourcePoisson)
         self.source22    = Population((2,2),SpikeSourcePoisson)
         self.source33    = Population((3,3),SpikeSourcePoisson)
         self.expoisson33 = Population((3,3),SpikeSourcePoisson,{'rate': 100})
         
     def testAllToAll(self):
         """For all connections created with "allToAll" it should be possible to obtain the weight using pyneuron.getWeight()"""
         for srcP in [self.source5, self.source22]:
             for tgtP in [self.target6, self.target33]:
                 prj1 = Projection(srcP, tgtP, 'allToAll')
                 prj1.setWeights(1.234)
                 weights = []
                 for i in range(len(prj1)):
                     weights.append(pcsim_globals.net.object(prj1.pcsim_projection[i]).W)
                 for w in weights:
                     self.assertAlmostEqual(w,1.234, places = 7)
         
     def testFixedProbability(self):
         """For all connections created with "fixedProbability" it should be possible to obtain the weight using pyneuron.getWeight()"""
         for srcP in [self.source5, self.source22]:
             for tgtP in [self.target6, self.target33]:
                 prj1 = Projection(srcP, tgtP, 'fixedProbability', 0.5)
                 prj2 = Projection(srcP, tgtP, 'fixedProbability', 0.5)
                 assert (0 < len(prj1) < len(srcP)*len(tgtP)) and (0 < len(prj2) < len(srcP)*len(tgtP))
                 
     def testoneToOne(self):
         """For all connections created with "OneToOne" it should be possible to obtain the weight using pyneuron.getWeight()"""
         prj1 = Projection(self.source33, self.target33, 'oneToOne')
         assert len(prj1) == self.source33.size
      
     def testdistantDependentProbability(self):
         """For all connections created with "distanceDependentProbability" it should be possible to obtain the weight using pyneuron.getWeight()"""
         # Test should be improved..."
         distrib_Numpy = random.RandomDistribution(random.NumpyRNG(12345),'uniform',(0,1)) 
         distrib_Native= random.RandomDistribution(NativeRNG(12345),'Uniform',(0,1)) 
         prj1 = Projection(self.source33, self.target33, 'distanceDependentProbability',[ 0.1, 2], distrib_Numpy)
         prj2 = Projection(self.source33, self.target33, 'distanceDependentProbability',[ 0.1, 3], distrib_Native)
         assert (0 < len(prj1) < len(self.source33)*len(self.target33)) and (0 < len(prj2) < len(self.source33)*len(self.target33))
#         
#     def testSaveAndLoad(self):
#         prj1 = neuron.Projection(self.source33, self.target33, 'oneToOne')
#         prj1.setDelays(1)
#         prj1.setWeights(1.234)
#         prj1.saveConnections("connections.tmp")
#         prj2 = neuron.Projection(self.source33, self.target33, 'fromFile',"connections.tmp")
#         w1 = []; w2 = []; d1 = []; d2 = [];
#         # For a connections scheme saved and reloaded, we test if the connections, their weights and their delays
#         # are equal.
#         for connection_id in prj1.connections:
#             w1.append(HocToPy.get('%s.object(%d).weight' % (prj1.label,prj1.connections.index(connection_id))))
#             w2.append(HocToPy.get('%s.object(%d).weight' % (prj2.label,prj2.connections.index(connection_id))))
#             d1.append(HocToPy.get('%s.object(%d).delay' % (prj1.label,prj1.connections.index(connection_id))))
#             d2.append(HocToPy.get('%s.object(%d).delay' % (prj2.label,prj2.connections.index(connection_id))))
#         assert (w1 == w2) and (d1 == d2)
#           


class ProjectionSetTest(unittest.TestCase):
     """Tests of the setWeights(), setDelays(), setThreshold(),
#       randomizeWeights() and randomizeDelays() methods of the Projection class."""

     def setUp(self):
         setup()
         self.target   = Population((3,3),IF_curr_alpha)
         self.target   = Population((3,3),IF_curr_alpha)
         self.source   = Population((3,3),SpikeSourcePoisson,{'rate': 100})
         self.distrib_Numpy = random.RandomDistribution(random.NumpyRNG(12345),'uniform',(0,1)) 
         self.distrib_Native= random.RandomDistribution(NativeRNG(12345),'Uniform',(0,1)) 
         
     def testsetWeights(self):
         prj1 = Projection(self.source, self.target, 'allToAll')
         prj1.setWeights(2.345)
         weights = []
         for i in range(len(prj1)):
             weights.append(pcsim_globals.net.object(prj1[i]).W)
         for w in weights:
             self.assertAlmostEqual(w, 2.345)
         
         
     def testrandomizeWeights(self):
         # The probability of having two consecutive weights vector that are equal should be 0
         prj1 = Projection(self.source, self.target, 'allToAll')
         prj2 = Projection(self.source, self.target, 'allToAll')
         prj1.randomizeWeights(self.distrib_Numpy)
         prj2.randomizeWeights(self.distrib_Native)
         w1 = []; w2 = []; w3 = []; w4 = []
         for i in range(len(prj1)):
             w1.append(pcsim_globals.net.object(prj1[i]).W)
             w2.append(pcsim_globals.net.object(prj1[i]).W)
         prj1.randomizeWeights(self.distrib_Numpy)
         prj2.randomizeWeights(self.distrib_Native)
         for i in range(len(prj1)):
             w3.append(pcsim_globals.net.object(prj1[i]).W)
             w4.append(pcsim_globals.net.object(prj1[i]).W)  
         self.assertNotEqual(w1,w3) and self.assertNotEqual(w2,w4)

         
     def testSetAndGetID(self):
         # Small test to see if the ID class is working
         # self.target[0,2].set({'tau_m' : 15.1})
         # assert (self.target[0,2].get('tau_m') == 15.1)
         pass
         
     def testSetAndGetPositionID(self):
         # Small test to see if the position of the ID class is working
         # self.target[0,2].setPosition((0.5,1.5))
         # assert (self.target[0,2].getPosition() == (0.5,1.5))
         pass
         

# #class ProjectionConnectionTest(unittest.TestCase):
# #    """Tests of the connection attribute and connections() method of the Projection class."""
# #    
# #    def setUp(self):
# #        neuron.Population.nPop = 0
# #        self.pop1 = neuron.Population((5,),neuron.IF_curr_alpha)
# #        self.pop2 = neuron.Population((4,4),neuron.IF_curr_alpha)    
# #        self.pop3 = neuron.Population((3,3,3),neuron.IF_curr_alpha)
# #        self.prj23 = neuron.Projection(self.pop2,self.pop3,"allToAll")
# #        self.prj11 = neuron.Projection(self.pop1,self.pop1,"fixedProbability",0.5)
# #        
# #    def testFullAddress(self):
# #        assert self.prj23.connection[(3,1),(2,0,1)] == "[3][1][2][0][1]"
# #        assert self.prj23.connection[(3,3),(2,2,2)] == "[3][3][2][2][2]"
# #        
# #    def testPreIDPostID(self):
# #        assert self.prj23.connection[0,0] == "[0][0][0][0][0]"
# #        assert self.prj23.connection[0,26] == "[0][0][2][2][2]"
# #        assert self.prj23.connection[0,25] == "[0][0][2][2][1]"
# #        assert self.prj23.connection[15,0] == "[3][3][0][0][0]"
# #        assert self.prj23.connection[14,0] == "[3][2][0][0][0]"
# #        assert self.prj23.connection[13,19] == "[3][1][2][0][1]"
# #        
# #    def testSingleID(self):
# #        assert self.prj23.connection[0] == "[0][0][0][0][0]"
# #        assert self.prj23.connection[26] == "[0][0][2][2][2]"
# #        assert self.prj23.connection[25] == "[0][0][2][2][1]"
# #        assert self.prj23.connection[27] == "[0][1][0][0][0]"
# #        assert self.prj23.connection[53] == "[0][1][2][2][2]"
# #        assert self.prj23.connection[52] == "[0][1][2][2][1]"
# #        assert self.prj23.connection[431] == "[3][3][2][2][2]"
# #        assert self.prj23.connection[377] == "[3][1][2][2][2]"
# #        assert self.prj23.connection[370] == "[3][1][2][0][1]"
# #        
# #        assert self.prj11.connection[0] == "[0][0]"


if __name__ == "__main__":
     unittest.main()
    