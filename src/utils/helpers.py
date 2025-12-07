from datetime import datetime 

def execution_time(callback,**kwargs):
    start = datetime.now()
    callback(**kwargs)
    end = datetime.now()
    duration = (end - start).seconds 
    print(f'the process last : {duration}')