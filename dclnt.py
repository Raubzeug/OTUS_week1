import ast
import os
import collections

from nltk import pos_tag


def flat(list_):
    """ [(1,2), (3,4)] -> [1, 2, 3, 4]"""
    return sum([list(item) for item in list_], [])


def is_verb(word):
    """checks if word is verb using pos_tag function from nltk module
    is_verb('decomposition') -> False
    is_verb('obtain') -> True"""
    if not word:
        return False
    pos_info = pos_tag([word])
    return pos_info[0][1] == 'VB'


def get_all_filenames(path, limit=100):
    """creates a list of first 'limit' dir+name of *.py files in given path (incl. all subdirs)"""
    filenames = set()
    for dirname, dirs, files in os.walk(path, topdown=True):
        py_files_in_dir = [os.path.join(dirname, file) for file in files if file.endswith('.py')]
        for file in py_files_in_dir:
            filenames.add(file)
            if len(filenames) > limit:
                print('total {0} files'.format(len(filenames)))
                return filenames
    print('total {0} files'.format(len(filenames)))
    return filenames


def get_tree_from_filename(filename):
    """builts Abstract Syntax Tree from code in given *.py file"""
    with open(filename, 'r', encoding='utf-8') as attempt_handler:
        main_file_content = attempt_handler.read()
    try:
        tree = ast.parse(main_file_content)
    except SyntaxError as e:
        print(e)
        tree = None
    return main_file_content, tree


def get_trees(path, with_filenames=False, with_file_content=False):
    """creates and return list of Abstract Syntax Trees for every *.py file
    in given path (incl. subdirectories)"""
    filenames = get_all_filenames(path)
    trees = set()
    for filename in filenames:
        main_file_content, tree = get_tree_from_filename(filename)
        if with_filenames:
            if with_file_content:
                trees.add(filename, main_file_content, tree)
            else:
                trees.add((filename, tree))
        else:
            trees.add(tree)
    print('trees generated', len(trees))
    return trees


def get_all_names(tree):
    """returns list of nodes which are ast.Name instances in given Abstract Syntax Tree"""
    return [node.id for node in ast.walk(tree) if isinstance(node, ast.Name)]


def get_all_functions_names(tree):
    """returns list of assigned function names in given Abstract Syntax Tree"""
    return [node.name.lower() for node in ast.walk(tree) if isinstance(node, ast.FunctionDef)]


def get_verbs_from_function_name(function_name):
    """returns only verbs from given function name"""
    return [word for word in function_name.split('_') if is_verb(word)]


def get_all_words_in_path(path):
    """returns all words of all used functions and assignments in *.py files
    contained in given path"""
    trees = {t for t in get_trees(path) if t}
    all_words = [f for f in flat([get_all_names(t) for t in trees])
                 if not (f.startswith('__') and f.endswith('__'))]
    for i in range(len(all_words)):
        all_words[i] = all_words[i].split('_')
    return flat(all_words)


def get_all_functions_names_in_path(path):
    """returns list of words contained in functions names from all *.py files
    in given path"""
    trees = {t for t in get_trees(path) if t}
    function_names = [f for f in flat([get_all_functions_names(t) for t in trees])
                      if not (f.startswith('__') and f.endswith('__'))]
    for i in range(len(function_names)):
        function_names[i] = function_names[i].split('_')
    print('functions extracted')
    return flat(function_names)


def get_top_verbs_in_functions_names_in_path(path, top_size=10):
    """returns top_size most often met verbs in functions names contained in all *.py files
    in given path"""
    fncs = get_all_functions_names_in_path(path)
    verbs = flat([get_verbs_from_function_name(function_name) for function_name in fncs])
    return collections.Counter(verbs).most_common(top_size)


def get_top_functions_names_in_path(path, top_size=10):
    """returns top_size most often met words of all used functions and assignments names in *.py files
        contained in given path"""
    nms = get_all_functions_names_in_path(path)
    return collections.Counter(nms).most_common(top_size)


def main():
    wds = []
    projects = [
        'django',
        'flask',
        'pyramid',
        'reddit',
        'requests',
        'sqlalchemy',
    ]
    for project in projects:
        path = os.path.join('.', project)
        wds += get_top_verbs_in_functions_names_in_path(path)

    top_size = 200
    print('total {0} words, {1} unique'.format(len(wds), len(set(wds))))
    for word, occurence in collections.Counter(wds).most_common(top_size):
        print(word, occurence)


if __name__ == '__main__':
    main()
