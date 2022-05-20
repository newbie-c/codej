from markdown.extensions import Extension
from pyembed.core import PyEmbed
from pyembed.core.discovery import (
    AutoDiscoverer, ChainingDiscoverer, FileDiscoverer, UrlDiscoverer)

from pyembed.markdown import pattern


class CodejDiscoverer(ChainingDiscoverer):
    def __init__(self):
        super().__init__([
            AutoDiscoverer(),
            UrlDiscoverer('http://oembed.com/providers.json')])


class CodejEmbed(PyEmbed):
    def __init__(self, discoverer=CodejDiscoverer(), renderer=None):
        super().__init__(discoverer=discoverer, renderer=renderer)


class PyEmbedMarkdown(Extension):
    def __init__(self, renderer=None):
        super(PyEmbedMarkdown, self).__init__()
        self.renderer = renderer

    def extendMarkdown(self, md, md_globals):
        if self.renderer:
            pyembed = CodejEmbed(renderer=self.renderer)
        else:
            pyembed = CodejEmbed()

        md.inlinePatterns.add(
            'pyembed', pattern.PyEmbedPattern(pyembed, md), '_begin')


def makeExtension(configs=None):  # pragma: no cover
    return PyEmbedMarkdown()
