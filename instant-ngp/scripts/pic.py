#!/usr/bin/env python3

import os
import sys
import json
import time  # Import time for measuring execution time
import numpy as np
import requests  # Import requests for HTTP POST
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
import time
# Add the build directory to Python path
pyngp_path = os.path.abspath("./build")
sys.path.append(pyngp_path)

import pyngp as ngp  # noqa
import common


class TransformHandler(FileSystemEventHandler):
    def __init__(self, testbed, output_dir, resolution, server_url):
        super().__init__()
        self.testbed = testbed
        self.output_dir = output_dir
        self.resolution = resolution
        self.server_url = server_url
        self.first_pass = True
        self.previous_transformation = [0.0] * 6  # Initial transformation is zero

    def on_modified(self, event):
        """Handle file modifications."""
        if event.src_path.endswith("transform.json"):
            print(f"Detected change in {event.src_path}. Applying transformations...")
            self.process_transform_file(event.src_path)
            time.sleep(0.1)

    def process_transform_file(self, transform_file):
        """Process the JSON file, calculate the delta transformation, and send the rendered image."""
        try:
            with open(transform_file, "r") as f:
                transform_data = json.load(f)

            rotation = transform_data.get("rotation", [0.0, 0.0, 0.0]) * -1
            position = transform_data.get("position", [0.0, 0.0, 0.0]) * 0.5

            # Combine rotation and translation
            current_transformation = rotation + position

            # Calculate the delta transformation
            delta_transformation = [
                0.0 if self.first_pass else current_transformation[i] - self.previous_transformation[i] for i in range(6)
            ]
            self.first_pass = False

            # Update the previous transformation
            self.previous_transformation = current_transformation

            print(f"Delta transformation: {delta_transformation}")

            # Measure start time
            start_time = time.time()

            # Apply the delta transformation
            apply_transformations(self.testbed, delta_transformation)

            # Render and save the image
            output_file = os.path.join(self.output_dir, "rendered_frame.png")
            render_image(self.testbed, self.resolution, output_file)

            # Send the rendered image to the server
            send_image_to_server(output_file, self.server_url)

            # Measure end time and calculate elapsed time
            elapsed_time = time.time() - start_time
            print(f"Rendered image saved to {output_file}. Took {elapsed_time:.4f} seconds.")
        except Exception as e:
            print(f"Error processing transform file: {e}")


def render_image(testbed, resolution, output):
    """Renders the current scene to an image."""
    frame = testbed.render(resolution[0], resolution[1], spp=8, linear=True)
    common.write_image(output, frame)


def send_image_to_server(image_path, server_url):
    """Send the rendered image to the specified server."""
    try:
        with open(image_path, "rb") as img_file:
            files = {"file": img_file}
            response = requests.post(server_url, files=files)
            if response.status_code == 200:
                print(f"Image successfully sent to {server_url}. Response: {response.json()}")
            else:
                print(f"Failed to send image. Status code: {response.status_code}, Response: {response.text}")
    except Exception as e:
        print(f"Error sending image to server: {e}")


def apply_transformations(testbed, transformation):
    print(transformation)
    """
    Apply both rotation and translation to the NeRF camera.
    :param transformation: A list of 6 elements [rot_x, rot_y, rot_z, trans_x, trans_y, trans_z]
    """
    # Extract rotation and translation
    rotation = transformation[:3]
    translation = transformation[3:]

    # Compute rotation matrices
    radians = np.radians(rotation)
    rotation_matrix_x = np.array([
        [1, 0, 0],
        [0, np.cos(radians[0]), -np.sin(radians[0])],
        [0, np.sin(radians[0]), np.cos(radians[0])],
    ])
    rotation_matrix_y = np.array([
        [np.cos(radians[1]), 0, np.sin(radians[1])],
        [0, 1, 0],
        [-np.sin(radians[1]), 0, np.cos(radians[1])],
    ])
    rotation_matrix_z = np.array([
        [np.cos(radians[2]), -np.sin(radians[2]), 0],
        [np.sin(radians[2]), np.cos(radians[2]), 0],
        [0, 0, 1],
    ])

    # Combined rotation matrix
    rotation_matrix = rotation_matrix_z @ rotation_matrix_y @ rotation_matrix_x

    # Get the current camera matrix
    cam_matrix = testbed.camera_matrix

    # Apply rotation to the camera orientation part
    cam_matrix[:3, :3] = rotation_matrix @ cam_matrix[:3, :3]

    # Apply translation to the camera position (last column)
    cam_matrix[:3, 3] += translation

    # Set the new camera matrix
    testbed.camera_matrix = cam_matrix


