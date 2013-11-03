# GMCR Data Structures V2

class DescriptionBase:
    """A base class providing a description interface.

    Potential target for upgrading to support rich formatting and
    validation for description entries.
    Also add support for brief (inline) versus expanded descriptions.

    """

    def __init__(self,name):
        self._description = ''
        self._name = name

    def getDescription(self):
        return self._description

    def setDescription(self,value):
        self._description = value

    description =property(getDescription,setDescription,doc='A description of the item.')
    #This could be expanded to allow for rich (HTML?) bio formatting and validation

    def __str__(self):
        return self._name

    def setName(self,value):
        """Changes the name if given a non-empty string."""
        if value.strip() != '':
            self._name = value.strip()

    name = property(__str__,setName,doc="Name of the item")

class DecisionMaker(DescriptionBase):
    """Fully describes a Decision Maker

    Tracks references to all options that they control.
    Maintains optional Bio information.
    Objects to be stored as a dictionary inside a Game object.
    Referenced by ID rather than the name, so that the name can be
        changed without breaking references.

    """

    def __init__(self,conflict,name):
        """Initializes a new Decision Maker with no options"""
        DescriptionBase.__init__(self,name)
        self.conflict=conflict
        self.optBank = conflict.optBank
        self._name = name
        self._options = []

    def remove_from_game(self):
        self.clearOptions()
        self.conflict.removeDM(self)

    def getOptions(self):
        return self._options[:]

    def clearOptions(self):
        for option in self:
            self.remove(option)   #removes all option references when deleting the DM

    options = property(getOptions,fdel=clearOptions,
        doc='References to the options controlled by the Decision Maker')
    #This Property definition should prevent the options entry from getting
    #  changed into something other than a list item or completely deleted.

    def addOption(self,option_name):
        self._options.append(self.optBank.addOption(option_name))

    def __getitem__(self,idx):
        return self._options[idx]

    def __delitem__(self,idx):
        self._options[idx].refDeinc()  #deincrements the count of references to the option.
        del self._options[idx]

    def __len__(self):
        return len(self._options)

    def __iter__(self):
            return iter(self._options)

    def __contains__(self,item):
        return (item in self._options) or (item in [str(opt) for opt in self])

    def test_string(self):
        print("The Decision Maker known as %s, with options: %s"%(self,', '.join([str(opt) for opt in self])))


class Option(DescriptionBase):
    """Full description of an option.

    Optional description string for of the option.
    Objects to be stored inside an OptionBank Object.
    Referenced by ID rather than the name, so that the name can be
        changed without breaking references.

    """

    def __init__(self,optBank,name):
        DescriptionBase.__init__(self,name)
        self.optBank = optBank
        self.refCount = 1

    def refInc(self):
        self.refCount += 1

    def refDeinc(self):
        self.refCount -= 1
        if self.refCount == 0:
            self.optBank.remove(self)


class OptionBank:
    """Holds options for a group of decision makers.

    Allows multiple DMs to reference a single move as a "common" move.
    Maintains counter of the number of DMs referencing each option,
        options are automatically deleted on reaching 0 references.
    Handles option ordering and value assignment when options are requested
        for use in logic.

    """
    def __init__(self):
        self.options = []

    def addOption(self,option_name):
        if option_name in self:
            option_name = self.collision_handler(option_name)
        newOpt = Option(self,option_name)
        self.options.append(newOpt)
        return(newOpt)

    def __contains__(self,item):
        return (item in self.options) or (item in [str(opt) for opt in self])

    def __iter__(self):
        return iter(self.options)

    def __len__(self):
        return len(self.options)

    def collision_handler(self, option_name):
        """Handles name conflict on command line. GUI should reimplement."""
        print( "Name collision detected")
        raw_input("")

    def all_those_value_handlers(self):
        pass


class Conflict(DescriptionBase):
    """Manages all information relating to a conflict.

    Consists of Decision Makers and an Option Bank. (More components to
    come?)

    """

    def __init__(self,name="Name the Conflict"):
        DescriptionBase.__init__(self,name)
        self.optBank = OptionBank()
        self.dmList = []

    def addDM(self,name="Enter a Name"):
        newDM = DecisionMaker(self,name)
        self.dmList.append(newDM)
        return newDM

    def removeDM(self,item):
        self.dmList.remove(item)

    def __iter__(self):
        return iter(self.dmList)

    def __getitem__(self,idx):
        return self.dmList[idx]

    def test_string(self):
        print("The %s conflict between DMs %s"%(self,", and ".join([str(dm) for dm in self])))


class StateList(DescriptionBase):
    """Description of a state or set of states in pseudo-dash notation.

    State descriptions are as references to options and positions.
    Behaviour is robust such that states can still be interpreted if options are
        added to or removed from the game.
    For infeasibles and preference statements.

    """

    def __init__(self):
        DescriptionBase.__init__(self)



if __name__ == '__main__':
    """Test case initialization"""

    nucCon = Conflict('NuWin')
    sp1 = nucCon.addDM()
    sp2 = nucCon.addDM("Super Power Two")
    nucCon.name = 'Nuclear Winter'
    nucCon.name = ''
    nucCon.test_string()
    sp1.name = "Super Power One"
    nucCon.test_string()
    sp1.addOption('Attack')
    for dm in nucCon:
        dm.test_string()
    sp2.addOption('Attack')
