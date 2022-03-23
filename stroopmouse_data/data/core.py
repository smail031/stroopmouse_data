import h5py
import numpy as np
import os

#data_repo_path = ('/Users/smaille/University of Ottawa/BeiqueLab - Documents/'
#                  'Data/Behaviour Data/Sebastien/Dual_Lickport/Mice/')
#dataset_repo_path = './datasets/'

class Experiment():
    '''
    A base class to work with a .hdf5 file containing data recorded in a single
    behavior experiment. Is instantiated by an object of class Mouse.

    Attributes:
    -----------
    self.mouse: str
        Number corresponding to this mouses ID.
    self.date: str
        Date on which the experiment took place.
    self.block: str
        Number corresponding to the experimental block for that mouse/date.
    self.data: h5py.File object
        The h5py object containing all experimental data.
    self.num_trials: int
        The number of trials in the corresponding experiment.

    '''
    def __init__(self, mouse, date, block, data_repo):
        '''
        Arguments:
        ----------
        mouse: str
            Number corresponding to this mouse's ID.
        date: str
            Date on which the experiment took place.
        block: str
            Number corresponding to the experimental block for that mouse/date.
        '''
        self.mouse = mouse
        self.date = date
        self.block = block
        self.data_repo = data_repo

        data_path = (f'{self.mouse}/{self.date}/'
            f'ms{self.mouse}_{self.date}_block{self.block}.hdf5')
        full_path = data_repo + data_path

        self.data = h5py.File(full_path, 'r')
        print(f'Opening mouse {self.mouse}, {self.date},'
            f'block {self.block}')

                
class Mouse():
    '''
    A class to work with all experimental data for a single mouse in a
    dataset file. Is instantiated by a DataSet object, and creates instances
    of class Experiment.

    Attributes:
    -----------
    self.mouse_number: str
        A number (in str) corresponding to this mouse's ID.
    self.mouse_group: h5py group object
        Object to work with the mouse's group in the dataset file.
    self.experiments: list of obj (Experiment)
        A list containing an instance of class Expriment for each experiment 
        on this mouse in the dataset.

    Methods:
    --------
    self.get_experiments(date_list):
        Returns a list containing an instance of class Experiment for each
        experiment associated with this mouse.
    self.get_data():
        Returns selected data from all experiments for this mouse in either
        a single 1D numpy array or nested numpy arrays.
    '''
    def __init__(self, mouse_number, mouse_group, data_repo):
        self.mouse_number = mouse_number
        self.mouse_group = mouse_group
        self.data_repo = data_repo
        self.date_list = list(self.mouse_group.keys())
        self.experiments = self.get_experiments(self.date_list)
     
    def get_experiments(self, date_list):
        '''
        Instantiates an object of class Experiment for each experiment in
        the dataset for this mouse. Returns a list of these objects. This
        method is called in __init__.

        Returns:
        --------
        experiments: list
            A list of objects from the Experiments class.
        '''
        experiments = []

        for date in self.date_list:
            block_list = self.mouse_group[date]['blocks']

            for block in block_list:
                block_number = block.decode('utf-8')

                experiments.append(Experiment(
                    self.mouse_number, date, block_number, self.data_repo))
        return experiments

    def get_data(self, hdf_data_path: str, vector: bool = False,
                 attr: bool = False, string: bool = False) -> np.ndarray:
        '''
        Extract specified data from all experiments for this mouse. 

        Arguments:
        ----------
        hdf_data_path (str): The path, in the hdf5 file, to the data 
            (ex.'sample-tone/freq')
        vector (bool, False): Indicates whether the data should be returned as
            a vector (all experiments concatenated) or not (nested 1d arrays).
        attr (bool, False): Indicates whether to look for an HDF5 attribute.

        Returns:
        --------
        data (np.array): Requested data from each experiment for this mouse
            either as a single 1D array or nested 1d arrays.
        '''
        data = np.empty(len(self.experiments), dtype=np.ndarray)
        
        for exp in range(len(self.experiments)):
            
            if attr:
                data[exp] = self.experiments[exp].data.attrs[hdf_data_path]
            else:
                data[exp] = np.array(self.experiments[exp].data[hdf_data_path])

            if string:
                data[exp] = data[exp].astype(str)
            
        if vector:
            data = as_vector(data)
            
        return data
        
   
