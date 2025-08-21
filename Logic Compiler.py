import json
import random
import copy

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
            Pos += 1
            CurrentGate.Data["controller"] = {"active": CurrentGate.Active,
                                       "controllers": None,
                                       "id": CurrentGate.ID,
                                       "joints": None}
            if isinstance(CurrentGate,Gate):
                print("Gate")
                CurrentGate.Data["shapeId"] = ShapeIDs["Logic Gate"]
                CurrentGate.Data["controller"]["mode"] = CurrentGate.Type
            if isinstance(CurrentGate,Timer):
                print("Timer")
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

def Compile(File):
    MainLogic = LogicGroup()

    Outputs = {}
    Inputs = {}

    Functions = {}
    Triggers = []

    with open(File,"r") as File:
        Code = File.readlines()

    while len(Code) != 0:
        Line = Code.pop(0).removesuffix("\n")
        Args = Line.replace("\t","    ").lstrip(" ").split(" ")
        if Args[0].lower() == "output":
            Name = Args[1]
            Latch, Enable, Disable, Output = MakeLatch()
            MainLogic.AddGroup(Latch)
            Outputs[Name] = {"Enable": Enable,
                             "Disable": Disable,
                             "Output": Output}
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
        if Args[0].lower() == "when":
            Triggers.append({"Trigger": Args[1],
                             "Action": Args[3]})
            if Args[2].lower() != "run":
                raise ValueError("Invalid Arguments to Wait: "+str(Args))
        if Args[0].lower() == "function":
            FunctionName = Args[1].removesuffix(":")
            Function = LogicGroup()
            FunctionStartGate = Gate("Or")
            Function.AddGate(FunctionStartGate)

            CurrentGate = FunctionStartGate
            while len(Code) != 0:
                FuncLine = Code.pop(0).removesuffix("\n")
                Args = FuncLine.replace("\t","    ").lstrip(" ").split(" ")
                if Args[0].lower() == "done":
                    break
                if Args[0].lower() == "enable":
                    Function.Connect(CurrentGate,Outputs[Args[1]]["Enable"])
                if Args[0].lower() == "disable":
                    Function.Connect(CurrentGate,Outputs[Args[1]]["Disable"])
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

            MainLogic.AddGroup(Function)
            Functions[FunctionName] = {"StartGate": FunctionStartGate}

    #print(Functions.keys())

    for Trigger in Triggers:
        TriggerTrigger = Trigger["Trigger"]
        TriggerAction = Trigger["Action"]
        MainLogic.Connect(Inputs[TriggerTrigger]["ProcessedInput"],Functions[TriggerAction]["StartGate"])
    
    Bp = Blueprint()
    Bp.AddLogicGroup(MainLogic)

    X = 0
    for Output in Outputs.keys():
        Outputs[Output]["Output"].Data["pos"] = {"x": X,
                                                 "y": 0,
                                                 "z": 1}
        Outputs[Output]["Output"].Data["color"] = "00FF00" 
        X += 1
    X = 0
    for Input in Inputs.keys():
        Inputs[Input]["RawInput"].Data["pos"] = {"x": X,
                                                 "y": 1,
                                                 "z": 1}
        Inputs[Input]["RawInput"].Data["color"] = "00FFFF"
        X += 1
    
    #Bp.Save("/home/toby/.steam/steam/steamapps/compatdata/387990/pfx/drive_c/users/steamuser/AppData/Roaming/Axolot Games/Scrap Mechanic/User/User_76561198894554628/Blueprints/8efc718a-4587-481f-8270-77dbe9d1de56/blueprint.json")
    #print(Bp.Export())
    #Bp.ShowStats()
    Bp.Save("blueprint.json")

Compile("Rocket.txt")
