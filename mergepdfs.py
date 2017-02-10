"""
A simple python script that recursively merges all pdf files in a folder
and its subfolders. Looks for files with the format _____p#.pdf
where _____ is a common name and p# is the page number that the pdf should
be in the combined filed

"""
import os
import re
import sys

import PyPDF2

from send2trash import send2trash

send_for_future_iters = ''

def mergepdfs(root, recursive):
    """
    Merges all pdfs with page numbers located in root
    Also optionally trashes the old files depending on user input

    Args:
        root: The folder to search for pdfs to merge
        recursive: A Boolean value, True if method is being called recursively
                   (via the recursive_merge method), False otherwise
    """
    pdfs = {}
    # Get all the PDF filenames
    for filename in os.listdir(root):
        m = re.match(r'(.*?)(p\d+)\.pdf', filename, re.I)
        # Group them by filename for easier merging later
        if m is not None:
            if m.group(1) in pdfs:
                pdfs[m.group(1)].append(filename)
            else:
                pdfs[m.group(1)] = [filename]

    del_items = []
    # Sort the pdfs so they're in the right order when merged
    for k in pdfs:
        if len(pdfs[k]) > 1:
            pdfs[k].sort(key=sort_by_page_number)
        else:
            del_items.append(k)

    if del_items != []:
        print("Didn't combine the follow pdfs because only 1 page was found:")
    # Deleting lists that only contain 1 pdf
    for item in del_items:
        assert len(pdfs[item]) == 1, 'Should only delete items with'\
                                     + ' length == 1: ' + str(pdfs[item])
        print('   ' + pdfs[item][0])
        del pdfs[item]

    if pdfs == {} and not recursive:
        print('There are no pdf files to merge in this directory!')
        print('Make sure the file names include p# where # is the page',
              ' number you want the file to be in the new document')
        print('Example: testp1.pdf, testp2.pdf & test3.pdf would be',
              ' merged to create test.pdf where the order is p1->p2->p3')
        return
    elif pdfs == {} and recursive:
        print('No pdf files to merge found in %s' % root)
        return

    # Looping through all pdf files with multiple pages and saving
    # them as new combined pdfs.
    print('In folder: '+root)
    print('Combining and saving pdfs:')
    for k in pdfs:
        pdf_writer = PyPDF2.PdfFileWriter()
        m = re.match(r'(.*?)(p\d)\.pdf', pdfs[k][0])

        savepath = os.path.join(root, m.group(1) + '.pdf')
        if os.path.exists(savepath):
            ans = get_answer('WARNING: A file of the name %s already exists.'
                             % savepath + ' Overwrite it? (y/n)', ['y', 'n'])
            if ans == 'n':
                continue # Skip combining and saving the pdf
            else:
                send2trash(savepath) # Sending to trash instead of overwriting
                                     # in case of user error
        first_page = True
        # Adding all the pages in the various pdf files to a new pdf file
        for pdf in pdfs[k]:
            if first_page:
                print('   ' + pdf)
                first_page = False
            else:
                print('   + ' + pdf)
            pdf_file_obj = open(os.path.join(root, pdf), 'rb')
            pdf_reader = PyPDF2.PdfFileReader(pdf_file_obj)
            for page_num in range(pdf_reader.numPages):
                page_obj = pdf_reader.getPage(page_num)
                pdf_writer.addPage(page_obj)
        print('   = ' + m.group(1) + '.pdf\n')
        # Saving the file
        pdf_output = open(savepath, 'wb')
        pdf_writer.write(pdf_output)
        pdf_output.close()

    global send_for_future_iters
    if send_for_future_iters == '' and recursive:
        ans = get_answer('Would you like to send the old files to the trash?\n'
                         + 'Type (y/n) to send/not send all old files in'
                         + ' this folder to the trash.\nOr type (y-all/n-all)'
                         + ' to send/not send all old files for this folder'
                         + ' and all future folders to the trash.\n(Choice'
                         + ' doesn\'t carry over between runs of the script)',
                         ['y', 'n', 'y-all', 'n-all'])
        if ans == 'y-all':
            send_for_future_iters = ans
            ans = 'y'
        elif ans == 'n-all':
            send_for_future_iters = ans
            ans = 'n'
    elif not recursive:
        ans = get_answer('Would you like to send the old files to the trash?'
                         + ' (y/n)', ['y', 'n'])
    else:
        if send_for_future_iters == 'y-all':
            ans = 'y'
        else:
            ans = 'n'

    if ans == 'y':
        print('Trashing the following files in %s:' % root)
        for k in pdfs:
            for old_pdf in pdfs[k]:
                print('   ' + old_pdf)
                send2trash(os.path.join(root, old_pdf))

def recursive_merge(dirpath):
    """
    Calls the mergepdfs function for all folders within dirpath
    
    Args:
        dirpath: The root that contains all the folders to recursively visit
    """
    for root, dirs, files in os.walk(dirpath):
        mergepdfs(root, True)

def sort_by_page_number(filename):
    """
    Returns the page number of the pdf as an int
    Used for sorting files by page number so they are in the correct order

    Args:
        filename: The filename to extract the page number from

    Returns:
        The page number found in the filename, returned as an int
    """
    return int(re.match(r'.*?p(\d+)\.pdf', filename, re.I).group(1))

def get_answer(message, options):
    """
    Gets an answer to message that is within the accepted options list

    Args:
        message: The message to prompt the user with
        options: A list containing the acceptable options

    Returns:
        The option the user picked from the list of options
    """
    assert len(options) > 0, 'options should have a length of > 0'
    assert isinstance(options, list), 'options should be a list'
    print(message)
    invalid_msg = ''
    if len(options) == 1:
        invalid_msg = 'Enter %s to continue' % options[0]
    elif len(options) == 2:
        invalid_msg = 'Enter %s or %s to continue' % (options[0], options[1])
    else:
        invalid_msg = 'Enter '
        for option in options[:-2]:
            invalid_msg += option + ', '
        invalid_msg += '%s or %s to continue' % (options[-2], options[-1])

    ans = input()
    while ans not in options:
        print(invalid_msg)
        ans = input()

    return ans

def main():
    if len(sys.argv) < 2:
        print('ERROR: Need a argument for the directory being used')
        print('Usage: python3 mergepdfs.py /path/to/folder')
        sys.exit()

    filepath = sys.argv[1]
    # Recombining filepath if it was split because of spaces
    for arg in sys.argv[2:]:
        filepath += ' ' + arg

    if not os.path.isdir(filepath):
        print('Error: Path provided doesn\'t exist and/or isn\'t a folder')
        print('Path entered was: '+filepath)
        sys.exit()

    ans = get_answer('Would you like to merge pdfs in this folder and all'\
                     + ' subfolders? (y/n)', ['y', 'n'])

    # Inserting blank line for readability
    print()
    if ans == 'y':
        recursive_merge(filepath)
    elif ans == 'n':
        mergepdfs(filepath, False)


main()
