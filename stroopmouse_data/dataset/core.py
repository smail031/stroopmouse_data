import h5py
import os
from datetime import datetime
import numpy as np

#data_repo = ('/Users/smaille/University of Ottawa/BeiqueLab - Documents/'
#             'Data/Behaviour Data/Sebastien/Dual_Lickport/Mice')
#dataset_repo = '/Users/smaille/Repositories/behavior_analysis/datasets/'
#dataset_search(data_repo, dataset_repo)

def dataset_edit(data_repo, dataset_repo):
    create_edit = input('Create(c) new dataset or edit(e) existing dataset?: ')

    if create_edit == 'e':
    
        while True:
            fname = input('Enter dataset name (ls:list): ')
            
            if fname == 'ls':
                print(sorted(os.listdir(dataset_repo)))
                
            elif f'{fname}.hdf5' in os.listdir(dataset_repo):
                print(f'Opening {fname}.hdf5')
                break
            
            else:
                print('Not recognized.')
                
    elif create_edit == 'c':
        fname = input('Enter new dataset name: ')
        print(f'Creating {fname}.hdf5')
        
    dset_path = f'{dataset_repo}{fname}.hdf5'
    dset = DataSet(dset_path, data_repo)
    dset.choose_mouse()

    
class DataSet():
    '''
    A class to handle creation and editing of a dataset file.

    Attributes:
    -----------
    self.hdf: h5py object
        h5py object representing the hdf5 file for this dataset.

    self.data_repo: str
        The path to the data repository.

    self.activity_log: h5py group object
        The h5py group for the activity log in which all changes are documented.

    self.mouse_list: list
        List of all mouse names in the current dataset file.

    self.all_mice: list
        List of all mice available in the dataset repo.

    self.mouse_objects: list
        A list of mouse objects for each of the mice in the dataset file.
    
    self.log_counter: int
        Counts items added to activity log in the current session
        (to prevent overwriting previous items).
    '''
    def __init__(self, filepath:str, data_repo:str):
        self.hdf = h5py.File(filepath, 'a')
        self.data_repo = data_repo
        self.activity_log = self.hdf.require_group('Activity log')
        self.mouse_list = [i for i in list(self.hdf.keys()) if i != 'Activity log']
        self.all_mice = sorted(os.listdir(self.data_repo))
        self.all_mice.remove('test')
        self.all_mice.remove('.DS_Store')
        self.mouse_objects = []
        self.log_count = 0
        
        for ms in self.mouse_list:
            self.mouse_objects.append(Mouse(ms, self.hdf[ms], self, data_repo))

        edit_msg = input('Describe your changes: ')
        self.log_event(f'User Message: {edit_msg}')

    def log_event(self, comment:str):
        '''Add a comment to the activity log for this dataset'''
        now = datetime.now()
        attr_name = now.strftime('%Y-%m-%d %H:%M:%S')
        self.activity_log.attrs[f'{attr_name} ({str(self.log_count).zfill(3)})'
                                ] = comment
        self.log_count += 1 # Log count ensures comments aren't overwritten.
        
    def add_mouse(self, mouse:str):
        '''Add a mouse to the mouse list and mouse object list.'''
        if mouse not in self.mouse_list:
            self.mouse_list.append(mouse)
            self.hdf.require_group(mouse)
            self.mouse_objects.append(Mouse(mouse, self.hdf[mouse],
                                            self, self.data_repo))
            self.log_event(f'Added mouse {mouse}')

        obj = [ms for ms in self.mouse_objects if ms.name==mouse][0]
        obj.choose_dates()
        
    def delete_mode(self):
        '''Remove a mouse from the mouse list and mouse object list.'''
        print('----------DELETE MODE----------')
        while True:
            mouse = input('Enter mouse number to be removed '
                          '(q:quit, lsf:list mice in file) :')
            
            if mouse == 'q':
                break

            elif mouse == 'lsf':
                print(self.mouse_list)
            
            elif mouse in self.mouse_list:
                self.mouse_list.remove(mouse)
                del self.hdf[mouse]
                self.mouse_objects = [ms for ms in self.mouse_objects
                                      if ms.name!=mouse]
                self.log_event(f'Removed mouse {mouse}')

            else:
                print('Not recognized.')

    def choose_mouse(self):
        '''Prompts the user to choose a mouse.'''
        while True:
            mouse = input('Enter mouse number (q:quit, h:help): ')

            if mouse == 'q':
                break

            elif mouse == 'h':
                print('q:quit, ls:list all mice, lsf:list mice in file, '
                      'rm:delete mode, log:print log')

            elif mouse == 'ls':
                print(self.all_mice)

            elif mouse == 'lsf':
                print(self.mouse_list)

            elif mouse == 'rm':
                self.delete_mode()

            elif mouse == 'log':
                for item in self.activity_log.attrs:
                    print(f'{item}: {self.activity_log.attrs[item]}')

            elif mouse in self.all_mice:
                self.add_mouse(mouse)

            else:
                print('Not recognized.')
    

