import os
from grpc_tools import protoc

def generate_proto(proto_file: str = "sensor.proto", output_dir: str = "."):
   
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    # Command to compile the .proto file
    command = [
        "grpc_tools.protoc",
        f"--proto_path={os.path.dirname(proto_file)}",
        f"--python_out={output_dir}",
        f"--grpc_python_out={output_dir}",
        proto_file,
    ]

    # Run the command
    if protoc.main(command) != 0:
        raise Exception("Error: Failed to generate Python code from proto file.")
    else:
        print(f"Successfully generated Python files in '{output_dir}'.")

if __name__ == "__main__":
  
    generate_proto()