import maya.cmds as cmds

global legCounter 
legCounter = 1

global jointCounter 
jointCounter = 0 

#reset and reuse once leg is done
global sphereList
sphereList = [] 
global jointList
jointList = []
global nurbList
nurbList = []
global groupList
groupList = []

global NAMES
NAMES = ["shoulder", "knee", "foot"]

def UIWindow():
    #make sure everything is clear and reset on start
    legCounter = 1
    jointCounter = 0
    sphereList.clear()
    jointList.clear()
    nurbList.clear()
    groupList.clear()
    
    cmds.window(width=200)
    cmds.columnLayout(adjustableColumn=True)
    
    cmds.text(label="Autorig IK Leg \n", font="boldLabelFont", align='center')
    cmds.text(label="  1. Click 'Add Joint' button and place the first sphere at the shoulder of the leg.\n", align='left')
    cmds.text(label="\tTip: Use the keyboard shortcut 'w' to go into translate mode.\n", align='left')
    cmds.text(label="  2. Click 'Add Joint' button and place the second sphere at the knee of the same leg.\n", align='left')
    cmds.text(label="  3. Click 'Add Joint' button and place the third sphere at the foot of the same leg.\n", align='left')
    cmds.button(label="Add Joint", command=AddJointButton)
    cmds.text(label="\n  4. Click 'Autorig Leg' once done with step #1-3.\n", align='left')
    cmds.text(label="\tNote: You won't be able to create more joints for another leg until you autorig the current leg.\n", align='left')
    cmds.button(label="Autorig Leg", command=AutorigLegButton)
    cmds.text(label="\n  5. Repeat Steps #1-4 for each leg needed.\n", align='left')
    cmds.showWindow()

def AddJointButton(self):
    global jointCounter
    if (jointCounter < 3):
        #ex name: leg1_shoulder_placeholder, leg2_knee_placeholder
        name = "leg" + str(legCounter) + "_" + NAMES[jointCounter] + "_placeholder" 
        s = cmds.polySphere(r=0.3, n=name)
        global sphereList
        sphereList.append(s[0])
        jointCounter = jointCounter + 1
    else:
        print("There are already 3 joints! Autorig current leg first.")

def AutorigLegButton(self):
    global jointCounter
    global legCounter
    
    #start process if there are 3 placeholders
    if (jointCounter == 3):
        #reset jointCounter
        jointCounter = 0
        
        #make joint chain
        CreateJointChain()
        
        #makes nurb controls
        CreateNurbControls()
        
        #adds constraints
        AddConstraints()
        
        #makes IK Handle
        CreateIKHandle()
        
        #clean up hierarchy
        CleanUp()
        
        #reset for next leg
        legCounter += 1
        sphereList.clear()
        jointList.clear()
        nurbList.clear()
        groupList.clear()
        
    else:
        print("Not enough to joints to make IK Handle")
    
def CreateJointChain():
    if (len(sphereList) == 3):
        nameIdx = 0
        for s in sphereList:
            cmds.select(s)
            global jointList
            
            x = cmds.getAttr("%s.translateX" %s)
            y = cmds.getAttr("%s.translateY" %s)
            z = cmds.getAttr("%s.translateZ" %s)
            
            #ex name: leg1_foot_joint
            name = "leg" + str(legCounter) + "_" + NAMES[nameIdx] + "_joint"
            j = cmds.joint(position=[x, y, z], n = name)
            
            #unparent from sphere
            cmds.parent(s, j, w=1)
            
            #add joint to list
            jointList.append(j)
            
            #delete placeholder sphere
            cmds.delete(s)
            nameIdx += 1
        
        #reset
        jointCounter = 0
        sphereList.clear()
        
        #freeze transformation of joints
        for j in jointList:
            cmds.makeIdentity(j, apply=True)
   
    else:
        print("You don't have 3 joints yet.")

def CreateNurbControls():
    nameIdx = 0
    for i in range(1, 3):
        cmds.select(jointList[i])
        global nurbList
        
        x = cmds.getAttr("%s.translateX" %jointList[i])
        y = cmds.getAttr("%s.translateY" %jointList[i])
        z = cmds.getAttr("%s.translateZ" %jointList[i])
        
        #ex name: leg1_foot_nurb
        name = "leg" + str(legCounter) + "_" + NAMES[nameIdx] + "_nurb"
        n = cmds.circle(c=(x, y, z), n = name)
        
        #center pivot point
        cmds.xform(n, centerPivots=True)
        
        #add nurb control to list
        nurbList.append(n[0])
        nameIdx += 1
    
    #freeze transformation of nurbs
    for n in nurbList:
        cmds.makeIdentity(n, apply=True)
    
    #parent the joints
    cmds.parent(jointList[1], jointList[0])
    cmds.parent(jointList[2], jointList[1]) 
    
    
def AddConstraints():
    #put nurbs into padding groups
    nameIdx = 1
    for nurb in nurbList:
        #ex name: leg1_knee_nurb-group
        name = "leg" + str(legCounter) + "_" + NAMES[nameIdx] + "_nurb-group"
        g = cmds.group(nurb, n=name)
        groupList.append(g)
        nameIdx += 1
        
    #freeze transformation of nurbs group
    for n in groupList:
        cmds.makeIdentity(n, apply=True)
    
    #constrain foot nurb and foot joint
    cmds.orientConstraint(nurbList[1], jointList[2])
        
def CreateIKHandle():
    ikName = "leg" + str(legCounter) + "_ikHandle"
    cmds.ikHandle(n=ikName, sj=jointList[0], ee=jointList[2])
    
    #pole vector constraint knee and ikhandle
    name = "leg" + str(legCounter) + "_poleVector"
    cmds.poleVectorConstraint(nurbList[0], ikName, n=name)
    
    #point constraint foot and ikhandle
    name = "leg" + str(legCounter) + "_pointConstraint"
    cmds.pointConstraint(nurbList[1], ikName, n=name)
        
def CleanUp():
    #group controls together
    groupName = "leg" + str(legCounter) + "_controls"
    item1 = groupList[0] #"leg" + str(legCounter) + "_knee_nurb-group" 
    item2 = groupList[1] #"leg" + str(legCounter) + "_foot_nurb-group" 
    item3 = "leg" + str(legCounter) + "_ikHandle"
    cmds.group(item1, item2, item3, n=groupName)
    
UIWindow()
