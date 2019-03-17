import argparse
import re


if __name__ == '__main__':
    parser = argparse.ArgumentParser(add_help=True, description='Sample Commandline')

    parser.add_argument('--file', action="store", help="path of file to take as input", nargs="?",
                        metavar="file")

    args = parser.parse_args()

    print(args.file)

    regex = re.compile("(?<=(=))(\d)+")
    output_file = open("task_1_5_result.txt", "w+")

    with open(args.file, "r") as f:
        for line in f:
            matches = regex.finditer(line)
            if matches :
                for match in matches:
                    output_file.write(match.group() + "\n")
