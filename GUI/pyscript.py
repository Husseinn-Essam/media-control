import sys
import json

def main():
    while True:
        # Read JSON data from Electron (stdin)
        line = sys.stdin.readline()
        if not line:
            break

        try:
            # Parse JSON data sent by Electron
            data = json.loads(line)
            # Process the data
            response = {"msgContent": "Hello from Python!", "originalData": data}

            # Send JSON response to Electron (stdout)
            print(json.dumps(response))  # This should only be the JSON response
            sys.stdout.flush()
        except json.JSONDecodeError as e:
            # If the data isn't valid JSON, log and continue
            sys.stderr.write(f"Error decoding JSON: {e}\n")
            sys.stderr.flush()

if __name__ == "__main__":
    main()
