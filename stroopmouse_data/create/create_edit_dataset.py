import os
import create.core as core

def main():
    data_repo_path = input("Please enter the path for the data repository: ")
    dataset_repo_path = input("Please enter the path for the dataset repository: ")

    if not os.path.exists(data_repo_path):
        print(f"Error: The data repository path '{data_repo_path}' does not exist.")
        return

    if not os.path.exists(dataset_repo_path):
        print(f"Error: The dataset repository path '{dataset_repo_path}' does not exist.")
        return

    try:
        core.edit_dataset(data_repo_path, dataset_repo_path)
        print("Dataset edited successfully.")
    except Exception as e:
        print(f"An error occurred while editing the dataset: {e}")

if __name__ == "__main__":
    main()