# -*- coding: utf-8 -*-

# pylint: disable=W0221
# Since the arguemts for __call__ will change from class to calss

"""
Need to work out the licence
"""

import sys  

from core_hazimp.jobs.jobs import Job
from core_hazimp.misc import instanciate_classes

class Calculator(Job):
    """
    Abstract Calculator class. Should use abc then.
    """
    def __init__(self):
        """
        Initalise a Calculator object having the attributes
        allargspec_call and args_in.
        """
        super(Calculator, self).__init__()
    
                
    def calc(self):
        """
        The actual calculation.
        """
        pass
        
        
    def __call__(self, context, **kwargs):
        args_in = []
        for job_arg in self.context_args_in:
            # A calc with no input is ok.
            if not context.exposure_att.has_key(job_arg):
                    #FIXME add Error
                print "job_arg", job_arg
                print "NO CORRECT VARIABLES" 
                sys.exit() 
            args_in.append(context.exposure_att[job_arg])
        args_out = self.calc(*args_in, **kwargs)
        assert len(args_out) == len(self.args_out)
        for i, arg_out in enumerate(self.args_out):
            context.exposure_att[arg_out] = args_out[i]


class AddTest(Calculator):
    """
    Simple test class, adding args together.
    """
    def __init__(self):
        super(AddTest, self).__init__()
        self.args_out = ['c_test']
        self.context_args_in = ['a_test', 'b_test']
        self.call_funct = 'add_test'
    
    def calc(self, a_test, b_test):
        """
        Add args
        """
        return [a_test + b_test]
    

class MultiplyTest(Calculator):
    """
    Simple test class, multiplying args.
    """
    
    def __init__(self):
        super(MultiplyTest, self).__init__()
        self.context_args_in = ['a_test', 'c_test']
        self.args_out = ['d_test']
        self.call_funct = 'multiply_test'
    
    def calc(self, a_test, c_test):
        """
        Multiply args
        """
        return [a_test * c_test]
 

class MultipleValuesTest(Calculator):
    """
    Simple test class, returning two values.
    """
    
    def __init__(self):
        super(MultipleValuesTest, self).__init__()
        self.context_args_in = ['a_test', 'b_test']
        self.args_out = ['e_test', 'f_test']
        self.call_funct = 'multiple_values_test'
    
    def calc(self, a_test, b_test):
        """
        Return two values
        """
        return [a_test, b_test]
                       

class ConstantTest(Calculator):
    """
    Simple test class, returning two values.
    """
    
    def __init__(self):
        super(ConstantTest, self).__init__()
        self.context_args_in = []
        self.args_out = ['g_test']
        self.call_funct = 'constant_test'
    
    def calc(self, constant=None):
        """
        Return two values
        """
        return [constant*2]
                    
    

            
CALCS = instanciate_classes(sys.modules[__name__])
