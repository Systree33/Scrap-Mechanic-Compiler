import json
import random
import copy
import math

LogicGates = {"and": 0,
              "or": 1,
              "xor": 2,
              "nand": 3,
              "nor": 4,
              "xnor": 5}

ShapeIDs = {"Logic Gate": "9f0f56e8-2c31-4d83-996c-d00a9b296c3f",
            "Timer": "8f7fd0e7-c46e-4944-a414-7ce2437bb30f"}

class Gate:
    def __init__(self,Type,Active=False):
        self.ID = 0
        self.Active = Active
        if Type.lower() in LogicGates:
            self.Type = LogicGates[Type.lower()]
        else:
            raise ValueError(str(Type)+" is not a valid gate type.")

class Timer:
    def __init__(self,Seconds=1,Ticks=0,Active=False):
        self.ID = 0
        self.Active = Active
        self.Seconds = Seconds
        self.Ticks = Ticks

class Connection:
    def __init__(self,GateFrom,GateTo):
        self.GateFrom = GateFrom
        self.GateTo = GateTo

class LogicGroup:
    def __init__(self):
        self.Gates = []
        self.Connections = []
        self.CurrentID = 0
    def AddGate(self,Gate):
        Gate.ID = self.CurrentID
        self.Gates.append(Gate)
        self.CurrentID += 1
        return Gate.ID
    def AddGroup(self,Group):
        for Gate in Group.Gates:
            Gate.ID += self.CurrentID
            self.Gates.append(Gate)
        self.CurrentID += len(Group.Gates)
        for Connection in Group.Connections:
            self.Connections.append(Connection)
    def Connect(self,GateFrom,GateTo):
        self.Connections.append(Connection(GateFrom,GateTo))
    def Debug(self):
        for Gate in self.Gates:
            print("ID: ",Gate.ID," Type: ",Gate.Type)
        for Connection in self.Connections:
            print("From: ",Connection.GateFrom.ID," To: ",Connection.GateTo.ID)

BaseData = {"color": "FFFFFF",
            "pos": {
                "x": 0,
                "y": 0,
                "z": 0
                },
            "xaxis": 1,
            "zaxis": -2
            }

