import os
if not os.getcwd().split('/')[-1] == 'case':
    os.chdir('../../case')
#print('Current working directory: ', os.getcwd())

def show_function(function):
    import inspect
    from IPython.display import display, Markdown
    lines = inspect.getsource(function)
    display(Markdown('```python\n' + lines + '\n```'))