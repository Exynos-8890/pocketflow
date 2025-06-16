from pocket import *
import string
# Assume Node and Flow classes are imported, e.g.:
# from pocketflow import Node, Flow

class RemoveCharNode(Node):
    def prep(self, shared):
        return shared['text']

    def exec(self, prep_res):
        char_to_remove = self.params['char']
        return prep_res.replace(char_to_remove, '')

    def post(self, shared, prep_res, exec_res):
        shared['text'] = exec_res
        return exec_res

class ThreeStepRemovalFlow(Flow):
    def __init__(self):
        super().__init__()
        remove_comma = RemoveCharNode()
        remove_period = RemoveCharNode()
        remove_exclamation = RemoveCharNode()

        remove_comma.set_params({'char': ','})
        remove_period.set_params({'char': '.'})
        remove_exclamation.set_params({'char': '!'})

        remove_comma >> remove_period >> remove_exclamation

        self.start(remove_comma)

if __name__ == "__main__":
    input_string = "Hello, world! This is a test sentence. With commas, periods, and exclamation marks!"
    shared_data = {'text': input_string}

    my_flow = ThreeStepRemovalFlow()
    final_result = my_flow.run(shared_data)

    print(f"Original: {input_string}")
    print(f"Cleaned (from flow result): {final_result}")
    print(f"Cleaned (from shared data): {shared_data.get('text')}")
