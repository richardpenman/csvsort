

import os
import sys
import csv
csv.field_size_limit(sys.maxint)
import heapq
from optparse import OptionParser


# temporary directory to store the sub-files
TMP_DIR = '.csvsort'
if not os.path.exists(TMP_DIR):
    os.mkdir(TMP_DIR)


def csvsort(input_filename, columns, output_filename=None, max_size=100, has_header=True, delimiter=',', quoting=csv.QUOTE_MINIMAL):
    """Sort the CSV file on disk rather than in memory
    The merge sort algorithm is used to break the file into smaller sub files and 

    input_filename: the CSV filename to sort
    columns: a list of column indices (0 based) to sort on
    output_filename: optional filename for sorted file. If not given then input file will be overriden.
    max_size: the maximum size (in MB) of CSV file to load in memory at once
    has_header: whether the CSV contains a header to keep separated from sorting
    delimiter: character used to separate fields, default ','
    """
    reader = csv.reader(open(input_filename), delimiter=delimiter)
    if has_header:
        header = reader.next()
    else:
        header = None

    filenames = csvsplit(reader, max_size)
    print 'Merging %d splits' % len(filenames)
    for filename in filenames:
        memorysort(filename, columns)
    sorted_filename = mergesort(filenames, columns)
  
    writer = csv.writer(open(output_filename or input_filename, 'w'), delimiter=delimiter, quoting=quoting)
    if header:
        writer.writerow(header)
    generate_result(writer, sorted_filename)


def generate_result(writer, sorted_filename): 
    """generate final output file
    """
    for row in csv.reader(open(sorted_filename)):
        writer.writerow(row)
    os.remove(sorted_filename)
    try:
        os.rmdir(TMP_DIR)
    except OSError:
        pass


def csvsplit(reader, max_size):
    """Split into smaller CSV files of maximum size and return the list of filenames
    """
    max_size = max_size * 1024 * 1024 # convert to bytes
    writer = None
    current_size = 0
    split_filenames = []

    # break CSV file into smaller merge files
    for row in reader:
        if writer is None:
            filename = os.path.join(TMP_DIR, 'split%d.csv' % len(split_filenames))
            writer = csv.writer(open(filename, 'w'))
            split_filenames.append(filename)

        writer.writerow(row)
        current_size += sys.getsizeof(row)
        if current_size > max_size:
            writer = None
            current_size = 0
    return split_filenames


def memorysort(filename, columns):
    """Sort this CSV file in memory on the given columns
    """
    rows = [row for row in csv.reader(open(filename))]
    rows.sort(key=lambda row: get_key(row, columns))
    writer = csv.writer(open(filename, 'wb'))
    for row in rows:
        writer.writerow(row)


def get_key(row, columns):
    """Get sort key for this row
    """
    return [row[column] for column in columns]


def decorated_csv(filename, columns):
    """Iterator to sort CSV rows
    """
    for row in csv.reader(open(filename)):
        yield get_key(row, columns), row


def mergesort(sorted_filenames, columns, nway=2):
    """Merge these 2 sorted csv files into a single output file
    """
    merge_n = 0
    while len(sorted_filenames) > 1:
        merge_filenames, sorted_filenames = sorted_filenames[:nway], sorted_filenames[nway:]
        readers = map(open, merge_filenames)

        output_filename = os.path.join(TMP_DIR, 'merge%d.csv' % merge_n)
        print 'create', output_filename
        writer = csv.writer(open(output_filename, 'w'))
        merge_n += 1

        for _, row in heapq.merge(*[decorated_csv(filename, columns) for filename in merge_filenames]):
            writer.writerow(row)
        
        sorted_filenames.append(output_filename)
        for filename in merge_filenames:
            print 'delete', filename
            os.remove(filename)
    return sorted_filenames[0]


def main():
    parser = OptionParser()
    parser.add_option('-c', '--column', dest='columns', action='append', type='int', help='index of CSV to sort on')
    #parser.add_option('-f', '--field', dest='field', action='append', help='column name of CSV to sort on')
    parser.add_option('-s', '--size', '-s', dest='max_size', type='float', default=100, help='maximum size of each split CSV file in MB (default 100)')
    parser.add_option('-n', '--no-header', dest='has_header', action='store_false', default=True, help='set CSV file has no header')
    parser.add_option('-d', '--delimiter', default=',', help='set CSV delimiter (default ",")')
    args, input_files = parser.parse_args()

    if not input_files:
        parser.error('What CSV file should be sorted?')
    elif not args.columns:
        parser.error('Which columns should be sorted on?')
    else:
        # escape backslashes
        args.delimiter = args.delimiter.decode("string_escape")
        csvsort(input_files[0], columns=args.columns, max_size=args.max_size, has_header=args.has_header, delimiter=args.delimiter)

 
if __name__ == '__main__':
    main()