class Blueprint:
    def __init__(self):
        self.Objects = []
    def AddLogicGroup(self,Group):
        Pos = 0
        for CurrentGate in Group.Gates:
            CurrentGate.Data = copy.deepcopy(BaseData)
            #CurrentGate.Data["pos"]["x"] = Pos
            #CurrentGate.Data["pos"]["y"] = Pos % 2
            #Pos += 1
            CurrentGate.Data["controller"] = {"active": CurrentGate.Active,
                                       "controllers": None,
                                       "id": CurrentGate.ID,
                                       "joints": None}
            if isinstance(CurrentGate,Gate):
                #print("Gate")
                CurrentGate.Data["shapeId"] = ShapeIDs["Logic Gate"]
                CurrentGate.Data["controller"]["mode"] = CurrentGate.Type
            if isinstance(CurrentGate,Timer):
                #print("Timer")
                CurrentGate.Data["shapeId"] = ShapeIDs["Timer"]
                CurrentGate.Data["controller"]["seconds"] = CurrentGate.Seconds
                CurrentGate.Data["controller"]["ticks"] = CurrentGate.Ticks
                print(CurrentGate.Seconds)
        for Connection in Group.Connections:
            try:
                CurrentConnections = Connection.GateFrom.Data["controller"]["controllers"]
            except AttributeError:
                raise RuntimeError("Did you forget to add a gate?")
            if CurrentConnections == None:
                CurrentConnections = []
            CurrentConnections.append({"id": Connection.GateTo.ID})
            Connection.GateFrom.Data["controller"]["controllers"] = CurrentConnections
        for CurrentGate in Group.Gates:
            self.Objects.append(CurrentGate.Data)
    def Arrange(self,InputsDict,OutputsDict,Function):
        InputsNum = len(InputsDict)
        OutputsNum = len(OutputsDict)
        OtherNum = len(self.Objects)-(len(InputsDict)+len(OutputsDict))
        print(InputsNum,OutputsNum,OtherNum)
        InputsPositions, OutputsPositions, OtherPositions = Function(InputsNum,OutputsNum,OtherNum)
        print(len(InputsPositions), len(OutputsPositions), len(OtherPositions))
        Inputs = [InputsDict[Input]["RawInput"] for Input in InputsDict.keys()]
        Outputs = [OutputsDict[Output]["Output"] for Output in OutputsDict.keys()]
        Other = []
        for ObjectNum, Object in enumerate(self.Objects):
            IsInputOrOutput = False
            for Input in Inputs:
                if Input.Data == Object:
                    IsInputOrOutput = True
            for Output in Outputs:
                if Output.Data == Object:
                    IsInputOrOutput = True
            if IsInputOrOutput == False:
                Other.append(ObjectNum)
            if IsInputOrOutput == True:
                print("Match")

        for InputNum, Input in enumerate(Inputs):
            Inputs[InputNum].Data["pos"]["x"] = InputsPositions[InputNum][0]
            Inputs[InputNum].Data["pos"]["y"] = InputsPositions[InputNum][1]
            Inputs[InputNum].Data["pos"]["z"] = InputsPositions[InputNum][2]
        #print(OutputsPositions[0])
        for OutputNum, Output in enumerate(Outputs):
            Outputs[OutputNum].Data["pos"]["x"] = OutputsPositions[OutputNum][0]
            Outputs[OutputNum].Data["pos"]["y"] = OutputsPositions[OutputNum][1]
            Outputs[OutputNum].Data["pos"]["z"] = OutputsPositions[OutputNum][2]
        for OtherGateNum, OtherGateID in enumerate(Other):
            self.Objects[OtherGateID]["pos"]["x"] = OtherPositions[OtherGateNum][0]
            self.Objects[OtherGateID]["pos"]["y"] = OtherPositions[OtherGateNum][1]
            self.Objects[OtherGateID]["pos"]["z"] = OtherPositions[OtherGateNum][2]
        #print(len(Other))
        #print(Inputs[Inputs.keys()])
        #print(Outputs[Outputs.keys()])
        #print(Other[0])
        #self.Object["pos"]["x"] = OtherPositions[]
        #X = 0
        #Y = 0
        #SideLength = math.ceil(math.sqrt(len(self.Objects)))
        #for Object in self.Objects:
        #    Object["pos"]["x"] = X
        #    Object["pos"]["y"] = Y
        #    X += 1
        #    if X > SideLength:
        #        X = 0
        #        Y += 1
    def Export(self):
        print(self.Objects)
        Structure = {"version": 4,
                     "bodies": [
                         {"childs": []}
                         ]
                     }
        Structure["bodies"][0]["childs"] = self.Objects
        return Structure
    def Save(self,FileName):
        Structure = self.Export()
        with open(FileName,"w+") as File:
            json.dump(Structure,File)
    def ShowStats(self):
        ObjectCounts = {list(ShapeIDs.keys())[list(ShapeIDs.values()).index(Object)]: list(map(lambda X : X["shapeId"],self.Objects)).count(Object) for Object in set(map(lambda X : X["shapeId"],self.Objects))}
        print(ObjectCounts)

def MakeLatch():
    Latch = LogicGroup()

    Enable = Gate("Or")
    Or1 = Gate("Or")
    Output = Gate("Or")
    And1 = Gate("And")
    Disable = Gate("Nor")
    AlwaysOff = Gate("And")

    Latch.AddGate(Enable)
    Latch.AddGate(Or1)
    Latch.AddGate(Output)
    Latch.AddGate(And1)
    Latch.AddGate(Disable)
    Latch.AddGate(AlwaysOff)

    Latch.Connect(Enable,Output)
    Latch.Connect(Output,And1)
    Latch.Connect(And1,Enable)

    Latch.Connect(Enable,Or1)
    Latch.Connect(Or1,Output)

    Latch.Connect(AlwaysOff,Disable)
    Latch.Connect(Disable,And1)
    
    #----> Latch  Enable  Diable  Output
    return Latch, Enable, Disable, Output

