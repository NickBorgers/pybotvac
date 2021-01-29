from http.server import BaseHTTPRequestHandler,HTTPServer
from pybotvac import Robot
import os
import json

robot_identity_raw = open(os.path.expanduser("~/.robot_identity.json")).read()
robot_identity = json.loads(robot_identity_raw)
cleaning_configuration_raw = open(os.path.expanduser("~/robot_cleaning_configuration.json")).read()
cleaning_configuration = json.loads(cleaning_configuration_raw)

if "persistent_maps" in robot_identity["traits"]:
  robot_identity["has_persistent_maps"] = True
else:
  robot_identity["has_persistent_maps"] = False

if cleaning_configuration["cleaning_mode"] == "turbo":
  cleaning_configuration["numeric_cleaning_mode"] = 2
else:
  cleaning_configuration["numeric_cleaning_mode"] = 1
  
if cleaning_configuration["navigation_mode"] == "extra care":
  cleaning_configuration["numeric_navigation_mode"] = 2
elif cleaning_configuration["navigation_mode"] == "deep":
  cleaning_configuration["numeric_navigation_mode"] = 3
else:
  cleaning_configuration["numeric_navigation_mode"] = 1
  
if robot_identity["has_persistent_maps"]:
  cleaning_configuration["numeric_category"] = 4
else:
  cleaning_configuration["numeric_category"] = 2

class myHandler(BaseHTTPRequestHandler):
  #Handler for the PUT requests to initiate cleaning
  def do_PUT(self):
    robot = Robot(serial=robot_identity["serial"], secret=robot_identity["secret"], name=robot_identity["name"], traits=robot_identity["traits"], has_persistent_maps=robot_identity["has_persistent_maps"])
    if "Quiet" in self.headers:
      quiet = int(self.headers["Quiet"])
      print("Cleaning mode being overriden")
      if quiet == 0:
        print("Cleaning will be loud")
        cleaning_configuration["numeric_cleaning_mode"] = 2
        cleaning_configuration["cleaning_mode"] = "turbo"
      else:
        print("Cleaning will be quiet")
        cleaning_configuration["numeric_cleaning_mode"] = 1
        cleaning_configuration["cleaning_mode"] = "quiet"
    if "ZoneToClean" in self.headers:
      boundary_id = self.headers["ZoneToClean"] 
      robot.start_cleaning(mode=cleaning_configuration["numeric_cleaning_mode"], navigation_mode=cleaning_configuration["numeric_navigation_mode"], category=cleaning_configuration["numeric_category"], map_id=robot_identity["map_id"], boundary_id=boundary_id)
      print("Cleaning zone: " + boundary_id)
    else:
      robot.start_cleaning(mode=cleaning_configuration["numeric_cleaning_mode"], navigation_mode=cleaning_configuration["numeric_navigation_mode"], category=cleaning_configuration["numeric_category"])
      print("Cleaning entire house")
    self.send_response(200)
    self.send_header('Content-type','application/json')
    self.end_headers()
    # Send the cleaning configuration used
    print("Full cleaning configuration: ")
    print(cleaning_configuration)
    self.wfile.write(str.encode(json.dumps(cleaning_configuration)))
    return

  #Handler for the GET requests to terminate cleaning mid-run
  def do_GET(self):
    robot = Robot(serial=robot_identity["serial"], secret=robot_identity["secret"], name=robot_identity["name"], traits=robot_identity["traits"], has_persistent_maps=robot_identity["has_persistent_maps"])
    robot.send_to_base()
    self.send_response(200)
    self.send_header('Content-type','text/plain')
    self.end_headers()
    print("Returning to base")
    self.wfile.write(str.encode("Returning to base"))
    return

def run(server_class=HTTPServer,
        handler_class=myHandler):
    server_address = ("10.2.3.13", 8080)
    httpd = server_class(server_address, handler_class)
    httpd.serve_forever()

def main():
  run()

if __name__ == "__main__":
  main()
