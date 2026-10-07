# Import python modules
from utime import sleep, ticks_ms, ticks_diff
from machine import Pin

amber = Pin(28, Pin.OUT)

def line_follow(lls, rls, lm, rm, ljs, rjs):
    crtime = 1500.0 # crtime = Counter Rotation Time; counter rotation time (s) = diff(ms) / crtime
    l = lls.value() # value of LLS(left line sensor) (0 if black surface, 1 if white surface)
    r = rls.value() # value of RLS(right line sensor)
    lj = ljs.value() # value of LJS(left junction sensor)
    rj = rjs.value() # value of RJS(right junction sensor)
    
    sleep(0.01)
    # Both LLS and RLS should stay in the white line to ensure that it is line following.
    # If LLS is 1(white) and RLS is 0(black), the robot must rotate right until both sensors become 1
    if l == 1 and r == 0:
        # Record the time when the robot was "out of track"
        sTime = ticks_ms()
        while l == 1 and r == 0:
            l = lls.value()
            r = rls.value()
            lj = ljs.value()
            rj = rjs.value()
            # detects junction while line following
            if lj == 1 or rj == 1:
                lm.off()
                rm.off()
                return 
            lm.off()
            rm.Forward()
        # Record the time when robot is "back on track"
        eTime = ticks_ms()
        # diff is eTime - sTime, which is basically the time it took the robot to get back on track
        # after it got out of track.
        diff = ticks_diff(eTime,sTime)
        rm.off()
        # Right motor is off, which means only the left motor is currently on. This makes the robot
        # rotate counter to the direction it went in order to get back on track. This ensures that
        # the robot retains a straight bearing after its effort to get back on track. Without this
        # mechanism, the direction of the robot becomes uncontrollable.
        lm.Forward()
        # Counter rotation for sleep time (s) = diff (ms) / crtime
        sleep(diff/crtime)
        lm.off()
        rm.off()
    
    # Same algorithm as l == 1 and r == 0, just symmetrical (refer to lines 18 ~ 47)
    elif l == 0 and r == 1:
        sTime = ticks_ms()
        while l == 0 and r == 1:
            l = lls.value()
            r = rls.value()
            lj = ljs.value()
            rj = rjs.value()
            if lj == 1 or rj == 1:
                lm.off()
                rm.off()
                return 
            lm.Forward()
            rm.off()
        eTime = ticks_ms()
        diff = ticks_diff(eTime,sTime)
        lm.off()
        rm.Forward()
        sleep(diff/crtime)
        lm.off()
        rm.off()
    
    # If both sensors are 1 (both are on white line), keep going forward
    elif l == 1 and r == 1:
        lm.Forward()
        rm.Forward()
    
    else:
        lm.off()
        rm.off()
