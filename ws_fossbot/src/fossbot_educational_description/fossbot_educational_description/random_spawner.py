import rclpy
from rclpy.node import Node
import random
import math
import os
import subprocess
import tempfile
from ament_index_python.packages import get_package_share_directory

# Define a dictionary of colors with their corresponding RGB values
COLORS = {
  "red": [1.0, 0.0, 0.0], "green": [0.0, 1.0, 0.0], "blue": [0.0, 0.0, 1.0],
  "yellow": [1.0, 1.0, 0.0], "orange": [1.0, 0.5, 0.0], "purple": [0.5, 0.0, 0.5],
  "pink": [1.0, 0.0, 1.0], "cyan": [0.0, 1.0, 1.0], "white": [1.0, 1.0, 1.0],
  "black": [0.0, 0.0, 0.0], "gray": [0.5, 0.5, 0.5], "brown": [0.6, 0.3, 0.1],
  "dark_green": [0.0, 0.4, 0.0], "dark_blue": [0.0, 0.0, 0.4],
  "dark_red": [0.4, 0.0, 0.0], "light_gray": [0.8, 0.8, 0.8]
}

# Define the catalog of objects with their corresponding STL files and available colors
OBJECT_CATALOG = {
  "cactus": {"stl": "cactus.stl", "colors": ["green", "dark_green"]},
  "cone": {"stl": "cone.stl", "colors": ["orange", "red", "yellow", "white"]},
  "hydrant": {"stl": "hydrant.stl", "colors": ["red", "yellow", "blue"]},
  "palette": {"stl": "palette.stl", "colors": ["brown", "gray", "light_gray"]},
  "traffic_light": {"stl": "traffic_light.stl", "colors": ["red", "yellow", "green", "black", "gray"]}
}

# Define safe inner bounding boxes based on the SDF files coordinates to prevent wall collisions
# Format: (min_x, max_x, min_y, max_y)
SPAWN_ZONES = [
    (0.0, 5.0, -3.0, 3.0),   # Room 1
    (7.0, 11.0, 1.0, 7.0),   # Room 2
    (1.0, 5.0, 5.0, 9.0),    # Room 3
    (-4.0, -2.5, 5.5, 9.0),  # Room 4
    (9.0, 12.0, 9.0, 9.5)    # Room 5
]

class RandomSpawnerNode(Node):
    def __init__(self):
        super().__init__('random_spawner')

        # Dynamically find the path to the installed STLs
        try:
            pkg_share = get_package_share_directory('fossbot_educational_description')
            default_stl_dir = os.path.join(pkg_share, 'worlds', 'objects')
        except Exception as e:
            self.get_logger().error(f"Could not find package fossbot_educational_description: {e}")
            default_stl_dir = ""

        # Declare ROS 2 Parameters
        self.declare_parameter('num_objects', 10)
        self.declare_parameter('seed', -1)
        self.declare_parameter('stl_dir', default_stl_dir) 
        
        # Get parameters
        self.num_objects = self.get_parameter('num_objects').get_parameter_value().integer_value
        self.seed = self.get_parameter('seed').get_parameter_value().integer_value
        self.stl_dir = self.get_parameter('stl_dir').get_parameter_value().string_value

        if not os.path.exists(self.stl_dir):
            self.get_logger().error(f"STL directory does not exist: {self.stl_dir}. Did you colcon build?")
            return

        # Setup random seed
        if self.seed != -1:
            random.seed(self.seed)
            self.get_logger().info(f"Using random seed: {self.seed}")

        # Remove old objects
        self.remove_old_objects()

        # Spawn new objects
        self.spawn_objects()

    def remove_old_objects(self):
        """ Clears out previous objects spawned by this script """
        self.get_logger().info("Cleaning up old objects...")
        # Try to remove at most 50 objects, or num_objects + 10, whichever is larger
        max_to_clear = max(self.num_objects + 10, 50) 
        
        for i in range(max_to_clear):
            model_name = f"sim_obj_{i}"
            # Natively call the Gazebo service to remove the model
            cmd = [
                "gz", "service", "-s", "/world/default/remove",
                "--reqtype", "gz.msgs.Entity",
                "--reptype", "gz.msgs.Boolean",
                "--timeout", "1000",
                "--req", f'name: "{model_name}", type: MODEL'
            ]
            subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

    def generate_sdf_string(self, model_name, stl_file, color_rgb):
        """ Creates the XML representing the object """
        r, g, b = color_rgb
        absolute_stl_path = os.path.join(self.stl_dir, stl_file)
        
        sdf = f"""
        <?xml version="1.0" ?>
        <sdf version="1.10">
            <model name="{model_name}">
                <static>false</static>
                <link name="link">
                    <collision name="collision">
                        <geometry>
                            <mesh><uri>file://{absolute_stl_path}</uri></mesh>
                        </geometry>
                    </collision>
                    <visual name="visual">
                        <geometry>
                            <mesh><uri>file://{absolute_stl_path}</uri></mesh>
                        </geometry>
                        <material>
                            <ambient>{r} {g} {b} 1.0</ambient>
                            <diffuse>{r} {g} {b} 1.0</diffuse>
                        </material>
                    </visual>
                </link>
            </model>
        </sdf>
        """
        return sdf

    def spawn_objects(self):
        object_keys = list(OBJECT_CATALOG.keys())

        for i in range(self.num_objects):
            obj_type = random.choice(object_keys)
            obj_info = OBJECT_CATALOG[obj_type]
            
            color_name = random.choice(obj_info["colors"])
            color_rgb = COLORS[color_name]
            
            zone = random.choice(SPAWN_ZONES)
            x = random.uniform(zone[0], zone[1])
            y = random.uniform(zone[2], zone[3])
            yaw = random.uniform(0, 2 * math.pi)

            # Fixed naming convention
            model_name = f"sim_obj_{i}"
            
            self.get_logger().info(f"Spawning {color_name} {obj_type} as '{model_name}' at X:{x:.2f} Y:{y:.2f}")

            # Generate SDF string
            sdf_string = self.generate_sdf_string(model_name, obj_info["stl"], color_rgb)

            # Write the SDF string to a temporary file
            with tempfile.NamedTemporaryFile(mode='w', suffix='.sdf', delete=False) as f:
                f.write(sdf_string)
                tmp_file = f.name

            # Call the ros_gz_sim create utility
            cmd = [
                "ros2", "run", "ros_gz_sim", "create",
                "-name", model_name,
                "-file", tmp_file,
                "-x", str(x),
                "-y", str(y),
                "-z", "0.5",
                "-Y", str(yaw)
            ]
            
            subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            
            # Clean up the temporary file
            os.remove(tmp_file)

        self.get_logger().info("Finished spawning all objects.")


def main(args=None):
    rclpy.init(args=args)
    node = RandomSpawnerNode()
    node.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()