def main():
    # Set up the testbed
    scene = "vid"  # Replace with your scene path
    snapshot = "vid/base.msgpack"  # Replace with your snapshot path
    output_dir = "output"  # Replace with your output directory
    server_url = "http://3.145.161.54:5000/vrside"  # Server URL for image upload

    # Ensure the output directory exists
    os.makedirs(output_dir, exist_ok=True)

    testbed = ngp.Testbed(ngp.TestbedMode.Nerf)
    testbed.load_training_data(scene)
    testbed.load_snapshot(snapshot)

    resolution = [960, 540]  # Default resolution

    # Set up watchdog observer
    event_handler = TransformHandler(testbed, output_dir, resolution, server_url)
    observer = Observer()
    observer.schedule(event_handler, path="scripts", recursive=False)

    print("Watching for changes in transform.json...")
    observer.start()

    try:
        while True:
            pass  # Keep the script running to monitor changes
    except KeyboardInterrupt:
        observer.stop()
    observer.join()


if __name__ == "__main__":
    main()



# !/usr/bin/env python3

# import os
# import sys
# import json
# import time
# import multiprocessing
# import numpy as np
# from watchdog.observers import Observer
# from watchdog.events import FileSystemEventHandler

# # Add the build directory to Python path
# pyngp_path = os.path.abspath("./build")
# sys.path.append(pyngp_path)

# import pyngp as ngp  # noqa
# import common


# class TransformHandler(FileSystemEventHandler):
#     def __init__(self, task_queue):
#         super().__init__()
#         self.task_queue = task_queue
#         self.previous_transform = {
#             "rotation": [0.0, 0.0, 0.0],
#             "position": [0.0, 0.0, 0.0]
#         }

#     def on_modified(self, event):
#         """Handle file modifications."""
#         if event.src_path.endswith("transform.json"):
#             print(f"Detected change in {event.src_path}. Adding to task queue...")
#             self.process_transform_file(event.src_path)

#     def process_transform_file(self, transform_file):
#         """Process the JSON file and add delta transformations to the task queue."""
#         try:
#             with open(transform_file, "r") as f:
#                 transform_data = json.load(f)

#             current_rotation = transform_data.get("rotation", [0.0, 0.0, 0.0])
#             current_position = transform_data.get("position", [0.0, 0.0, 0.0])

#             # Compute deltas
#             delta_rotation = [
#                 current_rotation[i] - self.previous_transform["rotation"][i]
#                 for i in range(3)
#             ]
#             delta_position = [
#                 current_position[i] - self.previous_transform["position"][i]
#                 for i in range(3)
#             ]

#             # Update previous transform
#             self.previous_transform["rotation"] = current_rotation
#             self.previous_transform["position"] = current_position

#             # Combine deltas into a single transformation
#             delta_transformation = delta_rotation + delta_position

#             # Add transformation to the task queue
#             self.task_queue.put(delta_transformation)
#             print(f"Added delta transformation {delta_transformation} to task queue.")
#         except Exception as e:
#             print(f"Error processing transform file: {e}")


# def render_worker(task_queue, output_dir, resolution, scene, snapshot):
#     """Worker process for rendering tasks."""
#     # Initialize a testbed instance for the worker
#     testbed = ngp.Testbed(ngp.TestbedMode.Nerf)
#     testbed.load_training_data(scene)
#     testbed.load_snapshot(snapshot)

