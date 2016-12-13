# Copyright:   (c) Oskar Petersons 2013

"""Core data model and class definitions for GMCR-py."""

import json
import data_03_gmcrUtilities as gmcrUtil


class Option:
    """An option as defined in GMCR.

    An option is a True/False condition controlled by a decision maker.

    """

    def __init__(self, name, masterList, permittedDirection='both'):
        """Create a new Option."""
        self.name = str(name)
        self.permittedDirection = permittedDirection
        self.refs = 0

    def __str__(self):
        """Return string representation of the Option."""
        return self.name

    def addRef(self):
        """Increment reference counter."""
        self.refs += 1

    def remRef(self):
        """De-increment reference counter."""
        self.refs -= 1

    def export_rep(self):
        """JSONify Option data."""
        return {'name': str(self.name),
                'permittedDirection': str(self.permittedDirection)}


class DecisionMaker:
    """A Decision Maker or Player in a GMCR conflict."""

    def __init__(self, conflict, name):
        """Create a new DecisionMaker."""
        self.name = str(name)
        self.isCoalition = False
        self.conflict = conflict
        self.options = OptionList(conflict.options)
        self.preferences = ConditionList(conflict)
        self.lastPreferences = None

        self.misperceptions = ConditionList(conflict)
        self.perceived = FeasibleList()

    def __str__(self):
        """Return string representation of the DM."""
        return self.name

    def export_rep(self):
        """JSONify DM data."""
        self.calculatePreferences()
        rep = {}
        rep['name'] = str(self.name)
        rep['options'] = self.options.export_rep()
        rep['preferences'] = self.preferences.export_rep()
        rep['payoffs'] = self.payoffs.tolist()
        rep['misperceptions'] = self.misperceptions.export_rep()
        if self.conflict.useManualPreferenceRanking:
            rep['preferenceRanking'] = self.preferenceRanking
        return rep

    def full_rep(self):
        """Equivalent to export_rep()."""
        return self.export_rep()

    def addOption(self, option):
        """Give DM control of an option."""
        if option not in self.options:
            self.options.append(option)

    def removeOption(self, option):
        """Remove control of an option from the DM."""
        if option in self.options:
            self.options.remove(option)

    def onDelete(self):
        """Cleanup options if DM is deleted."""
        for opt in reversed(self.options):
            self.removeOption(opt)
        for co in self.conflict.coalitions:
            if co is self:
                self.conflict.coalitions.remove(self)
            if isinstance(co, Coalition):
                co.remove(self)
                break

    def weightPreferences(self):
        """Assign sequential weights to DM preferences.

        Weights are powers of 2, guaranteeing that states satisfying more
        important preferences are ranked higher than those satisfying less
        important preferences.
        """
        for idx, pref in enumerate(self.preferences):
            pref.weight = 2**(len(self.preferences) - idx - 1)

    def calculatePreferences(self):
        """Calculate the DM's prefence ranking of the valid states."""
        if self.conflict.useManualPreferenceRanking:
            self.payoffs = gmcrUtil.mapPrefRank2Payoffs(
                self.preferenceRanking, self.conflict.feasibles)
            self.usedRanking = self.conflict.useManualPreferenceRanking
        elif (self.lastPreferences != self.preferences.export_rep() or
              self.oldFeasibles != self.conflict.feasibles.decimal or
              self.usedRanking != self.conflict.useManualPreferenceRanking):

            self.lastPreferences = self.preferences.export_rep()
            self.usedRanking = self.conflict.useManualPreferenceRanking
            self.oldFeasibles = list(self.conflict.feasibles.decimal)

            self.preferences.validate()
            self.weightPreferences()
            result = gmcrUtil.prefPriorities2payoffs(self.preferences,
                                                     self.conflict.feasibles)
            self.payoffs = result[0]
            self.preferenceRanking = result[1]

        self.perceivedRanking = []
        for st in self.preferenceRanking:
            if isinstance(st, list):
                subGroup = []
                for subState in st:
                    if subState in self.perceived.ordered:
                        subGroup.append(subState)
                if len(subGroup) > 1:
                    self.perceivedRanking.append(subGroup)
                elif len(subGroup) == 1:
                    self.perceivedRanking.append(subGroup[0])
            elif st in self.perceived.ordered:
                self.perceivedRanking.append(st)

    def calculatePerceived(self):
        """Calculate states perceived by the DM based on misperceptions."""
        percDash = self.conflict.feasibles.dash
        for misp in self.misperceptions:
            res = gmcrUtil.rmvSt(percDash, misp.ynd())
            percDash = res[0]
            misp.statesRemoved = res[1]
        toOrd = self.conflict.feasibles.toOrdered
        self.perceived = FeasibleList(percDash, toOrdered=toOrd)
        self.misperceived = [st for st in self.conflict.feasibles.ordered
                             if st not in self.perceived.ordered]