class Mouse():
    '''
    A class to work with mice in a dataset file.

    Attributes:
    -----------
    self.name: str
        A string containing the ID number of this mouse.
    
    self.group: h5py group object
        The h5py group that corresponds to this mouse in the dataset file.

    self.dataset: object
        The current dataset (used for logging events).

    self.date_repo: str
        The path to all dates for this mouse.

    self.all_dates: list
        A list containing all dates in the date repo.

    self.date_list: list
        A list of dates currently in the dataset file under this mouse.

    self.date_objects: list
        A list of Date objects corresponding to each date in date_list.
    '''
    def __init__(self, name:str, hdf_group:object,
                 dataset:object, data_repo:str):
        self.name = name
        self.group = hdf_group
        self.dataset = dataset
        self.date_repo = f'{data_repo}/{self.name}'
        self.all_dates = sorted(os.listdir(self.date_repo))
        if '.DS_Store' in self.all_dates:
            self.all_dates.remove('.DS_Store')
        self.date_list = list(self.group.keys())
        self.date_objects = []

        for date in self.date_list:
            block_path = f'{self.date_repo}/{date}/'
            self.date_objects.append(Date(date, self.group[date],
                                          block_path, self, self.dataset))

    def add_date(self, date:str):
        '''Add a date for this mouse to the dataset.'''
        # Remove date first to avoid redundancy.
        self.remove_date(date)
        self.date_list.append(date)
        self.group.require_group(date)
        block_path = f'{self.date_repo}/{date}/'
        obj = Date(date, self.group[date], block_path, self, self.dataset)
        self.date_objects.append(obj)
        obj.choose_blocks()

    def delete_mode(self):
        '''Remove a date for this mouse from the dataset.'''
        print('----------DELETE MODE----------')
        while True:
            date = input('Enter a date (yyyy-mm-dd) to be removed '
                         '(q:quit, lsf:list dates in file): ')
            
            if date == 'q':
                break

            elif date == 'lsf':
                print(self.date_list)
            
            elif date in self.date_list:
                self.remove_date(date)
                self.dataset.log_event(f'Removed {date}')
                print(f'Removed {date}.')

            else:
                print('Not recognized')

    def remove_date(self, date:str):
        '''Remove a date from the date list, object list and dataset file.'''
        if date in self.date_list:
            self.date_list.remove(date)
            del self.group[date]
            self.date_objects = [dt for dt in self.date_objects
                                 if dt.date!=date]

    def list_protocols(self):
        '''List all available dates with the protocol used on that date.'''
        for date in self.all_dates:
            date_directory = f'{self.date_repo}/{date}'
            last_exp = sorted(os.listdir(date_directory))[-1]

            with h5py.File(f'{date_directory}/{last_exp}', 'r') as w:

                if 'protocol_name' in w.attrs:
                    protocol_name = w.attrs['protocol_name']
                    print(f'{date}: {protocol_name}')
                    
                else:
                    print(date)

    def range_mode(self):
        '''Add all dates within a certain range'''
        print('----------RANGE MODE----------')
        start_date = input('Enter start date (yyyy-mm-dd): ')
        end_date = input('Enter end date (yyyy-mm-dd): ')

        if (start_date in self.all_dates) and (end_date in self.all_dates):
            start_index = self.all_dates.index(start_date)
            end_index = self.all_dates.index(end_date)+1
            date_range = self.all_dates[start_index:end_index]

            for date in date_range:
                self.add_date(date)

        else:
            print('Dates not recognized.')
        

    def choose_dates(self):
        '''Prompts the user to choose a date.'''
        while True:
            date = input('Enter date yyyy-mm-dd (q:quit, h:help): ')

            if date == 'q':
                break

            elif date == 'h':
                print('q:quit, ls:list all dates, lsf:list dates in file, '
                      'lsp:list dates with protocol, rg:range mode, '
                      'rm:delete mode')

            elif date == 'ls':
                print(self.all_dates)

            elif date == 'lsf':
                print(self.date_list)

            elif date == 'lsp':
                self.list_protocols()

            elif date == 'rg':
                self.range_mode()

            elif date == 'rm':
                self.delete_mode()

            elif date in self.all_dates:
                self.add_date(date)

            else:
                print('Not recognized.')

            