#     while True:
#         transformation = task_queue.get()  # Get a task from the queue
#         if transformation is None:  # Sentinel value to stop the worker
#             break

#         try:
#             # Measure start time
#             start_time = time.time()

#             # Apply transformations
#             apply_transformations(testbed, transformation)

#             # Render and save the image
#             output_file = os.path.join(output_dir, f"rendered_frame_{int(time.time())}.png")
#             render_image(testbed, resolution, output_file)

#             # Measure end time and calculate elapsed time
#             elapsed_time = time.time() - start_time
#             print(f"Rendered image saved to {output_file}. Took {elapsed_time:.4f} seconds.")
#         except Exception as e:
#             print(f"Error in rendering worker: {e}")


# def render_image(testbed, resolution, output):
#     """Renders the current scene to an image."""
#     frame = testbed.render(resolution[0], resolution[1], spp=8, linear=True)
#     common.write_image(output, frame)


# def apply_transformations(testbed, transformation):
#     """
#     Apply both rotation and translation to the NeRF camera.
#     :param transformation: A list of 6 elements [rot_x, rot_y, rot_z, trans_x, trans_y, trans_z]
#     """
#     # Extract rotation and translation
#     rotation = transformation[:3]
#     translation = transformation[3:]

#     # Compute rotation matrices
#     radians = np.radians(rotation)
#     rotation_matrix_x = np.array([
#         [1, 0, 0],
#         [0, np.cos(radians[0]), -np.sin(radians[0])],
#         [0, np.sin(radians[0]), np.cos(radians[0])],
#     ])
#     rotation_matrix_y = np.array([
#         [np.cos(radians[1]), 0, np.sin(radians[1])],
#         [0, 1, 0],
#         [-np.sin(radians[1]), 0, np.cos(radians[1])],
#     ])
#     rotation_matrix_z = np.array([
#         [np.cos(radians[2]), -np.sin(radians[2]), 0],
#         [np.sin(radians[2]), np.cos(radians[2]), 0],
#         [0, 0, 1],
#     ])

#     # Combined rotation matrix
#     rotation_matrix = rotation_matrix_z @ rotation_matrix_y @ rotation_matrix_x

#     # Get the current camera matrix
#     cam_matrix = testbed.camera_matrix

#     # Apply rotation to the camera orientation part
#     cam_matrix[:3, :3] = rotation_matrix @ cam_matrix[:3, :3]

#     # Apply translation to the camera position (last column)
#     cam_matrix[:3, 3] += translation

#     # Set the new camera matrix
#     testbed.camera_matrix = cam_matrix


# def main():
#     # Set up the testbed
#     scene = "vid"  # Replace with your scene path
#     snapshot = "vid/base.msgpack"  # Replace with your snapshot path
#     output_dir = "output"  # Replace with your output directory

#     # Ensure the output directory exists
#     os.makedirs(output_dir, exist_ok=True)

#     resolution = [960, 540]  # Default resolution

#     # Create a multiprocessing task queue
#     task_queue = multiprocessing.Queue()

#     # Set up watchdog observer
#     event_handler = TransformHandler(task_queue)
#     observer = Observer()
#     observer.schedule(event_handler, path="scripts", recursive=False)

#     print("Watching for changes in transform.json...")
#     observer.start()

#     # Start worker processes
#     num_workers = multiprocessing.cpu_count()  # Use one worker per CPU core
#     workers = []
#     for _ in range(num_workers):
#         worker = multiprocessing.Process(
#             target=render_worker,
#             args=(task_queue, output_dir, resolution, scene, snapshot)
#         )
#         workers.append(worker)
#         worker.start()

#     try:
#         while True:
#             pass  # Keep the main script running to monitor changes
#     except KeyboardInterrupt:
#         observer.stop()
#         print("Stopping workers...")

#         # Stop all worker processes
#         for _ in range(num_workers):
#             task_queue.put(None)  # Send sentinel values to workers
#         for worker in workers:
#             worker.join()

#     observer.join()


# if __name__ == "__main__":
#     main()
