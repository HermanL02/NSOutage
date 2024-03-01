import os
from dotenv import load_dotenv
def load_environment_variable(var_name):
    var_value = os.getenv(var_name)
    if var_value is None:
        load_dotenv()  
        var_value = os.getenv(var_name)
    return var_value