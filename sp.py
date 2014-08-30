import data_01_conflictModel as mod
import data_02_conflictSolvers as slv
import data_04_spSolvers as spslv
import time


conf2 = mod.ConflictModel()
conf2.load_from_file('save_files/garrison.gmcr')

t3 = time.perf_counter()
spsol = spslv.LogicalSolver(conf2)
spsol.findEquilibria()
t4 = time.perf_counter()

print(t4-t3)



conf = mod.ConflictModel()
conf.load_from_file('save_files/garrison.gmcr')

t1 = time.perf_counter()
sol = slv.LogicalSolver(conf)
sol.findEquilibria()
t2 = time.perf_counter()
print(t2-t1)