class Condition:
    """A subset of options, specified as either taken or not taken.

    A state may be tested against a condition to determine whether or not it
    satisfies it.
    """

    def __init__(self, conflict, condition):
        """Create a new Condition."""
        self.conflict = conflict
        self.options = OptionList(conflict.options)
        self.taken = []
        for opt, taken in condition:
            self.options.append(opt)
            self.taken.append(taken)
        self.name = self.ynd()
        self.isCompound = False

    def __str__(self):
        """String representation of the condition."""
        return self.name + " object"

    def updateName(self):
        """Update the value of .name to match the condition in YND notation."""
        self.name = self.ynd()

    def cond(self):
        """The condition represented as tuples: (option, True/False)."""
        return zip(self.options, self.taken)

    def ynd(self):
        """Return the Condition in 'Yes No Dash' notation."""
        self.conflict.options.set_indexes()
        ynd = ['-'] * len(self.conflict.options)
        for opt, taken in self.cond():
            ynd[opt.master_index] = taken
        return ''.join(ynd)

    def test(self, state):
        """Test against a decimal state.

        Returns True if state satisfies the Condition.
        """
        self.conflict.options.set_indexes()
        state = gmcrUtil.dec2yn(state, len(self.conflict.options))
        for opt, taken in self.cond():
            if state[opt.master_index] != taken:
                return False
        return True

    def isValid(self):
        """Check all options in the Condition are defined in the conflict."""
        for opt in self.options:
            if opt not in self.conflict.options:
                return False
        self.updateName()
        return True

    def export_rep(self):
        """JSONify the Condition for export."""
        self.conflict.options.set_indexes()
        return [(opt.master_index, taken) for opt, taken in self.cond()]


class CompoundCondition:
    """A complex condition defined as a union of simple conditions."""

    def __init__(self, conflict, conditions):
        """Create a compound condition."""
        self.conflict = conflict
        self.conditions = [Condition(self.conflict, dat) for dat in conditions]
        self.isCompound = True
        self.updateName()

    def __str__(self):
        """Return string representation."""
        return self.name + " object"

    def index(self, i):
        """Index of the passed condition."""
        return self.conditions.index(i)

    def __len__(self):
        return len(self.conditions)

    def __getitem__(self, key):
        return self.conditions[key]

    def __iter__(self):
        return iter(self.conditions)

    def updateName(self):
        """Update the name string based on the subconditions."""
        self.name = str(sorted(self.ynd()))[1:-1].replace("'", '')

    def append(self, condition):
        """Add the condition given to the compound condition."""
        self.conditions.append(condition)
        self.updateName()

    def __delitem__(self, key):
        """Remove the condition at idx from the compound condition."""
        del self.conditions[key]
        self.updateName()

    def ynd(self):
        """Return the compound condition as a list of items in YND notation."""
        return [cond.ynd() for cond in self.conditions]

    def test(self, state):
        """Test against a decimal state.

        Returns True if state satisfies one or more of the component
        conditions.
        """
        for cond in self.conditions:
            if cond.test(state):
                return True
        return False

    def isValid(self):
        """Check all options in the Condition are defined in the conflict."""
        for cond in self.conditions:
            if not cond.isValid():
                return False
        self.updateName()
        return True

    def export_rep(self):
        """JSONify the CompoundCondition for export."""
        return {"compound": True,
                "members": [cond.export_rep() for cond in self.conditions]}