class Date():
    '''
    A class to handle all experiment blocks for a given mouse on a given day.

    Attributes:
    -----------
    self.date: str
        The date (format: 'yyyy-mm-dd').

    self.hdf_group: h5py object
        The h5py group corresponding to this group in the dataset file.

    self.block_path: str
        The path to all blocks for this date.
    
    self.mouse: object
        The Mouse object corresponding to this date.

    self.dataset: object
        The DataSet object corresponding to this date (for logging events).

    self.all_blocks: list
        List of all available blocks for this date.
    '''
    def __init__(self, date:str, hdf_group:object, block_path:str,
                 mouse:object, dataset:object):
        self.date = date
        self.hdf_group = hdf_group
        self.block_path = block_path
        self.mouse = mouse
        self.dataset = dataset
        self.all_blocks = os.listdir(block_path)
        self.all_block_numbers = [block[-6] for block in self.all_blocks]


    def add_block(self, blocks:list):
        '''Adds the selected block to the dataset.'''
        # First remove any existing blocks.
        if 'blocks' in list(self.hdf_group.keys()):
            del self.hdf_group['blocks']
        # Convert list to dict and back to list to remove duplicates.
        blocks = list(dict.fromkeys(blocks))
        block_list = []

        for block in blocks:
            block_number = block[-6] # Block number is at that index of filename.
            block_list.append(block_number)
            print(f'Added {block}')
            self.dataset.log_event(f'Added {block}')

        self.hdf_group['blocks'] = block_list

    def check_experiment_msg(self, block:str) -> bool:
        '''
        Checks the hdf5 file to confirm whether the experimenter warned against
        using this data (because of errors). If so, provides the user with the 
        experimenter-generated messsage and asks whether to add the block.

        Returns:
        --------
        Bool: Whether or not the block should be added to the dataset.
        '''
        with h5py.File(f'{self.block_path}/{block}', 'r') as f:
            
            if 'n' in f.attrs['experimental_quality']:
                message = f.attrs['experimental_message']
                print(f'EXPERIMENTAL ERROR MESSAGE for {block}: {message}')
                use_data = input('Are you sure you sure this block should be'
                                 'added? (y/n): ')
                if 'y' in use_data:
                    return True
                else:
                    return False

            else:
                return True
        
    def choose_blocks(self):
        '''Prompts the user to select a block to add.'''
        if len(self.all_blocks) == 1:
            # If there is only 1 block, that block will be added automatically.
            if self.check_experiment_msg(self.all_blocks[0]):
                self.add_block([self.all_blocks[0]])

        else:
            blocks_to_add = []
            while True:
                block_num = input('Enter block number (q:quit, ls:list blocks, '
                                  'lsf:list selected blocks): ')

                if block_num == 'q':
                    break

                elif block_num == 'ls':
                    print(sorted(self.all_block_numbers))

                elif block_num == 'lsf':
                    print([i[-6] for i in blocks_to_add])

                elif block_num in self.all_block_numbers:
                    block = self.all_blocks[self.all_block_numbers.index(
                        block_num)]
                    if self.check_experiment_msg(block):
                        blocks_to_add.append(block)

                else:
                    print('Not recognized.')

            self.add_block(blocks_to_add)
