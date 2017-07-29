# coding=utf-8

"""Probabilistic Context Free Grammar."""

from __future__ import print_function
from __future__ import unicode_literals
from __future__ import absolute_import

from collections import defaultdict
import random
import re
import sys
import os


VERBS = {
    "research": "researching",
    "mine": "mining",
    "craft": "crafting"
}


class MaximumDepthExceeded(Exception):
    """Exception that is raised if the parse tree runs too deep."""

    pass


class SymbolNotFound(Exception):
    """Fix yo grammar."""

    pass


class Grammar(object):

    grammars = {}

    def __init__(self, grammar_string):
        self.grammar = self.parse_grammar(grammar_string)

    @classmethod
    def load(cls, grammar_file):
        with open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "data", grammar_file + ".grammar")) as f:
            cls.grammars[grammar_file] = cls(f.read())
            return cls.grammars[grammar_file]

    def weighted_choice(self, options, weights):
        """Choose a random item, according to weights.

        Args:
            options: list
            weights: list of floats -- don't have to add up to 1
        Returns:
            element of options
        """
        target = random.random() * sum(weights)
        acc = 0
        for idx, weight in enumerate(weights):
            acc += weight
            if acc > target:
                return options[idx]

    def parse_grammar(self, grammar):
        """Return a dictionary mapping symbols to extensions.

        Example:
            >>> grammar = '''
                @s -> @n @v
                @s -> @n @v @n
                @n -> dog | cat
                @v -> chases %3 | eats %2.0'''
            >>> parse_grammar(grammar)
            {
              "@s": [
                [ "@n @v", 0.3 ],
                [ "@n @v @n", 0.7 ]
              ],
              "@v": [
                [ "chases", 0.75 ],
                [ "eats", 0.25 ]
              ],
              "@n": [
                [ "dog", 0.5 ],
                [ "cat", 0.5 ]
              ]
            }

        Args:
            grammar: str
        Returns:
            dict
        """
        weight_re = r"%((?:[\d]*\.)?[\d]+)"

        result = defaultdict(list)
        for line in grammar.splitlines():
            if "->" in line:
                symbol, extension = line.split("->")
                for extension in extension.split("|"):
                    weight = re.search(weight_re, extension)
                    if weight:
                        extension = re.sub(weight_re, "", extension)
                        weight = float(weight.group(1))
                    else:
                        weight = 1.0
                    result[symbol.strip()].append((extension.strip(), weight))

        # normalize
        for symbol, extensions in result.items():
            total_weight = sum(ext[1] for ext in extensions)
            result[symbol] = [(ext[0], ext[1] / total_weight) for ext in extensions]

        return dict(result)

    def transform(self, parts, rule):
        if rule == "gen":
            if parts[-1].rstrip().endswith("s"):
                parts[-1] = parts[-1].rstrip() + "'"
            else:
                parts[-1] = parts[-1].rstrip() + "'s"
        if rule == "initial":
            return [p[0].upper() for p in parts]
        if rule == "title":
            return [p if p in ("by", "of", "and") else p.capitalize() for p in parts]
        return parts

    def extend_rule(self, symbol="@s", max_depth=8):
        """Start with a symbol and returns a list of tokens.

        Args:
            symbol: str -- should start with @
            max_depth: int -- maximum tree depth.
        Returns:
            list -- list of parts
        Raises:
            MaximumDepthExceeded
            SymbolNotFound
        """
        rule = None
        if "~" in symbol:
            symbol, rule = symbol.split("~")
        if max_depth == 0:
            raise MaximumDepthExceeded
        if symbol not in self.grammar:
            raise SymbolNotFound(symbol)
        extension = self.weighted_choice(*zip(*self.grammar[symbol]))
        result = self.extend_sentence(extension, max_depth)
        return self.transform(result, rule)

    def extend_sentence(self, sentence, max_depth=8):
        result = []
        for part in sentence.replace("\n", "\n ").split(" "):
            if part.startswith("@"):
                result.extend(self.extend_rule(part, max_depth - 1))
            else:
                result.append(part)
        return result

    # def extend_all(sentence, grammar, max_depth=8):
    #     if max_depth == 0:
    #         yield " ".join(sentence)
    #     else:
    #         if not isinstance(sentence, list):
    #             sentence = sentence.split()
    #         first_chars = [c[0] for c in sentence]
    #         try:
    #             part = first_chars.index("@")
    #             for extension, pr in grammar[sentence[part]]:
    #                 for r in extend_all(sentence[:part] + [extension] + sentence[part + 1:], grammar, max_depth - 1):
    #                     yield r
    #         except ValueError:
    #             yield " ".join(sentence)

    def assemble_sentence(self, parts):
        """Clean up parts and applies some syntactic rules.

        Args:
            parts: list
        Returns:
            str
        """
        sentence = " ".join(parts)
        sentence = re.sub(r" ([,.!?])", r'\1', sentence)
        sentence = re.sub(r"' ([A-Za-z0-9 ]+) '", r"'\1'", sentence)
        sentence = re.sub(r"  +", r' ', sentence)
        sentence = re.sub(r"\n ", '\n', sentence)
        return sentence.strip()

    def generate(self, sentence=None):
        """Generate a sentence from a grammar string.

        Args:
            grammar: str
        Returns:
            str
        """
        parts = None
        while not parts:
            try:
                parts = self.extend_sentence(sentence)
            except MaximumDepthExceeded:
                pass
            except SymbolNotFound as e:
                print("WARNING: Symbol {} not found".format(e.args[0]), file=sys.stderr)
        return self.assemble_sentence(parts)


NAMES = Grammar.load("names")
GUILDS = Grammar.load("guild_names")
LETTER = Grammar.load("letter")