class ObjectList:
    """A base class for lists of DMs/options. Defines useful magic methods."""

    def __init__(self, masterList=None):
        """Initialize a generic ObjectList."""
        self.itemList = []
        self.masterList = masterList

    def __len__(self):
        return len(self.itemList)

    def __getitem__(self, key):
        return self.itemList[key]

    def __setitem__(self, key, value):
        self.itemList[key] = value

    def __delitem__(self, key):
        item = self.itemList[key]
        del self.itemList[key]
        if self.masterList is not None:
            self.masterList.remove(item)

    def remove(self, item):
        """Remove the passed item from the list."""
        self.itemList.remove(item)
        if self.masterList is not None:
            self.masterList.remove(item)

    def __iter__(self):
        return iter(self.itemList)

    def __reversed__(self):
        return reversed(self.itemList)

    def __contains__(self, item):
        return item in self.itemList

    def insert(self, i, x):
        """Standard list insert behaviour."""
        self.itemList.insert(i, x)

    def pop(self, i=None):
        """Standard list pop behaviour."""
        return self.itemList.pop(i)

    def index(self, i):
        """Standard list index behaviour."""
        return self.itemList.index(i)

    def set_indexes(self):
        """Set each list item's index attribute based on the list order."""
        for idx, item in enumerate(self.itemList):
            item.master_index = idx
            item.dec_val = 2**(idx)

    def names(self):
        """Get string names of all items in the list."""
        return [item.name for item in self.itemList]


class DecisionMakerList(ObjectList):
    """A list of DecisionMaker objects."""

    def __init__(self, conflict):
        """Initialize a list of decisionMakers."""
        ObjectList.__init__(self)
        self.conflict = conflict

    def __str__(self):
        """Return string representation."""
        return str([dm.name for dm in self])

    def export_rep(self):
        """JSONify the DecisionMakerList for export."""
        return [x.export_rep() for x in self.itemList]

    def append(self, item):
        """Append the passed DecisionMaker to the list.

        Creates a new DecisionMaker if a string is passed, using the
        string as the DM's name.
        """
        if isinstance(item, DecisionMaker) and item not in self.itemList:
            self.itemList.append(item)
        elif isinstance(item, str):
            self.itemList.append(DecisionMaker(self.conflict, item))

    def __delitem__(self, key):
        self.itemList[key].onDelete()
        del self.itemList[key]

    def from_json(self, dmData):
        """Create a new DM from JSON data and add it to the list."""
        newDM = DecisionMaker(self.conflict, dmData['name'])
        for optIdx in dmData['options']:
            newDM.options.append(self.conflict.options[int(optIdx)])
        for preference in dmData['preferences']:
            newDM.preferences.from_json(preference)
        try:
            newDM.misperceptions = ConditionList(self.conflict)
            for mispData in dmData['misperceptions']:
                newDM.misperceptions.from_json(mispData)
        except KeyError:
            pass
        if self.conflict.useManualPreferenceRanking:
            try:
                newDM.preferenceRanking = dmData['preferenceRanking']
            except KeyError:
                # for compatibility with old save files
                newDM.preferenceRanking = dmData['preferenceVector']
        self.append(newDM)


class OptionList(ObjectList):
    """A list of Option objects."""

    def __init__(self, masterList=None):
        """Initialize a new OptionList."""
        ObjectList.__init__(self, masterList)

    def export_rep(self):
        """JSONify the Option for export."""
        if self.masterList is not None:
            self.masterList.set_indexes()
            return [x.master_index for x in self.itemList]
        else:
            return [x.export_rep() for x in self.itemList]

    def append(self, item):
        """Append the passed Option to the list.

        Creates a new Option if a string is passed, using the string
        as the option's name.
        """
        if isinstance(item, Option) and item not in self.itemList:
            self.itemList.append(item)
            if self.masterList is not None:
                item.addRef()
                if item not in self.masterList:
                    self.masterList.append(item)
        elif isinstance(item, str):
            if self.masterList is None:
                newOption = Option(item, self)
            else:
                newOption = Option(item, self.masterList)
                self.masterList.append(newOption)
                newOption.addRef()
            self.itemList.append(newOption)

    def from_json(self, optData):
        """Create a new option from JSON data and add it to the list."""
        newOption = Option(optData['name'], self.masterList,
                           optData['permittedDirection'])
        self.append(newOption)


