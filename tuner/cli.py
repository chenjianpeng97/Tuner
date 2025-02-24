import sys
import click
import os
from tuner.fiddler2python.fd2py import FidToPy


@click.group()
def cli():
    # place holder for the main function
    pass


@click.command(
    help="Convert fiddler export .txt file to .py file;single file or current directory"
)
@click.argument("filename", required=False)
def fd2py(filename):
    if filename:
        save_name = filename.replace("txt", "py")
        f = FidToPy(filename, save_name)
        f.start()
    else:
        txt_files = [f for f in os.listdir(".") if f.endswith(".txt")]
        print(txt_files)
        if not txt_files:
            print("Error: No .txt files found in the current directory.")
            sys.exit(1)
        for filename in txt_files:
            save_name = filename.replace("txt", "py")
            f = FidToPy(filename, save_name)
            f.start()


cli.add_command(fd2py)


def main():
    cli()


if __name__ == "__main__":
    cli()
