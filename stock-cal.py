"""
A simple python script that reads a file containing stock holdings, tries to
download the current price of those holdings and then prints out their values
in a readable table format. Future work will involve saving results and
allowing comparisons to historical performance.
"""
import argparse
import decimal
import os
import re
import requests

# The base url being used to get current stock prices
base_url = 'https://finance.google.com/finance/info?client=ig&q=NASDAQ%3A'

# TODO: Work on adding historical holdings
#save_file_loc = os.path.join('.','historical_holdings.txt')
# Future work:
# args:
    # -s - save results in default location
    # -s ______ save results in
    # -h print out historical performance with current performance
    # -ho print out historical performance only

    #Other actions:
    # compare to historical performance

def read_holdings(file_loc):
    """
    Reads the holdings file based on location given by file_loc and returns
    a dictionary of the ticker symbols and their quantities

    Args:
        file_loc: The location of the holdings file (it contains the ticker
                  symbols and the quantity owned)

    Returns:
        A dictionary where the key is the holding symbol and the value is
        the number of shares held
    """
    print('Reading the holdings file...')
    txt_regex = re.compile(r'(\w{1,5})\s*-\s*(\d+\.?\d*)')
    txt_file = open(file_loc)
    txt_file_contents = txt_file.read()
    result = txt_regex.findall(txt_file_contents)
    holdings = {}
    for symbol, amount in result:
        holdings[symbol] = amount

    return holdings

def download_info(url, indent):
    """
    Gets the price info for the ticker symbols (encoded in the url) and parses
    the response so that only the symbol and price are kept and everything
    else is discarded.

    Args:
        url: The url used to download the symbol prices
        indent: A Boolean value that determines whether to indent the message
                (used for readability)

    Returns:
        A list of tuples containing the ticker symbols and prices
    """
    if indent:
        print('   Requesting the pricing information...')
    else:
        print('Requesting the pricing information...')
    res = requests.get(url, timeout=3.0)
    res_regex = re.compile(r'"t"\s:\s"(\w{1,5})"(?:\n|.)*?"l_fix"\s:\s"(\d+\.?\d*)"')
    result = res_regex.findall(res.text)

    return result

def sanity_check(holdings, download):
    """
    The Google Finance API sometimes doesn't return info for all symbols
    (no idea what that's the case). This function checks to see if info
    for all symbols was downloaded and if not, calls a function that tries
    to download the missing info.

    Args:
        holdings: A dictionary where the key is the ticker symbol and the
                  value is the number of shares held of that stock
        download: A list of tuples containing the ticker symbols and their
                  current prices

    Returns:
        The download list that was passed in with any redownloaded info
        (that could be downloaded) appended
    """
    print('Making sure all pricing info was downloaded...')
    found = False
    all_found = True
    not_found = []

    # Loops through all the ticker symbols and makes sure the download contains
    # each of them
    for holding in holdings.keys():
        for entry in download:
            if holding == entry[0]:
                found = True
                break

        if not found:
            print('ERROR: %s was not downloaded' % holding)
            all_found = False
            not_found.append(holding)

        found = False

    if all_found:
        print('All pricing info correctly downloaded!')
    else:
        res = redownload_info(not_found)
        for tup in res:
            download.append(tup)

    return download

def redownload_info(not_found):
    """
    Tries to redownload the pricing info that wasn't downloaded the first time

    Args:
        not_found: A list of the symbols that weren't returned in the first
                   download

    Returns:
        A list of tuples containing the ticker symbol and its current price
        (if we were able to successfully redownload that info)
    """
    info = []
    try_again = []
    for holding in not_found:
        print('Retrying download of %s...' % holding)
        url = base_url + holding
        res = download_info(url, True)
        if len(res) == 1 and holding in res[0]:
            print('   Successfully downloaded %s info!' % holding)
            info.append(res[0])
        else:
            print('   Second attempt to download %s info failed' % holding)
            try_again.append(holding)

    not_downloaded = []
    for holding in try_again: # Wasn't found in previous download, try again
        print('Final attempt at downloading %s...' % holding)
        # Seems that adding Apple to the url sometimes gets it to work
        url = base_url + 'AAPL,' + holding
        res = download_info(url, True)
        if len(res) == 2 and holding in res[1]:
            print('   Successfully downloaded %s info!' % holding)
            info.append(res[1])
        else:
            print('   Third attempt to download %s info failed' % holding)
            not_downloaded.append(holding)

    # Print out symbols that failed all 3 download attempts
    if not_downloaded:
        print('The following symbols couldn\'t be downloaded:')
    for holding in not_downloaded:
        print('   ' + holding)

    return info

def print_holdings(holdings, result):
    """
    Prints out the holdings & price info in a readable table format

    Args:
        holdings: A dictionary where the key is the ticker symbol and the
                  value is the number of shares held of that stock
        result: A list of tuples containing the ticker symbols and current
                prices for those stocks
    """
    print('Printing financial information...')
    total_val = 0
    # Calculating total value early to allow percentage calculations
    for res in result:
        sym = res[0]
        price = decimal.Decimal(res[1])
        num_shares = decimal.Decimal(holdings[sym])
        total_val += decimal.Decimal(price * num_shares)

    value = 0.0
    print('%s %s %s %s %s' % ('Symbol'.ljust(15), 'Shares Held'.ljust(15),
                              '% of Total'.ljust(15), 'Price'.ljust(15),
                              'Worth'))
    for res in result:
        sym = res[0]
        price = decimal.Decimal(res[1])
        num_shares = decimal.Decimal(holdings[sym])
        value = decimal.Decimal(price * num_shares)
        percent = round((value / total_val) * 100, 2)
        print('%s %s %s %s %s' % (sym.ljust(15),
                                  str(round(num_shares, 2)).ljust(15),
                                  str(percent).ljust(15),
                                  str(round(price, 2)).ljust(15),
                                  str(round(value, 2))))
    print("Total Value: %.2f" % total_val)

def is_text_file(filepath):
    """
    Checks to see if the given filepath exists and is a text file
    (with extension .txt). Used for checking files given via command-line args

    Args:
        filepath: The filepath to check

    Raises:
        ArgumentTypeError: If the file doesn't exist or isn't a .txt file
    """
    if not os.path.isfile(filepath):
        msg = '%s is not a file\nNote: If you have spaces in the filepath,'\
              % filepath + ' you may need to escape them using a backslash'
        raise argparse.ArgumentTypeError(msg)
    if re.match(r'^.*\.txt$', filepath) is None:
        msg = '%s is not a text file' % filepath
        raise argparse.ArgumentTypeError(msg)

def main():
    parser = argparse.ArgumentParser(description='Calculate current and/or'
                                     + ' historical stock prices')
    parser.add_argument('-f', '--filename', type=is_text_file,
                        help='Optionally designate where the holdings file'
                        + ' is located')
    args = parser.parse_args()
    # Get the new holdings file if it was supplied
    if args.filename:
        file_loc = args.filename
    else:
        file_loc = os.path.join('.', 'holdings.txt')
    holdings = read_holdings(file_loc)

    # Getting the base url for stock prices
    url = base_url

    # Appending the ticker symbols onto the url
    for key in sorted(holdings):
        url += key + ','

    # Removing the trailing comma
    url = url[:-1]

    print('Url: '+url)

    result = download_info(url, False)

    result = sanity_check(holdings, result)

    print_holdings(holdings, result)

main()
