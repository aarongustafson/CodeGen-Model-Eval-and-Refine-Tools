import json
import os

from run_tests import instructions  # Import instructions from run_tests.py
from run_tests import process_prompts  # Import the function from run_tests.py

def load_tests():
  with open('tests.json', 'r') as f:
    data = json.load(f)
    return data['tests']

def get_test_key(tests):
  print("Available tests:")
  for index, test in enumerate(tests):
    print(f"{index}: {test['title']}")
  try:
    test_index = int(input("Enter the index of the test you want to re-run: "))
    if test_index < 0 or test_index >= len(tests):
      raise ValueError
  except ValueError:
    print("Invalid test index.")
    exit(1)
  return tests[test_index]

def get_diff_files():
  diff_files = []
  while True:
    diff_file = input("Enter the name of a .diff file to include (or press Enter to finish): ")
    if not diff_file:
      break
    diff_path = os.path.join('diffs', diff_file)
    if not os.path.isfile(diff_path):
      print(f"{diff_file} does not exist.")
      continue
    with open(diff_path, 'r') as f:
      diff_files.append(f.read())
  return diff_files

def run_test(test, diffs):
  system_prompt = instructions
  system_prompt.append(
    "In previous instances, I had to correct your code. Here are the diffs with comments as to what was incorrect:"
  )
  for diff in diffs:
      system_prompt.append(diff)
  execute_test(test, system_prompt)


def execute_test(test, system_prompt):
  test_title = test['title']
  test_folder = os.path.join('retest', test_title)
  os.makedirs(test_folder, exist_ok=True)

  prefix = test.get('prefix', '')

  for prompt_index, prompt in enumerate(test['prompts'], start=1):
    process_prompts(test_folder, system_prompt, prefix, prompt, prompt_index)

def main():
  tests = load_tests()
  test_key = get_test_key(tests)
  diffs = get_diff_files()
  run_test(test_key, diffs)

if __name__ == "__main__":
  main()