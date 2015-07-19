
import os
import sys
import csv
csv.field_size_limit(sys.maxint)
import heapq
from optparse import OptionParser


# temporary directory to store the sub-files
TMP_DIR = '.csvsort.%d' % os.getpid()
if not os.path.exists(TMP_DIR):
    os.mkdir(TMP_DIR)


class CsvSortError(Exception):
    pass


def csvsort(input_filename, columns, output_filename=None, max_size=100, has_header=True, delimiter=',', quoting=csv.QUOTE_MINIMAL):
    """Sort the CSV file on disk rather than in memory
    The merge sort algorithm is used to break the file into smaller sub files and 

    input_filename: the CSV filename to sort
    columns: a list of column to sort on (can be 0 based indices or header keys)
    output_filename: optional filename for sorted file. If not given then input file will be overriden.
    max_size: the maximum size (in MB) of CSV file to load in memory at once
    has_header: whether the CSV contains a header to keep separated from sorting
    delimiter: character used to separate fields, default ','
    """
    with open(input_filename) as input_fp:
        reader = csv.reader(input_fp, delimiter=delimiter)
        if has_header:
            header = reader.next()
        else:
            header = None

        columns = parse_columns(columns, header)

        filenames = csvsplit(reader, max_size)
        print 'Merging %d splits' % len(filenames)
        for filename in filenames:
            memorysort(filename, columns)
        sorted_filename = mergesort(filenames, columns)

    # XXX make more efficient by passing quoting, delimiter, and moving result
    # generate the final output file
    with open(output_filename or input_filename, 'wb') as output_fp:
        writer = csv.writer(output_fp, delimiter=delimiter, quoting=quoting)
        if header:
            writer.writerow(header)
        with open(sorted_filename) as sorted_fp:
            for row in csv.reader(sorted_fp):
                writer.writerow(row)

    os.remove(sorted_filename)
    try:
        os.rmdir(TMP_DIR)
    except OSError:
        pass


def parse_columns(columns, header):
    """check the provided column headers
    """
    for i, column in enumerate(columns):
        if isinstance(column, int):
            if header:
                if column >= len(header):
                    raise CsvSortError('Column index is out of range: "{}"'.format(column))
        else:
            # find index of column from header
            if header is None:
                raise CsvSortError('CSV needs a header to find index of this column name: "{}"'.format(column))
            else:
                if column in header:
                    columns[i] = header.index(column)
                else:
                    raise CsvSortError('Column name is not found in header: "{}"'.format(column))
    return columns


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
            writer = csv.writer(open(filename, 'wb'))
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
    with open(filename) as input_fp:
        rows = [row for row in csv.reader(input_fp)]
    rows.sort(key=lambda row: get_key(row, columns))
    with open(filename, 'wb') as output_fp:
        writer = csv.writer(output_fp)
        for row in rows:
            writer.writerow(row)


def get_key(row, columns):
    """Get sort key for this row
    """
    return [row[column] for column in columns]


def decorated_csv(filename, columns):
    """Iterator to sort CSV rows
    """
    with open(filename) as fp:
        for row in csv.reader(fp):
            yield get_key(row, columns), row


def mergesort(sorted_filenames, columns, nway=2):
    """Merge these 2 sorted csv files into a single output file
    """
    merge_n = 0
    while len(sorted_filenames) > 1:
        merge_filenames, sorted_filenames = sorted_filenames[:nway], sorted_filenames[nway:]
        readers = map(open, merge_filenames)

        output_filename = os.path.join(TMP_DIR, 'merge%d.csv' % merge_n)
        with open(output_filename, 'wb') as output_fp:
            writer = csv.writer(output_fp)
            merge_n += 1
            for _, row in heapq.merge(*[decorated_csv(filename, columns) for filename in merge_filenames]):
                writer.writerow(row)
        sorted_filenames.append(output_filename)

        del readers
        for filename in merge_filenames:
            os.remove(filename)
    return sorted_filenames[0]


def main():
    parser = OptionParser()
    parser.add_option('-c', '--column', dest='columns', action='append', help='column of CSV to sort on')
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
        args.columns = [int(column) if column.isdigit() else column for column in args.columns]
        csvsort(input_files[0], columns=args.columns, max_size=args.max_size, has_header=args.has_header, delimiter=args.delimiter)

 
if __name__ == '__main__':
    main()
