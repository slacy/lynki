import os
import markdown
from jinja2 import Environment, FileSystemLoader
from nltk.util import bigrams

# Recursively find all text files
# Process files into lists of words
# Process bigrams and trigram frequency
# Create list of bigrams and trigrams that occur more than once
# filter out bigrams and trigrams that start or end with a stopword
# Create mapping from N-gram to list of documents that contain in
# reprocess all documents, generating links for every N-gram


class Gram(object):
    """Gram"""
    def __init__(self, parts, filename, offset):
        self.parts = parts
        self.filename = filename
        self.offset = offset

    def string(self):
        """string"""
        return ' '.join(self.parts)

    def __str__(self):
        return "%s %s %s" % (self.parts, self.filename, self.offset)

    def can_join(self, other):
        """can_join"""
        if other.filename != self.filename:
            return False
        if (other.offset > self.offset
            and other.offset <= self.offset + len(self.string())):
            return True
        return False

    def join(self, other):
        """Join this gram with another gram and return the joined gram"""
        if not self.can_join(other):
            return None

        if self.offset < other.offset:
            first = self
            second = other
        else:
            first = other
            second = self

        overlap = second.offset - first.offset
        joined = first.string()[:overlap] + second.string()
        new_parts = tuple(joined.split(' '))
        return Gram(new_parts, first.filename, first.offset)


class GramSet(object):
    """GramSet"""
    def __init__(self):
        self.grams = []
        self.by_filename = {}
        self.by_parts = {}

    def add(self, gram):
        """add"""
        self.grams.append(gram)
        if gram.filename not in self.by_filename:
            self.by_filename[gram.filename] = []
        self.by_filename[gram.filename].append(gram)

        if gram.parts not in self.by_parts:
            self.by_parts[gram.parts] = []
        self.by_parts[gram.parts].append(gram)

    def backlinks(self, filename):
        """backlinks"""
        backlinks = []
        for gram in self.by_filename[filename]:
            for match in self.by_parts[gram.parts]:
                if match.filename != filename:
                    backlinks.append(match)
        return backlinks

    def remove(self, gram_list):
        """remove"""
        for gram in gram_list:
            self.grams.remove(gram)
            self.by_filename[gram.filename].remove(gram)
            self.by_parts[gram.parts].remove(gram)
            if len(self.by_filename[gram.filename]) == 0:
                del self.by_filename[gram.filename]
            if len(self.by_parts[gram.parts]) == 0:
                del self.by_parts[gram.parts]

    def debug(self):
        """debug"""
        print "DEBUG"
        print '\n'.join([str(g) for g in self.grams])

    def __str__(self):
        return "GramSet %d grams, %d unique" % (len(self.grams),
                                                len(self.by_parts))


def find_corpus(root, suffix):
    """find_corpus"""

    def visit(md_files, dirname, names):
        """visit"""
        md_files += [os.path.abspath(os.path.join(dirname, fn))
                     for fn in names if fn.endswith(suffix)]

    md_files = []
    os.path.walk(root, visit, md_files)
    return md_files


def find_layout(filepath):
    """find_layout"""
    fullpath = os.path.abspath(filepath)
    while fullpath != '/':
        base = os.path.dirname(fullpath)
        layout = os.path.join(base, '_layout', 'layout.html')
        if os.path.exists(layout):
            return layout
        fullpath = base
    return None


def find_root(filepath):
    """find_root"""
    fullpath = os.path.abspath(filepath)
    while fullpath != '/':
        dirname = os.path.dirname(fullpath)
        root = os.path.join(dirname, '_root')
        if os.path.exists(root):
            return dirname
        fullpath = dirname
    return None


def offsets_of(substr, content):
    """offsets_of"""
    offsets = []
    start = 0
    while start < len(content):
        found = content.find(substr, start)
        if found < 0:
            break
        offsets.append(found)
        start = found + len(substr)
    return offsets


class Preprocessor(object):
    """Preprocessor"""

    def __init__(self):
        self.content = {}
        self.all_grams = GramSet()

    def process(self, filename):
        """process"""
        in_file = open(filename)
        self.content[filename] = in_file.read()
        in_file.close()

        words = self.content[filename].split(' ')
        grams = bigrams(words)
        self.add_grams(filename, grams)

    def add_grams(self, filename, raw_grams):
        """add_grams"""
        for raw_gram in raw_grams:
            offsets = offsets_of(' '.join(raw_gram), self.content[filename])
            for offset in offsets:
                new_gram = Gram(raw_gram, filename, offset)
                self.all_grams.add(new_gram)

    def trim_grams(self):
        """trim_grams"""
        for gram_parts in self.all_grams.by_parts.keys():
            grams = self.all_grams.by_parts[gram_parts]
            unique_files = set([gram.filename for gram in grams])
            if len(unique_files) <= 1:
                self.all_grams.remove(grams)

    def joinup(self, filename):
        """joinup"""
        did_join = False
        for first_gram in self.all_grams.by_filename[filename]:
            for second_gram in self.all_grams.by_filename[filename]:
                joined_gram = first_gram.join(second_gram)
                if joined_gram:
                    self.all_grams.remove([first_gram, second_gram])
                    self.all_grams.add(joined_gram)
                    did_join = True

        return did_join

    def compile(self, filename):
        """compile"""
        root = find_root(filename)
        layout = find_layout(filename)
        layout = layout.replace(root, '')
        layout = layout.lstrip('/')
        env = Environment(loader=FileSystemLoader(root))
        out_file = open(filename.replace('.md', '.html'), 'w+')

        # Now, given grams in self.all_grams, linkify them
        print filename
        new_content = self.content[filename]
        for backlink in sorted(self.all_grams.backlinks(filename),
                               key=lambda x: x.offset):
            where = self.content[filename].find(backlink.string())
            relative = os.path.relpath(backlink.filename,
                                       os.path.dirname(filename))
            relative = relative.replace('.md', '.html')
            new_content = new_content.replace(
                backlink.string(),
                '[' + backlink.string() + '](' + relative + ')', 1)
        self.content[filename] = new_content

        html = markdown.markdown(self.content[filename])
        template = env.get_template(layout)
        final = template.render(html=html)
        out_file.write(final)
        out_file.close()


def main():
    """main"""
    corpus = find_corpus(os.curdir, '.md')

    pre = Preprocessor()
    for filename in corpus:
        pre.process(filename)
    pre.trim_grams()

    for filename in corpus:
        joined = pre.joinup(filename)
        while joined:
            joined = pre.joinup(filename)

    for filename in corpus:
        pre.compile(filename)

if __name__ == '__main__':
    main()
