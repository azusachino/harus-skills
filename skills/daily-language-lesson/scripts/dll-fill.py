#!/usr/bin/env python3
import sys
import os
import argparse


def main():
    parser = argparse.ArgumentParser(
        description="Fill Obsidian lesson templates with generated content."
    )
    parser.add_argument("output_path", help="Path to the Markdown file to update")
    parser.add_argument(
        "--en", required=True, help="Path to English lesson content file"
    )
    parser.add_argument(
        "--ja", required=True, help="Path to Japanese lesson content file"
    )
    parser.add_argument(
        "--es", required=True, help="Path to Spanish lesson content file"
    )

    args = parser.parse_args()

    if not os.path.exists(args.output_path):
        print(f"Error: Output path '{args.output_path}' does not exist.")
        sys.exit(1)

    try:
        with open(args.output_path, "r", encoding="utf-8") as f:
            content = f.read()

        def read_content(path):
            if not os.path.exists(path):
                print(f"Error: Content file '{path}' not found.")
                sys.exit(1)
            with open(path, "r", encoding="utf-8") as f:
                return f.read().strip()

        en_lesson = read_content(args.en)
        ja_lesson = read_content(args.ja)
        es_lesson = read_content(args.es)

        def replace_section(full_content, section_name, new_inner_content):
            header = f"## {section_name}"
            start_marker = "```ad-note"
            end_marker = "```"

            section_start = full_content.find(header)
            if section_start == -1:
                return full_content

            block_start = full_content.find(start_marker, section_start)
            if block_start == -1:
                return full_content

            block_inner_start = block_start + len(start_marker)
            # Find the closing ``` that belongs to this ad-note block
            block_end = full_content.find(end_marker, block_inner_start)

            if block_end == -1:
                return full_content

            return (
                full_content[:block_inner_start]
                + "\n"
                + new_inner_content
                + "\n"
                + full_content[block_end:]
            )

        content = replace_section(content, "writing", en_lesson)
        content = replace_section(content, "japanese", ja_lesson)
        content = replace_section(content, "spanish", es_lesson)

        with open(args.output_path, "w", encoding="utf-8") as f:
            f.write(content)

        print(f"Successfully filled lesson blocks in '{args.output_path}'.")

    except Exception as e:
        print(f"Error processing files: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
