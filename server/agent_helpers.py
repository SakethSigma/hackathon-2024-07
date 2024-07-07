import os
import re
import json

def get_absolute_path(path):
    return os.path.abspath(os.path.join(os.path.dirname(__file__), path))


class PromptConstructor():
    def __init__(self):
        self.messages = []

    def read_file_content(self, file_path):
        with open(file_path) as f:
            file_content = ''.join(f.readlines())
        return file_content

    def get_system_message(self):
        system_file = next(file for file in os.listdir(
            self.prompt_path) if file.find('system') > -1)
        system_file_path = os.path.join(self.prompt_path, system_file)
        system_message = self.read_file_content(system_file_path)
        return system_message

    def get_nth_user_example(self, n):
        nth_user_file = next(file for file in os.listdir(self.prompt_path) if (
            file.find(f'{n}_user') > -1) and (file.endswith('.txt')))
        user_file_path = os.path.join(self.prompt_path, nth_user_file)

        user_message = self.read_file_content(user_file_path)
        return user_message

    def get_nth_assistant_example(self, n):
        nth_ass_file = next(file for file in os.listdir(self.prompt_path) if (
            file.find(f'{n}_ass') > -1) and (file.endswith('.txt')))
        ass_file_path = os.path.join(self.prompt_path, nth_ass_file)

        ass_message = self.read_file_content(ass_file_path)
        return ass_message

    def get_nth_example(self, n):
        try:
            nth_user_message = self.get_nth_user_example(n)
            nth_ass_message = self.get_nth_assistant_example(n)

            return nth_user_message, nth_ass_message
        except:
            return None

    def prepare_examples(self):
        system_message = self.get_system_message()
        system_message_item = {
            "role": "system",
            "content": system_message
        }
        self.messages.append(system_message_item)

        n_files_in_directory = len([file for file in os.listdir(
            self.prompt_path) if file.endswith('.txt')])
        n_examples = (n_files_in_directory-1)/2  # (total - system) / 2
        current_example_no = 1

        while current_example_no <= n_examples:
            example = self.get_nth_example(current_example_no)

            user_message_item = {
                "role": "user",
                "content": example[0]
            }
            ass_message_item = {
                "role": "assistant",
                "content": example[1]
            }
            self.messages.append(user_message_item)
            self.messages.append(ass_message_item)

            current_example_no += 1

    def add_current_prompt(self):
        current_prompt_item = {
            "role": "user",
            "content": self.current_prompt
        }
        self.messages.append(current_prompt_item)

    def __call__(self, prompt_type, prompt_version, current_prompt, relative_path=''):
        self.prompt_type = prompt_type
        self.prompt_version = prompt_version
        self.prompt_path = os.path.join('prompts', prompt_type, prompt_version)
        self.prompt_path = os.path.join(relative_path, self.prompt_path)
        self.prompt_path = get_absolute_path(self.prompt_path)
        self.current_prompt = current_prompt
        self.prepare_examples()
        self.add_current_prompt()

        return self.messages


def response_to_json(text):
    pattern = r'```json\s*|\s*```'
    cleaned_text = re.sub(pattern, '', text, flags=re.DOTALL).strip()
    
    try:
        json_text = json.loads(cleaned_text)
        return json_text
    except:
        print("Invalid Json")
        print(f"{cleaned_text}")


def response_to_sql(text):
    pattern = r'```sql\s*|\s*```'
    cleaned_text = re.sub(pattern, '', text, flags=re.DOTALL).strip() 
   
    return cleaned_text