def MakeTickExtender():
    TickExtender = LogicGroup()

    Input = Gate("Or")
    G1 = Gate("Or")
    G2 = Gate("Or")
    Output = Gate("Or")

    TickExtender.AddGate(Input)
    TickExtender.AddGate(G1)
    TickExtender.AddGate(G2)
    TickExtender.AddGate(Output)

    TickExtender.Connect(Input,G1)
    TickExtender.Connect(G1,G2)
    
    TickExtender.Connect(Input,Output)
    TickExtender.Connect(G1,Output)
    TickExtender.Connect(G2,Output)

    return TickExtender, Input, Output

def ArrangeLine(InputsNum,OutputsNum,OtherNum):
    X = 0
    return ([(X,0,0) for X in range(InputsNum)],[(X+InputsNum,0,0) for X in range(OutputsNum)],[(X+InputsNum+OutputsNum,0,0) for X in range(OtherNum)])

def ArrangeRandom(InputsNum,OutputsNum,OtherNum):
    def RandomPos():
        return (random.randint(0,20),random.randint(0,20),random.randint(0,20))
    def RandomPositions(Amount):
        return [RandomPos() for Pos in range(Amount)]
    return (RandomPositions(InputsNum),RandomPositions(OutputsNum),RandomPositions(OtherNum))

def ArrangeCube(InputsNum,OutputsNum,OtherNum):
    X = 0
    Y = 0
    Z = 0
    SideLen = math.floor(OtherNum ** (1/3))
    print("Cube with side length "+str(SideLen))

    OtherPositions = []
    for Count in range(OtherNum):
        OtherPositions.append((X,Y,Z))
        X += 1
        if X == SideLen:
            X = 0
            Y += 1
        if Y == SideLen:
            Y = 0
            Z += 1
        if Z == SideLen:
            #Z = 0
            pass
    X = -1
    Y = -1
    Z = 0
    Direction = 0
    Pos = 0
    Total = 1
    Inputs = []
    Outputs = []
    for AddPos in range(InputsNum+OutputsNum):
        if AddPos < InputsNum:
            Inputs.append((X,Y,Z))
        else:
            Outputs.append((X,Y,Z))
        if Direction == 0:
            X += 1
        elif Direction == 1:
            Y += 1
        elif Direction == 2:
            X -= 1
        elif Direction == 3:
            Y -=1
        Pos += 1
        Total += 1
        if Pos == SideLen+2-1:
            Pos = 0
            Direction += 1
            if Direction == 4:
                Direction = 0
        if Total > (SideLen*4)+4:
            Z += 1
            Total = 1
    #return ([(X+SideLen,0,0) for X in range(InputsNum)],[(X+SideLen+InputsNum,0,0) for X in range(OutputsNum)],OtherPositions)
    return (Inputs,Outputs,OtherPositions)

def ParseExpression(Expression):
    Parsed = []
    Type = ""
    ExpressionNum = 0
    Expressions = []
    Remaining = list(Expression)
    State = "Type"
    After = ""
    Depth = 0
    while len(Remaining) > 0:
        Char = Remaining.pop(0)
        if State == "After":
            After = After + Char
            continue
        if Char == "(":
            if Depth == 0:
                Depth += 1
                State = "Expression"
                Expressions.append("")
                continue
            Depth += 1
        if Char == ")":
            if Depth == 1:
                Depth -= 1
                State = "After"
                continue
            Depth -= 1
            if Depth == 0:
                State = "After"
                continue
        if Char == " ":
            continue
        if Char == "," and Depth == 1 and State == "Expression":
            ExpressionNum += 1
            Expressions.append("")
            continue
        if State == "Expression":
            Expressions[ExpressionNum] = Expressions[ExpressionNum] + Char
        
        if State == "Type":
            Type = Type + Char

    if Depth != 0:
        raise SyntaxError("Invalid Expression")

    if len(Expressions) == 0:
        return Type, ""
    else:
        ParsedExpressions = [ParseExpression(Expr)[0] for Expr in Expressions]
        return [Type, ParsedExpressions], After

