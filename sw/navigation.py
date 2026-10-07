"""
Operation of Team 110 IDP robot is controlled by a continuous list consisted of
one of the following 9 moves.

The following 4 moves are called whenever the robot detects a junction:
    LT: left turn (90 deg)
    RT: right turn (90 deg)
    IG: ignore current junction
    FL: flourish

The following 5 moves are called whenever the robot finishes the previous move:
    LD: load (recalibrates actuator, turns on qr code detector, reads qr code and loads box)
    LUL: unload (unloads box at a lower rack)
    UUL: unload (unloads box at an upper rack)
    RO: rotate (180 deg)

The ST move is called only at the start when the robot needs to move when both line sensors are dark
    ST: straight (move straight until both line sensors turn on and both turn back off again)
"""

def low_unload(R,N,lst):
    # Lower rack A is in decreasing order (6 -> 1), so 6-N 'ignores' are needed
    if R == 'A':
        lst.extend(["IG"]*(6-N)+["RT","LUL","RO","LT"]+["IG"]*(6-N))
    # Lower rack B is in increasing order (1 -> 6), so N-1 'ignores' are needed
    elif R == 'B':
        lst.extend(["IG"]*(N-1)+["LT","LUL","RO","RT"]+["IG"]*(N-1))
    return lst

def up_unload(R,N,lst):
    # Upper rack A is in increasing order (1 -> 6), so N-1 'ignores' are needed
    if R == 'A':
        lst.extend(["IG"]*(N-1)+["LT","UUL","RO","RT"]+["IG"]*(N-1)+["LT"]*2)
    # Upper rack B is in decreasing order (6 -> 1), so 6-N 'ignores' are needed
    elif R == 'B':
        lst.extend(["IG"]*(6-N)+["RT","UUL","RO","LT"]+["IG"]*(6-N)+["RT"]*2)
    return lst

