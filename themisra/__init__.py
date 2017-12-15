__name__ = 'themisra'
__version__ = '0.1.1'
__minimum_isis_version__ = (3,4)

# Hard dependency on ISIS3
import pysis
pysis.check_isis_version(*__minimum_isis_version__)

# Conditional import if MPI is not available                                    
try:                                                                            
    from mpi4py import MPI                                                      
except:                                                                         
    import sys
    # If MPI is not available Mock in an MPI like interface                     
    class Comm():                                                               
        def __init__(self):                                                     
            self.rank = 0                                                       
        def Abort(self, n):                                                     
            sys.exit()                                                          
                                                                                
    class MPI_Wrapper():                                                        
        def __init__(self):                                                     
            self.COMM_WORLD = Comm()                                            
                                                                                
    MPI = MPI_Wrapper()

 
