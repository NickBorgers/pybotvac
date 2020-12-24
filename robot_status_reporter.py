from pybotvac import Robot
import os
import json
import time
import requests

robot_identity_raw = open(os.path.expanduser("~/.robot_identity.json")).read()
robot_identity = json.loads(robot_identity_raw)
robot = Robot(serial=robot_identity["serial"], secret=robot_identity["secret"], name=robot_identity["name"], traits=robot_identity["traits"])

while True:
  robot_state = robot.state
  if robot_state['details']['isDocked']:
    print("Neato is docked")
    if robot.state['details']['charge'] >= 50:
      print("Neato is charged")
      print("Neato is ready")
      requests.get('http://10.2.3.13/cgi-bin/neato-ready')
    else:
      print("Neato is not ready, because it is not charged")
      requests.get('http://10.2.3.13/cgi-bin/neato-not-ready')
  else:
    print("Neato is not ready, because it is not docked")
    requests.get('http://10.2.3.13/cgi-bin/neato-not-ready')
  time.sleep(60)
