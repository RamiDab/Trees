import itertools
from copy import deepcopy


class Node:
    def __init__(self, data, positive_child=None, negative_child=None):
        self.data = data
        self.positive_child = positive_child
        self.negative_child = negative_child

    def check_no_childes(self):
        if self.positive_child is not None and self.negative_child is not None:
            return False
        else:
            return True


class Record:
    def __init__(self, illness, symptoms):
        self.illness = illness
        self.symptoms = symptoms


def parse_data(filepath):
    with open(filepath) as data_file:
        records = []
        for line in data_file:
            words = line.strip().split()
            records.append(Record(words[0], words[1:]))
        return records


class Diagnoser:
    def __init__(self, root: Node):
        self.root = root

    def diagnose(self, symptoms):
        diagnose = self.helper_diagnose(self.root, symptoms)
        return diagnose

    def helper_diagnose(self, root: Node, symptoms):
        if root.check_no_childes():
            return root.data
        elif root.data in symptoms:
            root = root.positive_child
            return self.helper_diagnose(root, symptoms)
        else:
            root = root.negative_child
            return self.helper_diagnose(root, symptoms)

    def calculate_success_rate(self, records):
        count = len(records)
        if count == 0:
            raise ValueError("the length is zero")
        for check in records:
            if self.diagnose(check.symptoms) != check.illness:
                count -= 1
        return count / len(records)

    def all_illnesses(self):

        result = self.helper_all_illnesses(self.root, [])
        dict_counter = dict()
        for ill in result:
            if ill in dict_counter:
                dict_counter[ill] += 1
            else:
                dict_counter[ill] = 1
        list = sorted((value, key) for (key, value) in dict_counter.items())[::-1]
        last = []
        for item in list:
            last.append(item[1])
        return last

    def helper_all_illnesses(self, root: Node, lst: list):
        if root is None:
            return []
        if root.check_no_childes():
            return [root.data]
        neg_child = root.negative_child
        lst += self.helper_all_illnesses(neg_child, lst)
        pos_child = root.positive_child
        lst += self.helper_all_illnesses(pos_child, lst)
        return lst

    def paths_to_illness(self, illness):
        result = self.helper_paths_to_illness(self.root, illness, [], [])
        return result

    def helper_paths_to_illness(self, root: Node, illness: str, current_lst: list, result: list):
        if root is None and illness == "None":
            result += [current_lst]
        if root is None:
            return
        if root.check_no_childes() and root.data == illness:
            result += [current_lst]
            return result
        elif root.check_no_childes() and root.data != illness:
            return result
        neg_child = root.negative_child
        current_lst_neg = deepcopy(current_lst)
        current_lst_neg += [False]
        self.helper_paths_to_illness(neg_child, illness, current_lst_neg, result)
        pos_child = root.positive_child
        current_lst_pos = deepcopy(current_lst)
        current_lst_pos += [True]
        self.helper_paths_to_illness(pos_child, illness, current_lst_pos, result)
        return result


def build_tree(records, symptoms):
    for record in records:
        if not isinstance(record, Record):
            raise TypeError("there is an item in records that it's type isn't a record")
    for symptom in symptoms:
        if not isinstance(symptom, str):
            raise TypeError("there is an item in symptoms that it's type isn't a string")
    if len(symptoms) == 0:
        root = Node(None)
    else:
        root = Node(symptoms[0])
    build_tree_helper(records, symptoms, 1, root, len(symptoms), [], [])
    return Diagnoser(root)


def build_tree_helper(records, symptoms, current_index, root: Node, stop_index, pos_lst, neg_lst):
    if current_index == stop_index:
        root.positive_child = Node(find_ill(records, symptoms, pos_lst + [symptoms[current_index - 1]], neg_lst))
        root.negative_child = Node(find_ill(records, symptoms, pos_lst, neg_lst + [symptoms[current_index - 1]]))
        return
    new_pos_node = Node(symptoms[current_index])
    root.positive_child = new_pos_node
    build_tree_helper(records, symptoms, current_index + 1, new_pos_node, stop_index,
                      pos_lst + [symptoms[current_index - 1]],
                      neg_lst)
    new_neg_node = Node(symptoms[current_index])
    root.negative_child = new_neg_node
    build_tree_helper(records, symptoms, current_index + 1, new_neg_node, stop_index,
                      pos_lst,
                      neg_lst + [symptoms[current_index - 1]])
    # return Node(root, new_pos_node, new_neg_node)

def find_ill(records, symptoms, pos_lst, neg_lst):
    dict_helper = dict()
    for record in records:
        current_symptoms = record.symptoms
        current_ill = record.illness
        flag = True
        for symptom in pos_lst:
            if symptom not in current_symptoms:
                flag = False
                break
        for symptom in current_symptoms:
            if symptom in neg_lst:
                flag = False
                break
        if flag:
            if current_ill not in dict_helper:
                dict_helper[current_ill] = 1
            else:
                dict_helper[current_ill] += 1
    if len(dict_helper) != 0:
        return max(dict_helper, key=lambda x:dict_helper[x])
    return None


def optimal_tree(records, symptoms, depth):
    if 0 > depth <= len(records):
        raise ValueError("enter a different depth value")
    for rec in records:
        if not isinstance(rec , Record):
            raise ValueError("you records are not the same type")

    return optimal_tree_helper(records,itertools.combinations(symptoms , depth), 0)


def optimal_tree_helper(records, trees, highest_rate):
    for tree in trees:
        new_tree = build_tree(records, tree)
        the_tree_rate = new_tree.calculate_success_rate(records)
        if the_tree_rate > highest_rate:
            highest_tree = new_tree
            highest_rate = the_tree_rate
    return highest_tree



if __name__ == "__main__":

    # Manually build a simple tree.
    #                cough
    #          Yes /       \ No
    #        fever           healthy
    #   Yes /     \ No
    # covid-19   cold

    flu_leaf = Node("covid-19", None, None)
    cold_leaf = Node("cold", None, None)
    inner_vertex = Node("fever", flu_leaf, cold_leaf)
    healthy_leaf = Node("healthy", None, None)
    root = Node("cough", inner_vertex, healthy_leaf)

    diagnoser = Diagnoser(root)

    # Simple test
    diagnosis = diagnoser.diagnose(["cough"])
    if diagnosis == "cold":
        print("Test passed")
    else:
        print("Test failed. Should have printed cold, printed: ", diagnosis)

# Add more tests for sections 2-7 here.
