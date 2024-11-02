

class Region:
    def __init__(self, minimum_y,maximum_y,minimum_x,maximum_x):
        self.minimum_y=minimum_y
        self.maximum_y=maximum_y
        self.minimum_x=minimum_x
        self.maximum_x=maximum_x
    
    def update_params(self,new_gate):
        if self.maximum_y!=None and self.minimum_y!=None:
            if new_gate.x==self.maximum_x:
                self.maximum_x=new_gate.x+new_gate.width
            else:
                self.minimum_x=new_gate.x
            return 0
        elif self.maximum_y==None:
            self.maximum_y=new_gate.y+new_gate.height
            self.minimum_x=new_gate.x
            self.maximum_x=new_gate.x+new_gate.width
            return 1
        else:
            self.minimum_y=new_gate.y
            self.minimum_x=new_gate.x
            self.maximum_x=new_gate.x + new_gate.width
            return -1

class Gate:
    def __init__(self,id,width,height) -> None:
        self.id=id
        self.width=width
        self.height=height
        self.x=0
        self.y=0
        self.pinCoordinates={}
        self.connected_gates ={}
        self.added=False

    def pin(self,pin_id,x,y):
        self.pinCoordinates[pin_id]=(x,y)

    def wire(self,pin_id,other_gate,other_pin):
        if other_gate in self.connected_gates:
            self.connected_gates[other_gate].append((pin_id,other_pin))
        else:
            self.connected_gates[other_gate]=[(pin_id,other_pin)]

    def __repr__(self) -> str:
        return f'|{self.id} , {self.x,self.y} , h: {self.height} w:{self.width}  |'

class Part:
    def __init__(self,min_x,min_y,max_x,max_y,part_gates) -> None:
        self.min_x=min_x
        self.min_y=min_y
        self.max_x=max_x
        self.max_y=max_y
        self.part_gates=part_gates

def compare_wirelength(gate1,gate2,minimum):
    length=0
    for pin1,pin2 in gate1.connected_gates[gate2.id]:
        length += abs(gate1.x+gate1.pinCoordinates[pin1][0]-gate2.x-gate2.pinCoordinates[pin2][0]) + abs(gate1.y+gate1.pinCoordinates[pin1][1]- gate2.y -gate2.pinCoordinates[pin2][1])
    if minimum==None or length < minimum:
        return length
    return None

def gates_placer(pivot):
    global data,part_gates,boundaries
    part_gates.append(pivot)
    for gate_id in pivot.connected_gates:
        gate=None
        for it in data:
            if it.id==gate_id:
                gate=it
                break
        if not gate.added:
            # place_gate(gate, pivot, boundaries)
            minimum = None
            minWire_x = None
            minWire_y = None
            minRegion=None
            gate.added=True
            for region in boundaries:
                result=None
                if region.maximum_y==None:
                    gate.x=pivot.x + (pivot.width - gate.width)//2
                    gate.y=region.minimum_y
                    result=compare_wirelength(pivot,gate,minimum)

                elif region.minimum_y==None:
                    gate.x=pivot.x + (pivot.width - gate.width)//2
                    gate.y=region.maximum_y-gate.height
                    result=compare_wirelength(pivot,gate,minimum)

                elif region.maximum_y>= gate.height+region.minimum_y :
                    gate.x = region.maximum_x
                    gate.y = (region.minimum_y + region.maximum_y - gate.height)//2 
                    result=compare_wirelength(pivot,gate,minimum)

                    if result!=None:
                        minimum = result
                        minRegion=region
                        minWire_x = gate.x
                        minWire_y=gate.y

                    gate.x = region.minimum_x - gate.width
                    gate.y = (region.minimum_y + region.maximum_y - gate.height)//2 
                    result=compare_wirelength(pivot,gate,minimum)

                if result!=None:
                    minimum = result
                    minRegion=region
                    minWire_x = gate.x
                    minWire_y=gate.y
                
            gate.x=minWire_x 
            gate.y=minWire_y 
            placed=minRegion.update_params(new_gate=gate)
            if placed==1:   
                boundaries.append(Region(minRegion.maximum_y,None,None,None))
            elif placed==-1:
                boundaries.append(Region(None,minRegion.minimum_y,None,None))

            gates_placer(gate)
    return part_gates