# QRinput is value read by QR code reader. Example: "Rack A, Upper, 4" or "Rack B, Lower, 2"
def navigation_moves(QRinput, bay, set_moves):
    moves = set_moves
    rack = QRinput[5] # 5th character of QRinput is either 'A' or 'B'
    upOrLow = QRinput[8] # 8th character of QR input is either 'U' or 'L'
    num = int(QRinput[15]) # 15th character of QR input is one of six integers 1 ~ 6
    returnPoint = ""
    
    if bay == 1: # Robot started at bay 1
        if upOrLow == "L":
            if rack == "A":
                # If robot from bay 1 should go to lower rack A, just go straight (IGnore)
                moves.append("IG")
            elif rack == "B":
                # If robot from bay 1 should go to lower rack B, it needs a RT
                # followed by 3 IGs and a LT.
                moves.extend(["RT"]+["IG"]*3+["LT"])
        elif upOrLow == "U":
            # If robot from bay 1 should go to an upper rack, it needs 8 IGs to pass all the lower
            # racks then 2 RTs to position itself just before the ramp.
            moves.extend(["IG"]*8+["RT"]*2)

    elif bay == 2: # Robot started at bay 2
        if upOrLow == "L":
            if rack == "A":
                # If robot from bay 2 should go to lower rack A, it needs a LT and a RT
                moves.extend(["LT","RT"])
            elif rack == "B":
                # If robot from bay 2 should go to lower rack B, it needs a RT, then 2 IGs and a LT
                moves.extend(["RT","IG","IG","LT"])
        elif upOrLow == "U":
            # If robot from bay 2 should go to an upper rack, it needs a LT and a RT followed by 7 IGs
            # to pass all the lower racks followed by 2 RTs to position itself just before the ramp.
            moves.extend(["LT","RT"]+["IG"]*7+["RT"]*2)

    elif bay == 3: # Robot started at bay 3
        if upOrLow == "L":
            if rack == "A":
                # If robot from bay 3 should go to lower rack A, it needs a LT, then 2 IGs and a RT
                moves.extend(["LT","IG","IG","RT"])
            elif rack == "B":
                # If robot from bay 3 should go to lower rack B, it needs a RT and a LT
                moves.extend(["RT","LT"])
        elif upOrLow == "U":
            # If robot from bay 3 should go to an upper rack, it needs a RT and a LT followed by 7 IGs
            # to pass all the lower racks followed by 2 LTs to position itself just before the ramp.
            moves.extend(["RT","LT"]+["IG"]*7+["LT"]*2)
            
    elif bay == 4: # Robot started at bay 4
        if upOrLow == "L":
            if rack == "A":
                # If robot from bay 4 should go to lower rack A, it needs a LT
                # followed by 3 IGs and a RT
                moves.extend(["LT"]+["IG"]*3+["RT"])
            elif rack == "B":
                # If robot from bay 4 should go to lower rack B, just go straight (IGnore)
                moves.append("IG")
        elif upOrLow == "U":
            # If robot from bay 4 should go to an upper rack, it needs 8 IGs to pass all the lower
            # racks then 2 LTs to position itself just before the ramp.
            moves.extend(["IG"]*8+["LT"]*2)

    if upOrLow == 'L':
        # Appends set of moves at lower rack
        newLst = low_unload(rack,num,moves)
        moves = newLst
        # Now list "moves" contains set of moves until it has successfully unloaded the box
        # and got out of the region of consecutive junctions on the lower rack
        # Variable "returnPoint" is either "left" or "right" depending on which side it escaped
        # the lower rack. In the case of the lower racks, returnPoint is simply "left" if rack A
        # and "right" if rack B.
        if rack == 'A':
            returnPoint = "left"
        elif rack == 'B':
            returnPoint = "right"
        # Now robot is at returning point (either left or right)

    elif upOrLow == 'U':
        # Current set of moves puts robot right in front of the ramp (if qr code read upper ramp)
        # If upper rack A, it needs 2 RTs. If upper rack B, it needs 2 LTs.
        if rack == "A":
            moves.extend(["RT","RT"])
        elif rack == "B":
            moves.extend(["LT","LT"])
        # Now robot has unloaded the box from upper rack, got out of the region of consecutive
        # junctions, and now is at the top of the ramp ready for decline.
        newLst = up_unload(rack,num,moves)
        moves = newLst
        # Now robot has unloaded the box, got out of the region of consecutive junctions, and is at
        # the top of the ramp ready for decline.
        # If current bay is 1, next bay is 2. In this case returning to the left (rack A side) is
        # the quicker path. If current bay is 2 or 3, next bay is 3 or 4. In this case returning to the
        # right (rack B side) is the quicker path.
        if bay == 1:
            moves.extend(["LT","LT"])
            returnPoint = "left"
        elif bay == 2 or bay == 3 or bay == 4:
            moves.extend(["RT","RT"])
            returnPoint = "right"
        # Needs 7 ignores to get to the returning point (ignore all the junctions at the lower rack)
        for _ in range(7):
            moves.append("IG")
        # Now robot is at returning point (either left or right)
    
    next_bay = bay + 1

    # Depending of the position of the returning point (left or right) and the next bay, the list of
    # moves the robot has to execute is different. The following set of code appends the appropriate
    # list of moves the robot needs in order to load the next box. Notice that if the next bay is 5,
    # the current bay is 4, so robot has to stop, which means it does not have to load another box.
    if returnPoint == "left":
        if next_bay == 2:
            moves.extend(["LT","RT","LD","RO"])
        elif next_bay == 3:
            moves.extend(["LT","IG","IG","RT","LD","RO"])
        elif next_bay == 4:
            moves.extend(["LT","IG","IG","IG","RT","LD","RO"])
        elif next_bay == 5:
            moves.extend(["LT","IG","RT","FL"])

    elif returnPoint == "right":
        if next_bay == 2:
            moves.extend(["RT","IG","IG","LT","LD","RO"])
        elif next_bay == 3:
            moves.extend(["RT","LT","LD","RO"])
        elif next_bay == 4:
            moves.extend(["IG","LD","RO"])
        elif next_bay == 5:
            moves.extend(["RT","IG","LT","FL"])

    return moves
