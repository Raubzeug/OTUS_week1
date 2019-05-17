import ast
import os
import collections
import argparse
import subprocess
import json
import csv

from nltk import pos_tag
from abc import ABC, abstractmethod


class MixinFlat:
    def flat(self, list_):
        """ [(1,2), (3,4)] -> [1, 2, 3, 4]"""
        return sum([list(item) for item in list_], [])


class Report:
    """this class provides with different types of reports"""
    def __init__(self, data):
        self.data = data

    @staticmethod
    def get_filename_from_user():
        filename = input('please enter filename for your report: ')
        if filename == '' or filename == '\n':
            filename = 'report'
        return filename

    def to_console(self):
        print(self.data)

    def to_json(self):
        filename = self.get_filename_from_user()
        filename = '.'.join([filename, 'json'])
        with open(filename, 'w') as outfile:
            json.dump(self.data, outfile)
        print('your report was succesfully saved to {0}'.format(os.path.join('.', filename)))

    def to_csv(self):
        filename = self.get_filename_from_user()
        filename = '.'.join([filename, 'csv'])
        with open(filename, 'w') as outfile:
            reportwriter = csv.writer(outfile, delimiter=';')
            for row in self.data:
                reportwriter.writerow(list(row))
        print('your report was succesfully saved to {0}'.format(os.path.join('.', filename)))

    def to_etc(self):
        pass


class GithubRepository:
    """this is class that provides for actions with Github repository"""
    def __init__(self, link):
        self.link = link

    def clone_repo(self):
        path_to_copy = input('Please enter path to directory you want to copy repository (folder must be empty) '
                     'or press "Enter" to copy into current directory: ')

        if path_to_copy == '':
            folder = os.path.abspath('')
            repo_name = self.link.split('/')[-1]
            path_to_copy = os.path.join(folder, repo_name)

        count = 1
        while True:
            if os.path.isdir(path_to_copy):
                dir_contents = [x for x in os.listdir(path_to_copy)]
                if len(dir_contents) > 0:
                    new_repo_name = repo_name + str(count)
                    path_to_copy = os.path.join(folder, new_repo_name)
                    print('unfortunatelly folder you want to copy repository is not empty, '
                          'trying to copy to {0}'.format(path_to_copy))
                    count += 1
                else:
                    break
            else:
                break

        command = ["git", "clone", self.link, r'{0}'.format(path_to_copy)]

        try:
            subprocess.check_call(command)
        except subprocess.CalledProcessError as err:
            print('Terminated. Error = ', err)
            return

        print('GIT repository {0} was sucessfully cloned to {1}'.format(self.link, path_to_copy))
        return path_to_copy


def get_repository_clone(repo_link):
    """this function clones repository from given link if possible (if not
     it uses default data) and returns list of pathes for futher ananysis"""
    pathes = []
    if repo_link is not None and 'github' in repo_link:
        pathes += [GithubRepository(repo_link).clone_repo()]
    else:
        if repo_link is None:
            print('Program will continue running with default data')
        else:
            print('Unfortunatelly it is impossible to clone repository from {0}. Program will continue running with'
                  'default data'.format(repo_link))

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
            pathes.append(path)

    return pathes


class FileList:
    """this class provides with gettins list of filenames withi given path(incl. all subdirs)"""
    def __init__(self, path):
        self.path = path

    def get_all_py_filenames(self, limit=100):
        """creates a list of first 'limit' dir+name of *.py files"""
        filenames = set()
        for dirname, dirs, files in os.walk(self.path, topdown=True):
            py_files_in_dir = [os.path.join(dirname, file) for file in files if file.endswith('.py')]
            for file in py_files_in_dir:
                filenames.add(file)
                if len(filenames) > limit:
                    print('total {0} files'.format(len(filenames)))
                    return filenames
        print('total {0} files'.format(len(filenames)))
        return filenames

    def get_all_js_filenames(self, limit=100):
        pass


