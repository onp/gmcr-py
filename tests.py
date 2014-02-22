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

class TestLoading(unittest.TestCase):

    def setUp(self):
        self.conf = data_01_conflictModel.ConflictModel()

    def test_loads(self):
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
            numpy.testing.assert_array_equal(expected,solver.allEquilibria)
            
            
            
        
    def test_narration(self):
        pass
    
    def test_inverseSol(self):
        pass


if __name__ == "__main__":
    unittest.main()