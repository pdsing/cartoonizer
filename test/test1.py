import argparse


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-t', "--type", help="file to process single file, folder to process a full folder")
    parser.add_argument('input', help='source image/ folder that needs to be fully converted')
    parser.add_argument('output', help='destinaton image/ folder with cartoonized images')

    args = parser.parse_args()

    if args.type == "file":
        input_image = args.input
        output_image = args.output
        print(f"The files are {input_image} and {output_image}")

    if args.type == "folder":
        input_image_folder = args.input
        output_image_folder = args.output
        print(f"The folders are {input_image_folder} and {output_image_folder}")
