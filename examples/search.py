# This module is part of the Lupy project and is Copyright 2003 Amir
# Bakhtiar (amir@divmod.org). This is free software; you can redistribute
# it and/or modify it under the terms of version 2.1 of the GNU Lesser
# General Public License as published by the Free Software Foundation.

"""Examples of different kinds of query being run through an IndexSearcher.
"""

import re

from lupy.index.term import Term
from lupy.search.indexsearcher import IndexSearcher
from lupy.search.term import TermQuery
from lupy.search.phrase import PhraseQuery
from lupy.search.boolean import BooleanQuery

import lupy

import demo_config

# unique container function
# from http://aspn.activestate.com/ASPN/Cookbook/Python/Recipe/52560
def unique(s):
    """Return a list of the elements in s, but without duplicates.

    For example, unique([1,2,3,1,2,3]) is some permutation of [1,2,3],
    unique("abcabc") some permutation of ["a", "b", "c"], and
    unique(([1, 2], [2, 3], [1, 2])) some permutation of
    [[2, 3], [1, 2]].

    For best speed, all sequence elements should be hashable.  Then
    unique() will usually work in linear time.

    If not possible, the sequence elements should enjoy a total
    ordering, and if list(s).sort() doesn't raise TypeError it's
    assumed that they do enjoy a total ordering.  Then unique() will
    usually work in O(N*log2(N)) time.

    If that's not possible either, the sequence elements must support
    equality-testing.  Then unique() will usually work in quadratic
    time.
    """

    n = len(s)
    if n == 0:
        return []

    # Try using a dict first, as that's the fastest and will usually
    # work.  If it doesn't work, it will usually fail quickly, so it
    # usually doesn't cost much to *try* it.  It requires that all the
    # sequence elements be hashable, and support equality comparison.
    u = {}
    try:
        for x in s:
            u[x] = 1
    except TypeError:
        del u  # move on to the next method
    else:
        return u.keys()

    # We can't hash all the elements.  Second fastest is to sort,
    # which brings the equal elements together; then duplicates are
    # easy to weed out in a single pass.
    # NOTE:  Python's list.sort() was designed to be efficient in the
    # presence of many duplicate elements.  This isn't true of all
    # sort functions in all languages or libraries, so this approach
    # is more effective in Python than it may be elsewhere.
    try:
        t = list(s)
        t.sort()
    except TypeError:
        del t  # move on to the next method
    else:
        assert n > 0
        last = t[0]
        lasti = i = 1
        while i < n:
            if t[i] != last:
                t[lasti] = last = t[i]
                lasti += 1
            i += 1
        return t[:lasti]

    # Brute force is all that's left.
    u = []
    for x in s:
        if x not in u:
            u.append(x)
    return u

def printHits(hits):
    if len(hits) == 0:
        print 'Nothing found!'
    else:
        for hit in hits:
            print 'Found in document %s (%s)' % (hit.get('filename'), hit.get('title'))
        
def termSearch(qStr):
    t = Term('text', qStr)
    q = TermQuery(t)
    
    return q


def fieldSearch(qStr, fieldname):
    """Search for qStr only on specified fieldname
    """
    t = Term(fieldname, qStr)
    q = TermQuery(t)
    
    return q
        
        
def titleSearch(qStr):
    t = Term('title', qStr)
    q = TermQuery(t)
    
    return q
        
        
def phraseSearch(qStr, field='text'):
    """Find all docs containing the phrase C{qStr}."""

    parts = qStr.split()
    
    q = PhraseQuery()
    
    for p in parts:
        t = Term(field, p)
        q.add(t)
        
    return q
        

def boolSearch(ands=[], ors=[], nots=[]):
    """Build a simple boolean query.
    each word in B{ands} is equiv to +word
    each word in B{ors} is equiv to word
    each word in B{nots} is equiv to -word

    e.g. boolSearch(['spam'], ['eggs'], ['parrot', 'cheese'])
    is equiv to +spam eggs -parrot -cheese in Google/Lucene syntax"""
    
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
        

def lucene_wildcard_to_regex(in_str):
    """Takes a Lucene style wild card string and returns a regex search string.
    See http://lucene.apache.org/java/docs/queryparsersyntax.html
    Turns '.' and '*' into regex wildcards. Currently maps to
    regex that will match a word in string, i.e. 
    
        'fox*' to match 'foxes', but not 'fox hole' (due to space)
    
    Unlike Lucene you can place a wild card at the start of the search term
    BUT a search term of only wildcards is not allowed and an empty
    string is returned.
    TODO! currently inefficient but easy to read source
    """
    # escape search string, this may be redundant depending on how the
    # Terms in the index where tokenized at index time
    # this will also escape our Lucene wildcards
    tmp_str = re.escape(in_str)
    
    # Assume that Lucene wildcards are always escaped in the same way
    # i.e. assume 
    #   '.' -> r'\.'
    #   '*' -> r'\*'
    tmp_str = tmp_str.replace(r'\.', r'\S')
    tmp_str = tmp_str.replace(r'\*', r'\w*')
    return tmp_str 

    
