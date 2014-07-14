========
CSV Sort
========

Sort a CSV file on disk rather than in memory. The merge sort algorithm is used to break up the original file into smaller chunks, sort these in memory, and then merge these sorted files.

Example usage:

.. sourcecode:: python

    >>> import csvsort
    >>> # sort this CSV on the 4th and 2nd columns (columns are 0 indexed)
    >>> csvsort('test1.csv', [4,2])  
    >>> # sort this CSV with no header on 3rd column and save results to separate file
    >>> csvsort('test2.csv', [3], output_file='test3.csv', has_header=False)  

..

csvsort can also be used from the command line:

.. sourcecode:: bash

    $ # sort this CSV on 0th column
    $ python csvsort.py test1.tsv --coloumn=0
    
    $ # sort this tab separated file (TSV) on 3rd and 1st columns
    $ python csvsort.py test3.tsv --delimiter='\t' -c 3 -c 1

..


=======
Install
=======

.. sourcecode:: bash

    pip install csvsort

..