class ConditionList(ObjectList):
    """A list of Condition objects."""

    def __init__(self, conflict):
        """Initialize a new ConditionList."""
        ObjectList.__init__(self)
        self.conflict = conflict

    def export_rep(self):
        """JSONify the ConditionList for export."""
        return [x.export_rep() for x in self.itemList]

    def from_json(self, condData):
        """Replace the option number with the actual option object."""
        if isinstance(condData, list):
            for opt in condData:
                opt[0] = self.conflict.options[opt[0]]
        elif isinstance(condData, dict):
            for mem in condData['members']:
                for opt in mem:
                    opt[0] = self.conflict.options[opt[0]]
        self.append(condData)

    def append(self, item):
        """Add a new condition to the list.

        Argument can be a Condition, CompoundCondition, list/string format
        condition, or a dict/string format CompoundCondition.
        """
        if isinstance(item, Condition) or isinstance(item, CompoundCondition):
            newCondition = item
        elif isinstance(item, list):
            newCondition = Condition(self.conflict, item)
        elif isinstance(item, dict):
            newCondition = CompoundCondition(self.conflict, item['members'])
        else:
            raise TypeError('Not a valid Condition Object')

        if newCondition.name not in [cond.name for cond in self]:
            self.itemList.append(newCondition)
        else:
            print("attempted to add duplicate; ignored")

    def moveCondition(self, idx, targ):
        """Move a condition from position idx in the list to position targ."""
        j = self.pop(idx)
        self.insert(targ, j)

    def removeCondition(self, idx):
        """Remove the Condition at position idx."""
        del self[idx]

    def validate(self):
        """Check that all conditions in the list are valid."""
        toRemove = []
        for idx, pref in enumerate(self):
            if not pref.isValid():
                toRemove.append(idx)
        for idx in toRemove[::-1]:
            del self[idx]

    def format(self, fmt="YN-"):
        """Return the conditions in the specified format.

        Valid formats are:
        'YN-': uses 'Y','N', and '-' to represent infeasible states compactly.
        'YN': lists all infeasible states using 'Y' and 'N'.
        'dec': lists all infeasible states in decimal form.
        """
        if fmt == 'YN-':
            return [x.ynd() for x in self]
        if fmt == 'YN':
            return sorted(set(gmcrUtil.expandPatterns(self.format('YN-'))))
        if fmt == 'dec':
            return [self.yn2dec(state) for state in self.format('YN')]
        else:
            print('invalid format')


class FeasibleList:
    """A list of feasible states, allowing access in multiple formats."""

    def __init__(self, dash=None, toOrdered=None):
        """Construct a list of feasibles based on a dash format input list."""
        if not dash:
            self.decimal = []
            self.dash = []
            return
        # as 'Y,N,-' compact patterns
        self.dash = gmcrUtil.reducePatterns(dash)

        temp = sorted([(gmcrUtil.yn2dec(yn), yn) for yn
                       in gmcrUtil.expandPatterns(self.dash)])

        # as 'Y,N' patterns
        self.yn = [yn for dec, yn in temp]

        # as decimal values
        self.decimal = [dec for dec, yn in temp]

        # conversion dictionaries
        if toOrdered is None:
            self.toOrdered, self.toDecimal = gmcrUtil.orderedNumbers(
                self.decimal)
        else:
            self.toOrdered = {x: toOrdered[x] for x in self.decimal}
            self.toDecimal = {toOrdered[x]: x for x in self.decimal}

        # as ordered numbers
        self.ordered = sorted(self.toDecimal.keys())

        # special display notation
        self.ordDec = ['{:3d}  [{}]'.format(seq, dec)
                       for seq, dec in zip(self.ordered, self.decimal)]

    def __len__(self):
        return len(self.decimal)

    def __iter__(self):
        return iter(range(len(self.decimal)))


