from ometa.boot import BootOMetaGrammar
from ometa.runtime import ParseError, EOFError
from terml.parser import parseTerm as term
from terml.quasiterm import quasiterm

__version__ = '1.1'

def makeGrammar(source, bindings, name='Grammar', unwrap=False):
    """
    Create a class from a Parsley grammar.

    :param source: A grammar, as a string.
    :param bindings: A mapping of variable names to objects.
    :param name: Name used for the generated class.

    :param unwrap: If True, return a parser class suitable for
                   subclassing. If False, return a wrapper with the
                   friendly API.
    """
    g = BootOMetaGrammar.makeGrammar(source, bindings, name=name)
    if unwrap:
        return g
    else:
        return wrapGrammar(g)


def wrapGrammar(g):
    def makeParser(input):
        """
        Creates a parser for the given input, with methods for
        invoking each rule.

        :param input: The string you want to parse.
        """
        return _GrammarWrapper(g(input), input)
    makeParser._grammarClass = g
    return makeParser

def unwrapGrammar(w):
    """
    Access the internal parser class for a Parsley grammar object.
    """
    return w._grammarClass

class _GrammarWrapper(object):
    """
    A wrapper for Parsley grammar instances.

    To invoke a Parsley rule, invoke a method with that name -- this
    turns x(input).foo() calls into grammar.apply("foo") calls.
    """
    def __init__(self, grammar, input):
        self._grammar = grammar
        self._input = input
        #so pydoc doesn't get trapped in the __getattr__
        self.__name__ = _GrammarWrapper.__name__

    def __getattr__(self, name):
        """
        Return a function that will instantiate a grammar and invoke the named
        rule.
        :param name: Rule name.
        """
        def invokeRule(*args, **kwargs):
            """
            Invoke a Parsley rule. Passes any positional args to the rule.
            """
            try:
                ret, err = self._grammar.apply(name, *args)
            except ParseError, e:
                err = e
            else:
                try:
                    extra, _ = self._grammar.input.head()
                except EOFError:
                    return ret
            raise err
        return invokeRule

__all__ = ['makeGrammar', 'wrapGrammar', 'unwrapGrammar', 'term', 'quasiterm']
