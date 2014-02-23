import unittest
import data_01_conflictModel
import data_02_conflictSolvers
import data_03_gmcrUtilities
import numpy

files = [ "Garrison",
          "MilkRiver",
          "Prisoners",
          "SyriaIraq"
]

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
        pass


if __name__ == "__main__":
    unittest.main()