class Coalition:
    """Combination of two or more decision makers.

    Has interfaces equivalent to DMs.
    """

    def __init__(self, conflict, dms):
        """Initialize a new Coalition."""
        self.members = dms
        self.isCoalition = True
        self.conflict = conflict
        self.refresh()

    def refresh(self):
        """Refresh coalition attributes based on member DM data."""
        self.name = ', '.join([dm.name for dm in self.members])
        self.options = OptionList(self.conflict.options)

        for dm in self.members:
            for opt in dm.options:
                self.options.append(opt)

        self.preferences = ConditionList(self.conflict)
        self.calculatePreferences()
        self.calculatePerceived()

    def __str__(self):
        return self.name

    def __iter__(self):
        return iter(self.members)

    def __delitem__(self, key):
        del self.members[key]
        self.refresh()

    def remove(self, dm):
        """Remove a memeber from the coalition and refresh data."""
        if dm in self.members:
            self.members.remove(dm)
            self.refresh()

    def __contains__(self, dm):
        return dm in self.members

    def insert(self, i, x):
        """Insert a new member into the coalition and refresh data."""
        self.members.insert(i, x)
        self.refresh()

    def export_rep(self):
        """JSONify the Coalition for export."""
        if len(self.members) > 1:
            return [self.conflict.decisionMakers.index(dm)
                    for dm in self.members]
        else:
            return self.conflict.decisionMakers.index(self.members[0])

    def disp_rep(self):
        """Coalition display format for GUI use."""
        if len(self.members) > 1:
            return [self.conflict.decisionMakers.index(dm) + 1
                    for dm in self.members]
        else:
            return self.conflict.decisionMakers.index(self.members[0]) + 1

    def full_rep(self):
        """Representation of the coalition as a decision maker."""
        rep = {}
        rep['name'] = str(self.name)
        rep['options'] = self.options.export_rep()
        return rep

    def calculatePreferences(self):
        """Recalculate preferences of each member DM."""
        for dm in self.members:
            dm.calculatePreferences()
        self.payoffs = [", ".join([str(dm.payoffs[state])
                                   for dm in self.members])
                        for state in self.conflict.feasibles]

    def calculatePerceived(self):
        """Calculate the states perceived by the coalition.

        It is assumed that a state that can be seen by one or more
        members can be seen by the entire coalition.
        """
        for dm in self.members:
            dm.calculatePerceived()
        toOrd = self.conflict.feasibles.toOrdered
        percDash = [d for dm in self.members for d in dm.perceived.dash]
        self.perceived = FeasibleList(percDash, toOrdered=toOrd)


class CoalitionList(ObjectList):
    """A set of coalitions including all DMs in the conflict."""

    def __init__(self, conflict):
        """Initialize a new CoalitionList."""
        ObjectList.__init__(self)
        self.conflict = conflict

    def export_rep(self):
        """JSONify the CoalitionList for export."""
        working = list(self.itemList)
        for idx, item in enumerate(working):
            if isinstance(item, DecisionMaker):
                working[idx] = self.conflict.decisionMakers.index(item)
            else:
                working[idx] = item.export_rep()
        return working

    def full_rep(self):
        """Representation of the coalitions as decision makers."""
        return [x.full_rep() for x in self.itemList]

    def disp_rep(self):
        """Coalition display format for GUI use."""
        working = list(self.itemList)
        for idx, item in enumerate(working):
            if isinstance(item, DecisionMaker):
                working[idx] = self.conflict.decisionMakers.index(item) + 1
            else:
                working[idx] = item.disp_rep()
        return working

    def append(self, item):
        """Add a Coalition or DecisionMaker to the list."""
        if isinstance(item, Coalition) and item not in self.itemList:
            self.itemList.append(item)
        elif isinstance(item, DecisionMaker):
            self.itemList.append(item)
        else:
            raise TypeError("{} is not a Coalition".format(item))

    def from_json(self, coData):
        """Create a new Coalition from JSON data."""
        if isinstance(coData, int):
            memberList = [self.conflict.decisionMakers[int(coData)]]
        elif isinstance(coData, list):
            memberList = [self.conflict.decisionMakers[int(dmIdx)]
                          for dmIdx in coData]
        newCO = Coalition(self.conflict, memberList)
        self.append(newCO)

    def validate(self):
        """Check that coalitions are valid and do not include duplicates."""
        dms = list(self.conflict.decisionMakers)
        for co in self.itemList:
            if isinstance(co, Coalition):
                for dm in co:
                    dms.remove(dm)
            else:
                dms.remove(co)
        if len(dms) == 0:
            return True
        return False


