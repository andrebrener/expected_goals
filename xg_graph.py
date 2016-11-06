# =============================================================================
#          File: xg_graph.py
#        Author: Andre Brener
#       Created: 06 Nov 2016
# Last Modified: 
#   Description: description
# =============================================================================
import pandas as pd

import matplotlib.pyplot as plt

diff_table = diff_table[diff_table['result'] > 5]
goals = diff_table['result']
xg = diff_table['xg']
