__author__ = 'Amen Belayneh'

# This code is used to read the relations from a conceptnet dump, and
# return a container containing a list of lists of the relations

import sys

def ascii_lines(iterable):
    for line in iterable:
        if all(ord(ch) < 128 and ch not in "\\\"`" for ch in line):
            yield line

def csv(csv_file_path):
    ''' Reads from csv dump of conceptnet.'''
    # container for edges in conceptnet
    # Each element of the container is of the format
    # [rel,start,end,context,weight],
    # the context and weight element are included for future.

    # You have to open it in utf8 encoding because the conceptnet CSV file uses utf8.
    # Note that an English concept name can still contain unicode characters
    container = []
    #import codecs
    #with codecs.open(csv_file_path, 'r', encoding='utf-8') as stream:
    with open(csv_file_path, 'rb') as stream:
        # Determine file size to indicate progress reading the file.
        stream.seek(0, 2)
        file_size = stream.tell()
        stream.seek(0)
        printed_progress = -1

        for line in ascii_lines(stream):
            # Print the file read progress bar.
            read_progress = int(100 * stream.tell() / float(file_size))
            if read_progress >= printed_progress + 1:
                sys.stdout.write(str(read_progress) + "%  ")
                sys.stdout.flush()
                printed_progress = read_progress

            # convert it to ascii (required for atomspace) and remove \ or " or `
            #line = line.encode('ascii','xmlcharrefreplace')
            #line = line.replace("\\","").replace("\"","").replace("`","")
            temp = line.split('\t')
            columns_to_keep = temp[1:6]
            columns_to_keep.append(temp[9].strip())
            if (temp[2].startswith('/c/en/') and
             columns_to_keep not in container):
                container.append(columns_to_keep)

    # This line was presumably here to remove the header line from the file,
    # but the latest version of conceptnet no longer appears to have it.
    #TODO: Make some kind of a check or commandline switch to enable this if necessary.
    #del container[0]
    return container   # container is a list of lists

if __name__ == "__main__":
    url = raw_input("Enter file address: ")
    container = csv(url)
    print (container)
