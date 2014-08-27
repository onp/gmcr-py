# To use gmcr-py from the command line:

# First navigate to the folder where the program lives.
# Then type:

import gmcr

# this makes the the conflict model classes available as gmcr.model
# and the conflict solvers under as gmcr.solvers

# To initialize a fresh conflict, next type:

myConflict = gmcr.model.ConflictModel()

# A decision maker is created by giving a reference to the parent conflict, and a name for the dm:

syria = gmcr.model.DecisionMaker(myConflict, "syria")

# the DM must then be added to the game:

myConflict.decisionMakers.append(syria)

#you can also a decision maker to the conflict more directly by typing:

myConflict.decisionMakers.append("iraq")

# grab a reference to this decisionMaker:

iraq = myConflict.decisionMakers[-1]

#The list of decision makers can be shown with

print(myConflict.decisionMakers)

#or:

[dm.name for dm in myConflict.decisionMakers]

#Now, lets give the decision makers some options:

syria.addOption("Release Water")
syria.addOption("Escalate")
iraq.addOption("Attack")

rw = syria.options[0]
esc = myConflict.options[1]
att = iraq.options[0]

#View the options:

[opt.name for opt in syria.options]
[opt.name for opt in iraq.options]
[opt.name for opt in myConflict.options]

# remove infeasible states

myConflict.infeasibles.append([[rw,"Y"],[esc,"Y"]])
myConflict.recalculateFeasibleStates()

#add preferences

syria.preferences.append([[rw,"N"],[esc,"N"],[att,"N"]])
syria.preferences.append([[esc,"Y"]])
syria.preferences.append([[att,"N"]])
syria.preferences.append([[rw,"N"]])
syria.calculatePreferences()

iraq.preferences.append([[rw,"Y"],[esc,"N"],[att,"N"]])
iraq.preferences.append([[rw,"N"],[esc,"N"],[att,"Y"]])
iraq.preferences.append([[rw,"N"],[esc,"Y"],[att,"Y"]])
iraq.preferences.append([[rw,"N"],[esc,"N"],[att,"N"]])
iraq.preferences.append([[rw,"Y"],[esc,"N"],[att,"Y"]])
iraq.calculatePreferences()

# Run the conflict!

lSolver = gmcr.solvers.LogicalSolver(myConflict)











