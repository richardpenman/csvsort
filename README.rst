========
CSV Sort
========

For sorting CSV files on disk that do not fit into memory. The merge sort algorithm is used to break up the original file into smaller chunks, sort these in memory, and then merge these sorted files.


=============
Example usage
=============

.. sourcecode:: python

    >>> from csvsort import csvsort
    >>> # sort this CSV on the 5th and 3rd columns (columns are 0 indexed)
    >>> csvsort('test1.csv', [4,2])  
    >>> # sort this CSV with no header on 4th column and save results to separate file
    >>> csvsort('test2.csv', [3], output_filename='test3.csv', has_header=False)  
    >>> # sort this TSV on the first column and use a maximum of 10MB per split
    >>> csvsort('test3.tsv', [0], max_size=10, delimiter='\t')  
    >>> # sort this CSV on the first column and force quotes around every field (default is csv.QUOTE_MINIMAL)
    >>> import csv
    >>> csvsort('test4.csv', [0], quoting=csv.QUOTE_ALL) 

    # sort multi csv files into one
    >>> csvsort(["test1.csv", "test2.csv", [0], output_filename="test_all.csv")

..


=======
Install
=======

Supports python 2 & 3:

.. sourcecode:: bash

    $ pip install csvsort
    $ pip3 install csvsort

..

====
test
====

.. sourcecode:: bash
    $ pip3 install -e ./
    $ python3 -m unittest discover
..
