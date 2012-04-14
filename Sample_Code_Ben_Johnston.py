#! /usr/bin/env python

'''
This module defines the following classes:

- TransactionInfo: a class which stores transaction information.
- DirToTransactionInfos: a class that creates list of TransactionInfo objects
  from a directory.
- UniqueUserInfo: a class that generates dictionary and list objects that
  contain percentile and usage data from DirToTransactionInfos objects.

********************************************************************************
                           NOTE TO READER
********************************************************************************
This module is designed to parse through a directory
of csv files containing transaction information for "Square" card reader transactions.

The files contain the following details, each in a different cell in one row:
- user_id: Username for the merchant using Squares card reader
- payment_id: Unique ID code for that individual transaction
- payment_amount: Amount processed
- card_present: Was the card present. Data contains a "TRUE" if it was, empty if not.
  if customer used their account with that merchant to pay instead of their
  credit card.
- created_at: Date of transaction

There is one transaction per row.
A sample row would contain five cells, here are some sample values:

benjohnston1985, f394fn93, 13.99, TRUE, 05/11/2011

Percentile information. I used the following paper for determining a percentile
distribution function table:

http://www.stanford.edu/class/archive/anthsci/anthsci192/
anthsci192.1064/handouts/calculating%20percentiles.pdf

Created by Ben Johnston on 2011-09-26.

'''

import os
from collections import defaultdict
import csv
 

class TransactionInfo(object):
    
    '''Class which stores the transaction information.'''
    
    def __init__(self, user_id,
                 payment_id, payment_amount, card_present, created_at):
        self.user_id = user_id
        self.payment_id = payment_id
        self.payment_amount = payment_amount
        self.card_present = card_present
        self.created_at = created_at


class DirToTransactionInfos(object):
    
    '''Class that creates list of TransactionInfo objects from a directory.'''
    
    def __init__(self, path_of_files):
        '''Take input string path_of_files.
        
        Instance Variables:
        self.path_of_files: a str, the directory where the files are stored.
        self.transactioninfo_list: a list, a flat list of TransactionInfo
        objects.
        
        '''
        self.path_of_files = path_of_files
        self.master_transactioninfo_list = list()
        self.below_transactioninfo_list = list()
        self.above_transactioninfo_list = list()
        self.update_transactioninfo_list()
        self.amount_spent()
    
    def extract_transaction_info(self, filename):
        '''Open file of str "filename" and return list of TransactionInfo objects.'''
        # os.path.join() joins filenames to path.
        path_and_filename = os.path.join(self.path_of_files, filename)
        f = open(path_and_filename, 'rU')
        individual_transactions = csv.reader(f)
        for transaction in individual_transactions:
            # Creates object of TransactionInfo class.
            transaction_info = TransactionInfo(*transaction)
            self.master_transactioninfo_list.append(transaction_info)
        f.close()
        return self.master_transactioninfo_list
    
    def update_transactioninfo_list(self):
        '''Update "self.transactioninfo_list" with info from files in "self.path_of_files".'''
        filenames_list = os.listdir(self.path_of_files)
        # Loops through filenames_list directory and parses each file
        # using self.extract_transaction_info() to create TransactionInfo objects
        for filename in filenames_list:
            transaction_info_list = self.extract_transaction_info(filename)
           
    
    def amount_spent(self):
	    '''Separate TransactionInfo objects into two lists based on payment_amount'''
        for each in self.master_transactioninfo_list:
            if int(each.payment_amount) <= 100:
                self.below_transactioninfo_list.append(each)
            else:
                self.above_transactioninfo_list.append(each)

class UniqueUserInfo(object):
    
    '''Class that generates percentile dictionary from list of TransactionInfo
    objects.'''
    
    def __init__(self, transactioninfo_list):
        '''Take input list of TransactionInfo objects
        
        Instance Variables:
        self.transactioninfo_list = a list, a flat list of TransactionInfo
        objects.
        
        self.unique_user_id_dct = a dict, a dict with the unique user_ids
        as keys and an integer as the value.
        
        self.percentages_list = a list, a flat list of floats
        
        self.percentile_dct= a dict, a dict with 1-99 as its keys representing
        percentiles values and the corresponding percentage as its values.
        
        self.user_id_freq= a dict, a dict containing the unique user_ids as
        keys and the number of times the user_id made a transaction as the
        values.
        
        '''
        self.transactioninfo_list = transactioninfo_list
        self.unique_user_id_dct = dict()
        self.percentages_list = list()
        self.percentile_dct = dict()
        self.user_id_freq = defaultdict(int)
        self.get_user_ids()
        self.get_card_present()
        self.get_user_freq()
        self.gen_percentages_list()
        self.gen_percentile_dict()
    
    def get_user_ids(self):
        '''Creates a dict of strings, the user_ids in self.transactioninfo_list.'''
        for each in self.transactioninfo_list:
            if not each.user_id in self.unique_user_id_dct:
                # Create user_id dict keys with 0 as value, 0 represents the counter
                # that will be used for counting the number of times the
                # card was present at a transaction.
                self.unique_user_id_dct[each.user_id] = 0
    
    def get_card_present(self):
        '''Increments number of times the card was present for each user_id in the dictionary: self.unique_user_id_dct'''
        for each in self.transactioninfo_list:
            if each.card_present:
                self.unique_user_id_dct[each.user_id] += 1
    
    def get_user_freq(self):
        '''Iterates through transactioninfo_list and creates dict with user_id as key and occurrences of that user_id as value '''
        for each in self.transactioninfo_list:
            self.user_id_freq[each.user_id] += 1
    
    def gen_percentages_list(self):
        '''Creates list of integers corresponding to card_present percentages for each user_id'''
        for each in self.unique_user_id_dct:
            num_card_present = float(self.unique_user_id_dct[each])
            num_transactions = float(self.user_id_freq[each])
            percent_card_present = 100*(num_card_present/num_transactions)  # percentage calculation
            self.percentages_list.append(round(percent_card_present))  #append each percentage to list
    
    def gen_percentile_dict(self):
        '''Outputs a dictionary with the percentile as its keys and corresponding card_present percentage as values.'''
        self.percentages_list = sorted(self.percentages_list)
        for nth_percentile in range(1, 100):
            # percentile formula for finding position on percentages list
            distribution_position = round((nth_percentile / 100.0)
                                        *len(self.percentages_list) + 0.5)
            self.percentile_dct[int(nth_percentile)] = (self.percentages_list
                                                  [int(distribution_position) - 1])
            # - 1 so self.percentages_list index correlates to distribution_position


if __name__ == "__main__":
    sample_transaction_obj = (DirToTransactionInfos
                              ('/Users/alisoncascio/python/square/sample'))
    #Creates DirToTransactionInfos object with a directory path.
    sample_percentile_obj_above= (UniqueUserInfo
                            (sample_transaction_obj.above_transactioninfo_list))
    for k,v in sample_percentile_obj_above.percentile_dct.items():
	    print k, ' : ', str(v)+'%'
    print '\n','*******************************************************************', '\n'
    sample_percentile_obj_below= (UniqueUserInfo
                            (sample_transaction_obj.below_transactioninfo_list))
    for k,v in sample_percentile_obj_below.percentile_dct.items():
	    print k, ' : ', v
	    







