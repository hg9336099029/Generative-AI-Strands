# argparse is a built-in Python module used to read command-line arguments.
# It allows users to provide input while running a Python script instead of
# changing values directly in the source code.

# Reasons for using argparse:

# 1. Avoid Hardcoding
#    - No need to edit the Python file every time you want different inputs.

# 2. Make the Script Reusable
#    - The same script can be used for different folders, files, or parameters.

# 3. Runtime Customization
#    - Users can choose values like chunk size, overlap, or document path
#      while executing the program.

# 4. Input Validation
#    - Automatically checks input types (e.g., int, float, string) and
#      shows an error if the user enters an invalid value.

# 5. Default Values
#    - If the user doesn't provide an argument, argparse uses the default value,
#      so the program still works.

# 6. Automatic Help Message
#    - Running:
#          python script.py --help
#      automatically displays all available arguments and their descriptions.

# 7. Readable Commands
#    - Named arguments are easier to understand than positional values.

#      Good:
#          python build_index.py --docs ./docs --chunk-size 500 --overlap 50

#      Less clear:
#          python build_index.py ./docs 500 50

# 8. Easy Automation
#    - Scripts using argparse can easily be called from shell scripts,
#      cron jobs, Docker containers, CI/CD pipelines, or other programs.

# Import the argparse module to handle command-line arguments
import argparse

# Import default configuration values
from app.config import CHUNK_OVERLAP, CHUNK_SIZE, DOCS_DIR

# Import the function that reads documents, creates embeddings,
# and builds the vector index
from app.ingestion import build_index


# Main function of the program
def main() -> None:

    # Create an ArgumentParser object
    # This allows users to pass arguments while running the script
    parser = argparse.ArgumentParser(
        description="Build the Knowledge Assistant vector index."
    )

    # Add the --docs argument
    # Specifies the folder containing the documents.
    # If not provided, DOCS_DIR from config.py is used.
    parser.add_argument(
        "--docs",
        default=DOCS_DIR,
        help="Path to the docs folder."
    )

    # Add the --chunk-size argument
    # Specifies the size of each text chunk.
    # Default value comes from config.py
    parser.add_argument(
        "--chunk-size",
        type=int,
        default=CHUNK_SIZE
    )

    # Add the --overlap argument
    # Specifies how many characters/tokens overlap
    # between consecutive chunks.
    parser.add_argument(
        "--overlap",
        type=int,
        default=CHUNK_OVERLAP
    )

    # Parse all command-line arguments
    # Example:
    # python build_index.py --docs ./data --chunk-size 600 --overlap 100
    args = parser.parse_args()

    # Print the folder being processed
    print(f"Ingesting documents from: {args.docs}")

    # Build the vector index by:
    # 1. Reading documents
    # 2. Splitting them into chunks
    # 3. Generating embeddings
    # 4. Storing them in the vector database/index
    build_index(
        docs_dir=args.docs,
        chunk_size=args.chunk_size,
        overlap=args.overlap
    )


# This block runs only when this file is executed directly.
# It will NOT run if this file is imported into another Python file.
if __name__ == "__main__":
    main()