class PyCodeParsed(MixinFlat):
    """this class provides parsing of *.py code: creating of Abstract Syntax Tree using ast module
    and working with tree"""
    def __init__(self,  filename):
        self.filename = filename
        self.main_file_content, self.tree = self.python_code_parsing()

    def python_code_parsing(self):
        """builts Abstract Syntax Tree from code in given *.py file"""

        with open(self.filename, 'r', encoding='utf-8') as attempt_handler:
            main_file_content = attempt_handler.read()
        try:
            tree = ast.parse(main_file_content)
        except SyntaxError as e:
            print(e)
            tree = None

        return main_file_content, tree

    def get_all_names(self):
        """returns list of nodes which are ast.Name instances"""
        if self.tree is not None:
            all_names = [node.id for node in ast.walk(self.tree) if isinstance(node, ast.Name)
                         if not (node.id.startswith('__') and node.id.endswith('__'))]
            for i in range(len(all_names)):
                all_names[i] = all_names[i].split('_')
            return self.flat(all_names)
        else:
            return []

    def get_all_functions_names(self):
        """returns list of assigned function names"""
        if self.tree is not None:
            all_f_names = [node.name.lower() for node in ast.walk(self.tree) if isinstance(node, ast.FunctionDef)
                           if not (node.name.lower().startswith('__') and node.name.lower().endswith('__'))]
            for i in range(len(all_f_names)):
                all_f_names[i] = all_f_names[i].split('_')
            return self.flat(all_f_names)
        else:
            return []


class JSCodeParsed:
    pass


class Word:
    """this class allows to analysis words using nltk module"""
    def __init__(self, word):
        self.word = word
        self.word_type = self.determine_word_type()

    def determine_word_type(self):
        """checks if word is current word_type using pos_tag function from nltk module
        is_word_type('decomposition', 'verb') -> False
        is_word_type('decomposition', 'noun') -> True
        is_word_type('obtain', 'verb') -> True"""
        if not self.word:
            return False
        pos_info = pos_tag([self.word])
        if pos_info[0][1] == 'VB':
            return 'verb'
        if pos_info[0][1] == 'NN':
            return 'noun'
        else:
            return 'unknown_type'


class Statistics(MixinFlat):
    """this class providing with different statistics of frequency met words in data"""
    def __init__(self, data):
        self.data = self.flat(data)

    def verb_frequency(self, top_size=10):
        verbs = [word for word in self.data if Word(word).word_type == 'verb']
        return Report(collections.Counter(verbs).most_common(top_size))

    def noun_frequency(self, top_size=10):
        nouns = [word for word in self.data if Word(word).word_type == 'noun']
        return Report(collections.Counter(nouns).most_common(top_size))

    def another_stat(self):
        pass


def get_trees(path, with_filenames=False, with_file_content=False):
    """creates and return list of Abstract Syntax Trees for every *.py file
    in given path (incl. subdirectories)"""
    filenames = get_all_filenames(path)
    trees = set()
    for filename in filenames:
        tree = Code_tree(filename)
        if with_filenames:
            if with_file_content:
                trees.add(filename, tree.main_file_content, tree.tree)
            else:
                trees.add((filename, tree.tree))
        else:
            trees.add(tree.tree)
    print('trees generated', len(trees))
    return trees


def get_args_from_command_line():
    """this function provides parcing of command line"""
    parser = argparse.ArgumentParser(description='This program makes an analysis of most frequently met'
                                                 ' words in the code within copied repository from GitHub')
    parser.add_argument('-s', '--statistics', default='verb',
                        choices=['verb', 'noun'], help='Select a part of speech you want to check')
    parser.add_argument('-r', '--range', default='func',
                        choices=['func', 'var'], help='Select range of analysis')
    parser.add_argument('-o', '--output', default='console',
                        choices=['console', 'json', 'csv'], help='Select a type of output')
    parser.add_argument('-repo', default=None, help='Enter a path to repository you want to clone')
    arguments = parser.parse_args()
    return arguments


def get_data_for_analysis_py(pathes, analysys_range):
    """this function returns instance of class Statistics for further analysis"""
    py_filelnames = set()
    for obj in [FileList(path) for path in pathes]:
        py_filelnames.update(obj.get_all_py_filenames())

    py_files = [PyCodeParsed(filename) for filename in py_filelnames]

    if analysys_range == 'func':
        names = [obj.get_all_functions_names() for obj in py_files]
    elif analysys_range == 'var':
        names = [obj.get_all_names() for obj in py_files]

    return Statistics(names)


def main():
    args = get_args_from_command_line()
    pathes = []
    pathes += get_repository_clone(args.repo)

    data = get_data_for_analysis_py(pathes, args.range)

    if args.statistics == 'verb':
        result = data.verb_frequency()
    elif args.statistics == 'noun':
        result = data.noun_frequency()

    if args.output == 'console':
        result.to_console()
    elif args.output == 'json':
        result.to_json()
    elif args.output == 'csv':
        result.to_csv()


if __name__ == '__main__':
    main()