class ConflictModel:
    """Master object defining a conflict."""

    def __init__(self):
        """Initialize a new, empty conflict."""
        # list of Option objects
        self.options = OptionList()

        # list of DecisonMaker objects
        self.decisionMakers = DecisionMakerList(self)

        # list of Condition objects
        self.infeasibles = ConditionList(self)
        self.feasibles = FeasibleList()

        self.useManualPreferenceRanking = False
        self.preferenceErrors = None
        self.coalitions = CoalitionList(self)

    def newCondition(self, condData):
        """Create a new Condition linked to the conflict."""
        return Condition(self, condData)

    def newCompoundCondition(self, condData):
        """Create a new CompoundCondition linked to the conflict."""
        return CompoundCondition(self, condData)

    def newCoalition(self, coalitionData):
        """Create a new Coalition linked to the conflict."""
        return Coalition(self, coalitionData)

    def export_rep(self):
        """Generate a  JSON encodable representation of the conflict."""
        self.reorderOptionsByDM()
        return {'decisionMakers': self.decisionMakers.export_rep(),
                'coalitions': self.coalitions.export_rep(),
                'coalitionsFull': self.coalitions.full_rep(),
                'options': self.options.export_rep(),
                'infeasibles': self.infeasibles.export_rep(),
                'useManualPreferenceRanking': self.useManualPreferenceRanking,
                'program': 'gmcr-py',
                'version': '0.3.13'}

    def save_to_file(self, file):
        """Save the current conflict to the file location given."""
        print(self.export_rep())
        try:
            fileObj = open(file, mode='w')
        except IOError:
            print('file not readable')
            return
        try:
            json.dump(self.export_rep(), fileObj)
        finally:
            fileObj.close()

    def json_import(self, d):
        """Import values into the conflict from JSON data."""
        try:
            self.useManualPreferenceRanking = d['useManualPreferenceRanking']
        except KeyError:
            # old save file compatibility
            self.useManualPreferenceRanking = d['useManualPreferenceVectors']
        for optData in d['options']:
            self.options.from_json(optData)
        for dmData in d['decisionMakers']:
            self.decisionMakers.from_json(dmData)
        for infData in d['infeasibles']:
            self.infeasibles.from_json(infData)
        self.reorderOptionsByDM()
        self.infeasibles.validate()
        self.recalculateFeasibleStates(True)
        for dm in self.decisionMakers:
            dm.calculatePerceived()
            dm.calculatePreferences()
        try:
            for coData in d['coalitions']:
                self.coalitions.from_json(coData)
        except KeyError:
            for dm in self.decisionMakers:
                self.coalitions.append(dm)
        if not self.coalitions.validate():
            print('Coalitions failed to validate, reseting')
            self.coalitions = CoalitionList(self)
            for dm in self.decisionMakers:
                self.coalitions.append(dm)
            if not self.coalitions.validate():
                raise Exception("Coalitions Failure")

    def load_from_file(self, file):
        """Load a conflict from the file given."""
        self.__init__()
        self.file = file
        try:
            fileObj = open(file, mode='r')
        except IOError:
            print('file not readable')
            return
        try:
            self.json_import(json.load(fileObj))
        except EOFError:
            print('file is empty')
            return
        finally:
            fileObj.close()

    def recalculateFeasibleStates(self, init_override=False):
        """Update all feasible state calculations."""
        oldFeas = list(self.feasibles.decimal)
        feasDash = ['-' * len(self.options)]
        for infeas in self.infeasibles:
            res = gmcrUtil.rmvSt(feasDash, infeas.ynd())
            feasDash = res[0]
            infeas.statesRemoved = res[1]
        self.feasibles = FeasibleList(feasDash)
        if self.feasibles.decimal != oldFeas:
            if not init_override:
                self.onFeasibleStatesChanged()

    def onFeasibleStatesChanged(self):
        """Clear obsolete preferences when feasible states are changed."""
        self.useManualPreferenceRanking = False

    def clearPreferences(self):
        """Reinitialize preferences for all DMs."""
        for dm in self.decisionMakers:
            dm.preferences.__init__(self)

    def reorderOptionsByDM(self):
        """Sort option list, placing options controlled by same DM together."""
        moved = []
        for dm in self.decisionMakers:
            for option in dm.options:
                if option not in moved:
                    moved.append(option)
                    self.options.insert(
                        len(moved),
                        self.options.pop(self.options.index(option))
                    )
        self.options.set_indexes()