class DataSet():
    '''
    A class to handle datasets containing data from several experiments from
    several different mice. Creates instances of class Mouse.

    Attributes:
    -----------
    self.dataset: h5py File object

    self.mouse_list: list of str

    self.mouse_objects: list of obj (Mouse)
    
    Methods:
    --------
    self.get_mice():
        Returns self.mouse_list, a list of all mice in the dataset.
    self.get_mouse_objects():
        Returns a list containing an instance of class Mouse for each
        mouse in the dataset.
    self.get_weights():
        Returns the daily weights for each mouse in mouse_objects.
    self.get_performance_experiment():
        Returns the fraction of correct trials for each experiment for 
        each mouse in the dataset.
    self.get_post_reversal_performance:
        For each reversal for each mouse, returns a nested vectors for 
        performance for a given number of trials post-reversal.
    '''
    
    
    def __init__(self, filename, data_repo, dataset_repo):
        '''
        '''
        print(f'Opening {filename}.hdf5')
        self.dataset = h5py.File(f'{dataset_repo}{filename}.hdf5','r')
        self.data_repo = data_repo
        self.mouse_list = [i for i in list(self.dataset.keys())
                           if i != 'Activity log']
        self.mouse_objects = self.get_mouse_objects(self.mouse_list)

    def get_mouse_objects(self, mouse_list):
        '''
        For each mouse in mouse_list, instantiates an object of class
        Mouse. 
        
        Arguments:
        ----------
        mouse_list: list(str)
            A list containing the ID numbers of each relevant mouse.

        Returns:
        mouse_objects: list(Mouse objects)
            A list containing an instance of class Mouse for each mouse
            in mouse_list
        '''
        mouse_objects = []
        for mouse in mouse_list:
            mouse_group = self.dataset[mouse]
            mouse_objects.append(Mouse(mouse, mouse_group, self.data_repo))
        return mouse_objects
        
    
def as_array(nested_vectors):
    '''
    Converts a 1D numpy array with nested 1D numpy arrays of variable length
    into a single 2D numpy array, with width equal to length of the longest
    nested array. Missing values are np.nan.

    Arguments:
    ----------
    nested_vectors: 1D numpy array, dtype=np.ndarray
        1D numpy array with nested 1D numpy arrays (can be different lengths).

    Returns:
    --------
    output_array: 2D numpy array
        2D numpy array containing all nested vectors, with np.nan in missing
        places.
    '''

    max_length = max([len(i) for i in nested_vectors])
    output_array = np.empty(shape=[len(nested_vectors), max_length])
    output_array.fill(np.nan)

    for vector in range(len(nested_vectors)):
        vector_length = len(nested_vectors[vector])
        output_array[vector,0:vector_length] = nested_vectors[vector]

    return output_array

def as_vector(nested_vectors):
    '''
    Converts a 1D numpy array with nested 1D numpy arrays of variable length
    into a single 1D numpy array with all data concatenated.

    Arguments:
    ----------
    nested_vectors: 1D numpy array, dtype=np.ndarray
        1D numpy array with nested 1D numpy arrays (can be different lengths).

    Returns:
    --------
    output_array: 1D numpy array
        1D numpy array containing all vectors concatenated together. 
    '''
    output_vector = np.array([])

    for vector in nested_vectors:
        output_vector = np.append(output_vector, vector)
    return output_vector

def dataset_load(data_repo, dataset_repo):
    '''
    Gets the user to choose one of many dataset files in dataset_repo.
    Once these datasets are chosen, a corresponding DataSet object is 
    instantiated and appended to a list.

    Returns:
    --------
    datasets: list (DataSet objects)
        A list containing a DataSet object for each selected dataset file.
    dataset_names: list (str)
        A list containing a user input name for each selected dataset.
        To be used as label in figures.
    '''
    datasets = []
    dataset_names = []
    file_search = True
    while file_search == True:   
        fname = input('Enter dataset name (ls:list): ')
        
        if fname == 'ls':  
            print(sorted(os.listdir(dataset_repo)))
            
        elif f'{fname}.hdf5' in os.listdir(dataset_repo):
            datasets.append(DataSet(fname, data_repo, dataset_repo))
            dataset_names.append(input('Enter label for this dataset: '))
            
            if input('Add another dataset?(y/n): ') == 'n':
                file_search = False
                
        else:
            print('Dataset file not found.')

    return datasets, dataset_names