#print(ParseExpression("And(Or(A,B),C) hello"))

def HexToRGB(Hex):
    return tuple(int(Hex.lstrip("#")[I:I+2],16) for I in (0,2,4))

def Compile(File):
    MainLogic = LogicGroup()

    Outputs = {}
    Inputs = {}

    Bools = {}

    Functions = {}
    Triggers = []
    Conditions = {}

    AlwaysOff = Gate("Or")
    AlwaysOn = Gate("Nor")
    StartTick = Gate("Xor")

    LineNum = 0

    def BuildExpression(Expression):
        nonlocal MainLogic
        nonlocal LineNum
        try:
            OutputGate = Gate(Expression[0])
        except IndexError:
            raise ValueError("Invalid expression: "+str(Expression)+" at line "+str(LineNum))
        MainLogic.AddGate(OutputGate)
        for Expr in Expression[1]:
            if isinstance(Expr,str):
                FoundReference = False
                Reference = None
                if Expr in Conditions.keys():
                    FoundReference = True
                    Reference = Conditions[Expr]
                elif Expr in Bools.keys():
                    FoundReference = True
                    Reference = Bools[Expr]["Output"]
                elif Expr in Inputs.keys():
                    FoundReference = True
                    Reference = Inputs[Expr]["RawInput"]
                elif Expr in Outputs.keys():
                    FoundReference = True
                    Reference = Outputs[Expr]["Output"]
                if Reference == None:
                    raise NameError("What is "+Expr+" on line "+str(LineNum))
                MainLogic.Connect(Reference,OutputGate)
                print("Connecting "+Expr+" ("+str(Reference)+") to outputgate "+str(OutputGate))
            elif isinstance(Expr,list):
                SubOutputGate = BuildExpression(Expr)
                MainLogic.Connect(SubOutputGate,OutputGate)
                print("Connecting suboutputgate "+str(SubOutputGate)+" to OutputGate")
            else:
                print("Error at line "+str(LineNum))
            #CompileExpression()
        return OutputGate

    #print(BuildExpression(ParseExpression("And(And(A,B),And(C,D))")[0]))
    #return

    StartedLatch, EnableStarted, DisableStarted, StartedLatchOutput = MakeLatch()
    MainLogic.AddGroup(StartedLatch)
    MainLogic.AddGate(AlwaysOff)
    MainLogic.AddGate(AlwaysOn)
    MainLogic.Connect(AlwaysOff,AlwaysOn)
    MainLogic.AddGate(StartTick)
    #MainLogic.Connect(AlwaysOff,StartTick)
    MainLogic.Connect(AlwaysOn,StartTick)
    StartTickExtender, StartTickInput, InstantStartPulse = MakeTickExtender()
    MainLogic.AddGroup(StartTickExtender)
    MainLogic.Connect(StartTick,StartTickInput)
    StartPulse = Timer(Ticks=2,Seconds=0)
    MainLogic.AddGate(StartPulse)
    MainLogic.Connect(StartedLatchOutput,StartTick)
    MainLogic.Connect(StartPulse,EnableStarted)
    MainLogic.Connect(InstantStartPulse,StartPulse)

    with open(File,"r") as File:
        Code = File.readlines()

    while len(Code) != 0:
        Line = Code.pop(0).removesuffix("\n")
        LineNum += 1
        Args = Line.replace("\t","    ").lstrip(" ").split(" ")
        if Args[0].lower() == "output":
            Name = Args[1]
            Latch, Enable, Disable, Output = MakeLatch()
            MainLogic.AddGroup(Latch)
            Outputs[Name] = {"Enable": Enable,
                             "Disable": Disable,
                             "Output": Output}
        if Args[0].lower() == "outputlinked":
            Name = Args[1]
            Output = Gate("Or")
            MainLogic.AddGate(Output)
            Outputs[Name] = {"Output": Output}
        if Args[0].lower() == "bool":
            Name = Args[1]
            Latch, Enable, Disable, Output = MakeLatch()
            MainLogic.AddGroup(Latch)
            Bools[Name] = {"Enable": Enable,
                           "Disable": Disable,
                           "Output": Output}
        if Args[0].lower() == "condition":
            Expression, After = ParseExpression(" ".join(Args[2:]))
            ConditionGate = BuildExpression(Expression)
            Conditions[Args[1]] = ConditionGate
        if Args[0].lower() == "input" or Args[0].lower() == "buttoninput":
            Name = Args[1]

            if Args[0].lower() == "buttoninput":
                TickExtender, RawInputGate, ProcessedInput = MakeTickExtender()
                MainLogic.AddGroup(TickExtender)

                Inputs[Name] = {"RawInput": RawInputGate,
                                "ProcessedInput": ProcessedInput}
            else:
                RawInputGate = Gate("Or")
                MainLogic.AddGate(RawInputGate)

                Inputs[Name] = {"RawInput": RawInputGate,
                                "ProcessedInput": RawInputGate}
        if Args[0].lower() == "link":
            FoundReference = False
            Reference = None
            if Args[1] in Conditions.keys():
                FoundReference = True
                Reference = Conditions[Args[1]]
            elif Args[1] in Bools.keys():
                FoundReference = True
                Reference = Bools[Args[1]]["Output"]
            elif Args[1] in Inputs.keys():
                FoundReference = True
                Reference = Inputs[Args[1]]["RawInput"]
            elif Args[1] in Outputs.keys():
                FoundReference = True
                Reference = Outputs[Args[1]]["Output"]
            if Reference == None:
                raise NameError("What is "+Args[1])
            MainLogic.Connect(Reference,Outputs[Args[2]]["Output"])
        # When <Event (Button press)> Run <Function>        Run an event when a button is pressed
        if Args[0].lower() == "when":
            Triggers.append({"Trigger": Args[1],
                             "Action": Args[3]})
            if Args[2].lower() != "run":
                raise ValueError("Invalid Arguments to Wait: "+str(Args))
        # Run <Event>        Run an event on start
        if Args[0].lower() == "run":
            Triggers.append({"TriggerGate": StartPulse,
                             "Action": Args[1]})
        # Function <Name>: <CODE> Done        Define a function
        if Args[0].lower() == "function":
            FunctionName = Args[1].removesuffix(":")
            Function = LogicGroup()
            FunctionStartGate = Gate("Or")
            Function.AddGate(FunctionStartGate)

            CurrentGate = FunctionStartGate
            while len(Code) != 0:
                FuncLine = Code.pop(0).removesuffix("\n")
                LineNum += 1
                Args = FuncLine.replace("\t","    ").lstrip(" ").split(" ")
                if Args[0].lower() == "done":
                    break
                if Args[0].lower() == "enable":
                    if Args[1] in Bools.keys():
                        Function.Connect(CurrentGate,Bools[Args[1]]["Enable"])
                    elif Args[1] in Outputs.keys():
                        Function.Connect(CurrentGate,Outputs[Args[1]]["Enable"])
                    else:
                        raise NameError(Args[1]+" is not defined")
                if Args[0].lower() == "disable":
                    if Args[1] in Bools.keys():
                        Function.Connect(CurrentGate,Bools[Args[1]]["Disable"])
                    elif Args[1] in Outputs.keys():
                        Function.Connect(CurrentGate,Outputs[Args[1]]["Disable"])
                    else:
                        raise NameError(Args[1]+" is not defined")
                if Args[0].lower() == "wait":
                    Seconds = 0
                    Ticks = 0
                    if Args[2].lower() == "seconds":
                        Seconds = int(Args[1])
                    if Args[2].lower() == "ticks":
                        Ticks = int(Args[1])
                    if len(Args) > 3:
                        if Args[4].lower() == "seconds":
                            Seconds = int(Args[3])
                        if Args[4].lower() == "ticks":
                            Ticks = int(Args[3])
                    WaitTimer = Timer(Seconds=Seconds,Ticks=Ticks)
                    Function.AddGate(WaitTimer)
                    Function.Connect(CurrentGate,WaitTimer)
                    CurrentGate = WaitTimer
                if Args[0].lower() == "run":
                    Triggers.append({"TriggerGate": CurrentGate,
                                     "Action": Args[1]})
                if Args[0].lower() == "if":
                    AndGate = Gate("And")
                    MainLogic.AddGate(AndGate)
                    MainLogic.Connect(CurrentGate,AndGate)
                    
                    if Args[1] in Conditions.keys():
                        ConditionGate = Conditions[Args[1]]
                        AfterArgs = Args[2:]
                        MainLogic.Connect(ConditionGate,AndGate)
                    else:
                        print("Parsing: "+" ".join(Args[1:]))
                        Expression, AfterText = ParseExpression(" ".join(Args[1:]))
                        print(Expression)
                        try:
                            ConditionGate = BuildExpression(Expression)
                        except ValueError as Error:
                            raise ValueError("Line "+str(LineNum)+" "+str(Error))
                        MainLogic.Connect(ConditionGate,AndGate)
                        AfterArgs = AfterText.lstrip(" ").split(" ")

                    if AfterArgs[0].lower() == "run":
                        print("Adding Trigger")
                        Triggers.append({"TriggerGate": AndGate,
                                         "Action": AfterArgs[1]})
                    if AfterArgs[0].lower() == "continue":
                        CurrentGate = AndGate
                else:
                    SyntaxError("Unknown thing on line "+str(LineNum))
            else:
                raise SyntaxError("Unknown thing on line "+str(LineNum))
                        
            MainLogic.AddGroup(Function)
            Functions[FunctionName] = {"StartGate": FunctionStartGate}

    #print(Functions.keys())

    print(f"{len(Triggers)} Triggers")
    for Trigger in Triggers:
        TriggerAction = Trigger["Action"]
        if "Trigger" in Trigger:
            TriggerTrigger = Trigger["Trigger"]
            MainLogic.Connect(Inputs[TriggerTrigger]["ProcessedInput"],Functions[TriggerAction]["StartGate"])
        elif "TriggerGate" in Trigger:
            TriggerGate = Trigger["TriggerGate"]
            print(TriggerAction)
            MainLogic.Connect(TriggerGate,Functions[TriggerAction]["StartGate"])
        print("Connecting Trigger")
    
    Bp = Blueprint()
    Bp.AddLogicGroup(MainLogic)
    Bp.Arrange(Inputs,Outputs,ArrangeCube)

    for Object in Bp.Objects:
        if Object["shapeId"] == "8f7fd0e7-c46e-4944-a414-7ce2437bb30f" and Object["pos"]["z"] != 0:
            Object["pos"]["z"] -= 1
            print("Shifting")

    for Output in Outputs.keys():
##        Outputs[Output]["Output"].Data["pos"] = {"x": X,
##                                                 "y": 0,
##                                                 "z": 1}
        Outputs[Output]["Output"].Data["color"] = "00FF00" 
    for Input in Inputs.keys():
##        Inputs[Input]["RawInput"].Data["pos"] = {"x": X,
##                                                 "y": 1,
##                                                 "z": 1}
        Inputs[Input]["RawInput"].Data["color"] = "00FFFF"
    
    Bp.Save("/home/toby/.steam/steam/steamapps/compatdata/387990/pfx/drive_c/users/steamuser/AppData/Roaming/Axolot Games/Scrap Mechanic/User/User_76561198894554628/Blueprints/8efc718a-4587-481f-8270-77dbe9d1de56/blueprint.json")
    #print(Bp.Export())
    Bp.ShowStats()
    #Bp.Save("blueprint.json")

    Gates = []
    for Object in Bp.Objects:
        #print(Object)
        RGB = HexToRGB(Object["color"])
        Gates.append([False,(RGB[0],RGB[1],RGB[2]),(Object["pos"]["x"],Object["pos"]["y"],Object["pos"]["z"])])
    import LogicSimulator
    LogicSimulator.ShowGates(Gates)

Compile("BomberAirship.txt")
