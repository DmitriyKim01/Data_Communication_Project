import os
import sys
from grpc_tools import protoc

def generate_proto(proto_file: str = "sensor.proto", output_dir: str = "proto"):
    # Get the absolute paths for proto file and output directory
    root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..')) 
    proto_file_path = os.path.join(root_dir, 'proto', proto_file)  
    output_dir_path = os.path.join(root_dir, output_dir)  

    # Ensure that the output directory exists
    if not os.path.exists(output_dir_path):
        os.makedirs(output_dir_path)

    # Command to compile the .proto file
    command = [
        "grpc_tools.protoc",
        f"--proto_path={os.path.dirname(proto_file_path)}",
        f"--python_out={output_dir_path}",                   
        f"--grpc_python_out={output_dir_path}",           
        proto_file_path,                                   
    ]

    # Run the command
    if protoc.main(command) != 0:
        raise Exception("Error: Failed to generate Python code from proto file.")
    else:
        print(f"Successfully generated Python files in '{output_dir_path}'.")

if __name__ == "__main__":
    # Run the function from the root directory of the app
    generate_proto()