def dumbWildSearch(qStr, keyword_str):
    """Not really a proper PrefixQuery and/or WildcardQuery 
    takes in qStr containing Lucene wildcards.
    This actually searches ALL Terms in the index to find matches
    then uses the found terms are input to a boolean (OR) search.
    """
    regex_keyword_search_str = lucene_wildcard_to_regex(qStr)
    or_search_terms = re.findall(regex_keyword_search_str, keyword_str)
    q = boolSearch([], or_search_terms, [])
    return q
    
    
def runQuery(q, searcher):
    """The run a query through a searcher and return the hits"""

    print 'Query:', q.toString('text')
    hits = searcher.search(q)
    printHits(hits)
    print
    return hits

       
      
def main():
    """One shot search.
    Opens and closes the index on every query.
    """
    
    import time    
    
    index_info = demo_config.get_config('demo.ini')
    index_name = index_info['index']
    
    tt = time.time()
    
    searcher = IndexSearcher(index_name)

    # enumerate through index, and get all Terms
    # this should be done as SOON as the index is opened BUT before it is used
    # this is potentially VERY slow
    all_keywords=[]
    if isinstance(searcher.reader, lupy.index.segmentmerger.SegmentReader):
        for tuple_info in searcher.reader.tis.enum:
            (term_struct, key_pos) = tuple_info 
            field_name = term_struct.field()
            keyword_str = term_struct.text()
            ## will get duplicates if keyword exists in different terms (e.g. title and text)
            ## fastest thing to do is NOT insert into container IF it is already present
            all_keywords.append(keyword_str)
            #print field_name, ':', keyword_str
    elif isinstance(searcher.reader, lupy.index.segmentmerger.SegmentsReader):
        for tmp_reader in searcher.reader.readers:
            for tuple_info in  tmp_reader.tis.enum:
                (term_struct, key_pos) = tuple_info
                field_name = term_struct.field()
                keyword_str = term_struct.text()
                ## will get duplicates if keyword exists in different terms (e.g. title and text)
                ## fastest thing to do is NOT insert into container IF it is already present
                all_keywords.append(keyword_str)
                #print field_name, ':', keyword_str
    ## TODO FIXME remove duplicates? use dict?
    #print 'all keywords', all_keywords
    all_keywords = unique(all_keywords)
    #print 'all keywords', all_keywords
    all_keywords_str = ' '.join(all_keywords)
    #print 'all_keywords_str', all_keywords_str
    
    
    
    # Note that all queries have to be submitted in lower-case...

    print 'Term search 1'
    q = termSearch('fox')
    runQuery(q, searcher)
    
    print 'Term search 2'
    q = termSearch('lion')
    runQuery(q, searcher)
    
    print 'Phrase search'
    q = phraseSearch('fox and the crow')
    runQuery(q, searcher)

    # A boolean search equiv to 'x and not y'
    print 'Boolean search 1 (must have x and not y)'
    q = boolSearch(['fox'], [], ['crow', 'lion'])
    runQuery(q, searcher)

    print 'Boolean search 2 (must have x, must have y)'
    q = boolSearch(['fox', 'lion'], [], [])
    runQuery(q, searcher)

    print 'Boolean search 3.a (must have x, y is optional)'
    q = boolSearch(['fox'], ['lion'], [])
    runQuery(q, searcher)

    print 'Boolean search 3.b (must have x, y is optional)'
    q = boolSearch(['lion'], ['fox'], [])
    runQuery(q, searcher)

    print 'Boolean search 3.c (x is optional, y is optional)'
    q = boolSearch([], ['fox', 'lion'], [])
    runQuery(q, searcher)

    # Search the title field
    print 'field search on "title"'
    q = fieldSearch('frog', 'title')
    runQuery(q, searcher)
    
    # Search the title field
    print 'field search on "invalidtitle"'
    q = fieldSearch('frog', 'invalidtitle')
    runQuery(q, searcher)
    
    # Search the title field
    print 'Title search'
    q = titleSearch('frog')
    runQuery(q, searcher)
    

    print 'Exact term search (default)'
    #q = termSearch('some')
    q = termSearch('wood')
    runQuery(q, searcher)
    
    print 'Exact term search (default)'
    #q = termSearch('something')
    q = termSearch('woodman')
    runQuery(q, searcher)
    
    print 'wildcard term search (slow)' # but most cost was spent at "list keywords time"
    #q = dumbWildSearch('some*', all_keywords_str)
    q = dumbWildSearch('wood*', all_keywords_str)
    runQuery(q, searcher)

    searcher.close()
    
    print time.time() - tt

if __name__ == "__main__":
    main()
