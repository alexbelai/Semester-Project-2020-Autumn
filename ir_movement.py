import pigpio
import ir_sensor
import threading
import motors

left = ir_sensor.IRSensor(23)#16
right = ir_sensor.IRSensor(25)#22

motor_left = motors.Motor(5,0)#29 & #27
motor_right = motors.Motor(6,26)#31 & #37

motors_list = []
motors_list.append(motor_left)
motors_list.append(motor_right)

controller = motors.MotorController(motors_list)



if(left.scan_line()==True and right.scan_line()==True):
        #Both white go forward
        controller.forward()
        

elif(left.scan_line()==False and right.scan_line()==True):
        #turn right
        controller.backward()


elif (left.scan_line()==True and right.scan_line()==False):
        #turn left

