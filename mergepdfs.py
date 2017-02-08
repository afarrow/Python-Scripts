import os
import re
import sys

import PyPDF2

from send2trash import send2trash

send_for_future_iters = ''

def mergepdfs(root, recursive):
    pdfFiles = {}
    # Get all the PDF filenames
    for filename in os.listdir(root):
        m = re.match(r'(.*?)(p\d+)\.pdf', filename, re.I)
        # Group them by filename for easier merging later
        if m is not None:
            if m.group(1) in pdfFiles:
                pdfFiles[m.group(1)].append(filename)
            else:
                pdfFiles[m.group(1)] = [filename]

    for k in pdfFiles:
        pdfFiles[k].sort(key=sort_by_page_number)

    if pdfFiles == {} and not recursive:
        print('There are no pdf files to merge in this directory!')
        print('Make sure the file names include p# where # is the page',
              ' number you want the file to be in the new document')
        print('Example: testp1.pdf, testp2.pdf & test3.pdf would be',
              ' merged to create test.pdf where the order is p1->p2->p3')
        return
    elif pdfFiles == {} and recursive:
        print('No pdf files to merge found in %s' % root)
        return

    # Looping through all pdf files with multiple pages and saving
    # them as new combined pdfs.
    for k in pdfFiles:
        pdfWriter = PyPDF2.PdfFileWriter()
        m = re.match(r'(.*?)(p\d)\.pdf', pdfFiles[k][0])
        
        # Adding all the pages in the various pdf files to a new pdf file
        for pdf in pdfFiles[k]:
            print('Opening ' + os.path.join(root, pdf))
            pdfFileObj = open(os.path.join(root, pdf), 'rb')
            pdfReader = PyPDF2.PdfFileReader(pdfFileObj)
            for pageNum in range(pdfReader.numPages):
                pageObj = pdfReader.getPage(pageNum)
                pdfWriter.addPage(pageObj)

        savepath = os.path.join(root, m.group(1) + '.pdf')
        if os.path.exists(savepath):
            ans = get_answer('WARNING: A file of the name %s already exists.'
                             % savepath + ' Overwrite it? (y/n)', ['y', 'n'])
            if ans == 'n':
                continue # Skipping the save part

        print('Saving %s to %s' % (m.group(1) + '.pdf', root))
        pdfOutput = open(savepath, 'wb')
        pdfWriter.write(pdfOutput)
        pdfOutput.close()

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
        for k in pdfFiles:
            for x in pdfFiles[k]:
                trashfile = os.path.join(root, x)
                print('Trashing: ' + trashfile)
                send2trash(trashfile)

def recursive_merge(dirpath):
    """Calls the mergepdfs function for all folders within dirpath"""
    for root, dirs, files in os.walk(dirpath):
        mergepdfs(root, True)

def sort_by_page_number(filename):
    """
    Returns the page number of the pdf as an int
    Used for sorting files by page # so they are in the correct order
    """
    return int(re.match(r'.*?p(\d+)\.pdf', filename, re.I).group(1))

def get_answer(message, options):
    """Gets an answer to message that is within the accepted options list"""
    assert len(options) > 0, 'options should have a length of > 0'
    print(message)
    invalid_msg = ''
    if len(options) == 1:
        invalid_msg = 'Enter %s to continue' % options[0]
    elif len(options) == 2:
        invalid_msg =  'Enter %s or %s to continue' % (options[0], options[1])
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
    #Recombining filepath if it was split because of spaces
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