def parse_gate(input_data, data):
    id = int(input_data[0][1:])
    w = int(input_data[1])
    h = int(input_data[2])
    gate = Gate(id, w, h)
    data.append(gate)

def parse_pins(input_data, data):
    id = int(input_data[1][1:])
    coordinates = input_data[2:]
    input_pin_id = 1
    for i in range(0, len(coordinates), 2):
        x, y = int(coordinates[i]), int(coordinates[i + 1])
        data[id - 1].pin(input_pin_id, x, y)
        input_pin_id += 1

def parse_wire(input_data, data):
    gate1, pin1 = input_data[1].split('.')
    gate2, pin2 = input_data[2].split('.')
    id1 = int(gate1[1:])
    id2 = int(gate2[1:])
    pID1 = int(pin1[1:])
    pID2 = int(pin2[1:])
    
    data[id1 - 1].wire(pID1, id2, pID2)
    data[id2 - 1].wire(pID2, id1, pID1)

data = []
parts=[]

file = open('input.txt', 'r')
lines = file.readlines()
file.close() 

for line in lines:
    input_data = line.split()
    if input_data[0][0] == 'g':
        parse_gate(input_data, data)
    elif input_data[0] == 'pins':
        parse_pins(input_data, data)
    elif input_data[0] == 'wire':
        parse_wire(input_data, data)

data.sort(key=lambda gate : len(gate.connected_gates),reverse=True)
    

for gate in data:
    gate.connected_gates=dict(sorted(gate.connected_gates.items(),key=lambda item: len(item[1]),reverse=True))  
    if not gate.added:
        gate.added=True
        min_x=None
        min_y=None
        max_x=None
        max_y=None
        boundaries=[Region(0,gate.height,0,gate.width),Region(None,0,None,None),Region(gate.height,None,None,None)]
        part_gates=[]
        gates_placer(gate)
        for gate in part_gates:
            if min_x==None or gate.x< min_x:
                min_x=gate.x
            if max_x==None or gate.x +gate.width> max_x:
                max_x=gate.x+gate.width
            if min_y==None or gate.y < min_y:
                min_y = gate.y
            if max_y==None or gate.y + gate.height> max_y:
                max_y = gate.y+gate.height

        parts.append(Part(min_x,min_y,max_x,max_y,part_gates))


max_x=None
max_y=0
for part in parts:
    for gate in part.part_gates:
        gate.x-=part.min_x
        gate.y=gate.y -part.min_y + max_y
    max_y=max_y+part.max_y - part.min_y 
    if max_x==None or part.max_x>max_x:
        max_x=part.max_x-part.min_x


#calculate total wirelength
total_wire_length=0
for i in range(len(data)):
    for j in range(i,len(data)):
        gate_1=data[i]
        gate_2=data[j]
        if gate_2.id not in gate_1.connected_gates:
            continue
        for pin1,pin2 in gate_1.connected_gates[gate_2.id]:
            total_wire_length += abs(gate_1.x+gate_1.pinCoordinates[pin1][0]-gate_2.x-gate_2.pinCoordinates[pin2][0]) + abs(gate_1.y+gate_1.pinCoordinates[pin1][1]- gate_2.y -gate_2.pinCoordinates[pin2][1])
        


data.sort(key=lambda x: x.id)
file = open("output.txt", "w")

file.write(f'bounding_box {max_x} {max_y}\n')

for gate in data:
    file.write(f'g{gate.id} {gate.x} {gate.y}\n')
file.write(f'{total_wire_length}\n')

file.close()

    
