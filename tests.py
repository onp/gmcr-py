import unittest
import data_01_conflictModel
import data_02_conflictSolvers
import data_03_gmcrUtilities as util
import numpy

files = [ "Garrison",
          "MilkRiver",
          "Prisoners",
          "SyriaIraq"
]

class TestStateSetMath(unittest.TestCase):

    def test_reduce(self):
        #non-overlapping sets should not change.
        a1 = util.reducePatterns(["Y---","---Y"])
        self.assertEqual(a1,["Y---","---Y"])
        
        #subsets should be removed.
        a2 = util.reducePatterns(["Y---","YY--"])
        self.assertEqual(a2,["Y---"])
        
        #larger example
        a3 = util.reducePatterns(["-Y---","YY---","---NY","NNNY-"])
        self.assertEqual(a3,["-Y---","---NY","NNNY-"])
        
        #If elements have different lengths, an exception should be raised.
        with self.assertRaises(ValueError):
            a4 = util.reducePatterns(["N-NN","Y-N"])
            
        #If something other than a list is provided, an exception should be raised.
        with self.assertRaises(TypeError):
            a5 = util.reducePatterns("N--,Y-N")
        
    def test_subtract(self):
        #basic subtraction example.
        a1 = util._subtractPattern("---","NYN")
        self.assertEqual(a1,['Y--','NN-','NYY'])
        
        #subtracting itself should give empty set.
        a2 = util._subtractPattern("Y--","Y--")
        self.assertEqual(a2,[])

        #subtracting a superset should give an empty set.
        a3 = util._subtractPattern("-Y-","---")
        self.assertEqual(a3,[])
        
        #If elements have different lengths, an exception should be raised.
        with self.assertRaises(ValueError):
            a4 = util._subtractPattern("-Y-","Y---")
        with self.assertRaises(ValueError):
            a5 = util._subtractPattern("-Y--","Y--")
        
    def test_subtractSingleFromGroup(self):
        #basic examples
        a1 = util.rmvSt(['-N-Y-','-N-NN'],'NNNY-')
        self.assertEqual(a1[0],["YN-Y-",'NNYY-','-N-NN'])
        self.assertEqual(a1[1],2)
        
        #Results must be presented in minimal form.
        a2 = util.rmvSt(['N----','YN---'],'-Y---')
        self.assertEqual(a2[0],['-N---'])
        self.assertEqual(a2[1],8)
        
    def test_groupSubtract(self):
        #basic examples
        a1 = util.subtractStateSets(['-----'],["-Y---","YY---","---NY","NNNY-"])
        self.assertEqual(a1,["YN-Y-",'NNYY-','-N-NN'])
        a2 = util.subtractStateSets(['N----','YN---'],["-Y---","---NY","NNNY-"])

class TestSolvers(unittest.TestCase):
    def setUp(self):
        self.conf = data_01_conflictModel.ConflictModel()

    def test_fileLoading(self):
        self.assertTrue(len(self.conf.decisionMakers) == 0)
        self.assertTrue(len(self.conf.options) == 0)
        
        for file in files:
            self.conf.load_from_file("save_files/"+file+".gmcr")
            self.assertTrue(len(self.conf.decisionMakers) > 0)
            self.assertTrue(len(self.conf.options) > 0)
            
        self.conf.__init__()
        self.assertTrue(len(self.conf.decisionMakers) == 0)
        self.assertTrue(len(self.conf.options) == 0)
        
    def test_logSol(self):
        for file in files:
            self.conf.load_from_file("save_files/"+file+".gmcr")
            solver = data_02_conflictSolvers.LogicalSolver(self.conf)
            solver.findEquilibria()
            expected = numpy.loadtxt("test_data/"+file+"_logSol.txt")
            numpy.testing.assert_array_equal(expected,solver.allEquilibria,"Incorrect logical solution for "+file)
            
    def test_narration(self):
        for file in files:
            self.conf.load_from_file("save_files/"+file+".gmcr")
            solver = data_02_conflictSolvers.LogicalSolver(self.conf)
            narrOut = ""
            for dm in self.conf.decisionMakers:
                for state in self.conf.feasibles:
                    narrOut += "\n#DM %s  state %s  NASH\n"%(dm.name,state)
                    narrOut += solver.nash(dm,state)[1]
                    narrOut += "\n#DM %s  state %s  SEQ\n"%(dm.name,state)
                    narrOut += solver.seq(dm,state)[1]
                    narrOut += "\n#DM %s  state %s  SIM\n"%(dm.name,state)
                    narrOut += solver.sim(dm,state)[1]
                    narrOut += "\n#DM %s  state %s  GMR\n"%(dm.name,state)
                    narrOut += solver.gmr(dm,state)[1]
                    narrOut += "\n#DM %s  state %s  SMR\n"%(dm.name,state)
                    narrOut += solver.smr(dm,state)[1]
            with open("test_data/"+file+"_narr.txt","r") as f:
                expected = f.read().splitlines()
                generated = narrOut.splitlines()
                self.assertEqual(expected,generated)  #used for testing
                #f.write(narrOut)  #used to update expected test results
                        
    
    def test_inverseSol(self):
        for file in files:
            self.conf.load_from_file("save_files/"+file+".gmcr")
            varyRanges = [([0,min(len(dm.preferenceVector)+1,4)] if len(dm.preferenceVector)>1 else [0,0]) for dm in self.conf.decisionMakers]
            desEqs = range(min(5,len(self.conf.feasibles)))
            for desEq in desEqs:
                solver = data_02_conflictSolvers.InverseSolver(self.conf,varyRanges,desEq)
                solver.findEquilibria()
                expected = numpy.loadtxt("test_data/%s_%s_invSol.txt"%(file,desEq))
                numpy.testing.assert_array_equal(expected,solver.equilibriums,"Incorrect inverse results for %s_%s"%(file,desEq))


if __name__ == "__main__":
    unittest.main()