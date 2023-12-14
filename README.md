NOTE this was originally taken from the divmod web site - but the api
links in this document are broken.

::: innercontent
::: {#indexing-and-searching-with-lupy .section}
# [Indexing and Searching With Lupy]{#indexing-and-searching-with-lupy}

::: {#introduction .section}
## [Introduction]{#introduction}

Check that Lupy has been installed correctly by starting Python and
successfully doing:

``` literal-block
import lupy
```

You can exit python.

In this examples directory there is a directory named ./aesop/ which
contains 30 files, each with a fable in them.

To index these files type:

``` literal-block
python index.py
```

You will see some confirmation that Lupy is adding the text files to an
index. The index will be saved in a directory named
[`./aesopind/`{.literal}]{.pre}.

Once indexing is finished, have a look in
[`./aesopind/`{.literal}]{.pre} and you will see a lot of files with
names like [`_19.tii`{.literal}]{.pre}. Each of these files belongs to a
segment. This is what Lucene format indexes look like. The number of
files in this directory depends on a lot of factors. Calling optimize()
once in a while compacts all the segments into one.

Back in the examples directory type:

``` literal-block
python search.py
```

This will perform 4 different searches against the index that you just
built and print the results.

You should get output similar to this:

``` literal-block
Query: fox
Found in document aesop/3.txt (The Lion's Share)
Found in document aesop/7.txt (The Fox and the Crow)
Found in document aesop/20.txt (The Fox and the Mask)
Found in document aesop/19.txt (The Fox and the Stork)

Query: \fox and the crow\
Found in document aesop/7.txt (The Fox and the Crow)

Query: +fox-crow-lion
Found in document aesop/20.txt (The Fox and the Mask)
Found in document aesop/19.txt (The Fox and the Stork)

Query: title:frog
Found in document aesop/22.txt (The Frog and the Ox)
```
:::

::: {#fields .section}
## [Fields]{#fields}

The basic unit of data in a Lupy index is the field: a name paired with
a value, either free text or a keyword. Fields have three independent
boolean attributes: *stored*, *indexed*, and *tokenized*. Stored fields
are included in search results when their containing document is
matched, indexed fields are the ones actually searched, and tokenized
fields are split into words (as opposed to being included as an opaque
string). The default for
[document.Field](http://divmod.org/projects/lupy/api/public/lupy.document.Field-class.html){.reference}
is to be indexed and tokenized but not stored; this will be used for
most of the text Lupy processes.
[document.Keyword](http://divmod.org/projects/lupy/api/public/lupy.document-module.html#Keyword){.reference}
produces stored, indexed, untokenized fields, and is useful for
filenames or database IDs.
[document.Text](http://divmod.org/projects/lupy/api/public/lupy.document-module.html#Text){.reference}
produces stored, indexed, tokenized fields, and is useful for a
document\'s title or summary.
:::

::: {#simple-indexing .section}
## [Simple Indexing]{#simple-indexing}

Simple forms of document indexing can be accomplished easily. For
example, here is the code from simple.py that creates an index and adds
data from files to it (simplified for clarity):

``` literal-block
index = Index(indexName, create=True)

for name in os.listdir(filedir):
    f = os.path.join(filedir, name)
    text = open(f, 'rb').read().decode("latin-1")
    title = text.split('\n\n\n')[0]
    index.index(text=text, __title=title, _filename=f)
    
index.optimize()
```

First, a
[indexer.Index](http://divmod.org/projects/lupy/api/public/lupy.indexer.Index-class.html){.reference}
is created, which opens the directory that will contain the index files
(and in this case, since [`create`{.literal}]{.pre} is True, removes any
existing index). Each file to be indexed is opened and Unicode text is
extracted from it. The title of the fable being read is split off (the
example files have their title as the first line, separated by three
newlines from the text), and then [`index()`{.literal}]{.pre} is called,
pairing field names with indexable data. The names of arguments to
[`index()`{.literal}]{.pre} and field names, and indicate what Lupy
should do with the data: names preceded with an underscore are Keyword
fields, and names preceded with a double underscore are Text fields.
Thus, [`text`{.literal}]{.pre}, [`title`{.literal}]{.pre}, and
[`filename`{.literal}]{.pre} are instances of Field, Text, and Keyword,
respectively.

[`index.optimize()`{.literal}]{.pre} is an optional call that merges all
on-disk segments together into a single segment. It can be quite an
expensive operation, but it can save space and speed up searches.
:::

::: {#simple-searching .section}
## [Simple Searching]{#simple-searching}

When using the
[indexer.Index](http://divmod.org/projects/lupy/api/public/lupy.indexer.Index-class.html){.reference}
interface, simple searches can be done by passing the query string to
the [`find`{.literal}]{.pre} method, which returns a
[Hits](http://divmod.org/projects/lupy/api/public/lupy.search.hits.Hits-class.html){.reference}
object, a sequence of
[Documents](http://divmod.org/projects/lupy/api/public/lupy.document.Document-class.html){.reference}
found. For example:

``` literal-block
hits = index.find('fox')
for h in hits:
   print 'Found in', h.get('filename')

index.close()
```

Searches done in this fashion are done in all fields; documents
containing any of the terms specified are returned. To search for
phrases, enclose the query in double quotes. To search in a single field
only, use [`index.findInField(field=query)`{.literal}]{.pre}; the query
will be parsed as with [`find()`{.literal}]{.pre}.

Note that an instance of
[indexer.Index](http://divmod.org/projects/lupy/api/public/lupy.indexer.Index-class.html){.reference}
can be used for both indexing and searching; just remember to call
[`close()`{.literal}]{.pre} on it when finished, to flush its contents
to disk.
:::

::: {#advanced-searching .section}
## [Advanced Searching]{#advanced-searching}

Queries can also be built by hand, using the
[TermQuery](http://divmod.org/projects/lupy/api/public/lupy.search.term.TermQuery-class.html){.reference},
[PhraseQuery](http://divmod.org/projects/lupy/api/public/lupy.search.phrase.PhraseQuery-class.html){.reference},
and
[BooleanQuery](http://divmod.org/projects/lupy/api/public/lupy.search.boolean.BooleanQuery-class.html){.reference}
classes, and then run using an
[IndexSearcher](http://divmod.org/projects/lupy/api/public/lupy.search.indexsearcher.IndexSearcher-class.html){.reference}.
Examples of their use can be seen in search.py:

``` literal-block
def termSearch(qStr):
    t = Term('text', qStr)
    q = TermQuery(t)
    return q

def phraseSearch(qStr):
    q = PhraseQuery()
    for p in qStr.split():
        t = Term('text', p)
        q.add(t)
    return q


def boolSearch(ands=[], ors=[], nots=[]):
    q = BooleanQuery()

    for a in ands:
        t = Term('text', a)
        tq = TermQuery(t)
        q.add(tq, True, False)

    for a in ors:
        t = Term('text', a)
        tq = TermQuery(t)
        q.add(tq, False, False)

    for a in nots:
        t = Term('text', a)
        tq = TermQuery(t)
        q.add(tq, False, True)

    return q
```

In particular, note that instances of
[Term](http://divmod.org/projects/lupy/api/public/lupy.index.term.Term-class.html){.reference}
must be created for each word in the query, and that the field that
should be searched for it must be specified. Boolean queries can be used
to combine other queries in various ways, either requiring or
prohibiting search terms. Once your query has been constructed, pass it
to
[IndexSearcher](http://divmod.org/projects/lupy/api/public/lupy.search.indexsearcher.IndexSearcher-class.html){.reference}.search:

``` literal-block
searcher = IndexSearcher(indexName)
q = termSearch('fox')
hits = searcher.search(q)
for h in hits:
    print 'Found in', h.get('filename')
```

A sequence of found documents is returned, as before.
:::

::: {#advanced-indexing .section}
## [Advanced Indexing]{#advanced-indexing}

It is also possible to manually create
[Documents](http://divmod.org/projects/lupy/api/public/lupy.document.Document-class.html){.reference}
and put them in an index, via
[IndexWriter](http://divmod.org/projects/lupy/api/public/lupy.index.indexwriter.IndexWriter-class.html){.reference}.
This example is adapted from index.py:

``` literal-block
index = IndexWriter(indexName, create=True)
for name in os.listdir(dir):
    fname = os.path.join(dir, name)
    if os.path.isdir(fname) or os.path.islink(fname):
        continue
    text = open(fname,'rb').read().decode('latin-1')

    d = document.Document()
    t = document.Text('text',text, False)
    d.add(t)
    
    f = document.Keyword('filename',name)
    d.add(f)
    
    index.addDocument(d)
    
index.close()
```

Data is added to the index by building up
[Documents](http://divmod.org/projects/lupy/api/public/lupy.document.Document-class.html){.reference}
from various fields (in this case, the text from the file, and the
filename), and calling [`addDocument()`{.literal}]{.pre} on the index.
Keyword fields, as before, are not tokenized, but are merely stored as
opaque text, and returned with search results.

IndexWriter (as well as indexer.Index) also take an
[`analyzer`{.literal}]{.pre} keyword argument, allowing you to specify
your own token generator (which gets called with the string to be
tokenized). The default is
[index.documentwriter.standardTokenizer](http://divmod.org/projects/lupy/api/public/lupy.index.documentwriter-module.html#standardTokenizer){.reference}
:::

::: {#performance .section}
## [Performance]{#performance}

Initial benchmarks using Psyco indicate the possibility of a 2x speedup
when it is used. The number of documents to be indexed before in-memory
data is flushed to disk can be adjusted by calling
[`.setMergeFactor`{.literal}]{.pre} (the default is 20).
:::
:::
:::
