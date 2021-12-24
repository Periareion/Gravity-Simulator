
print_format = "{k} has been set to {v}"

replace_dict = {
    ":"  : "=",
    " =" : "=",
    "= " : "="
    }

def evaluate(value):
    if '#' in value:
        return str(value)
    try:
        return eval(value)
    except (NameError, SyntaxError):
        return str(value)

def readLine(line):
    for wrong, correct in replace_dict.items():
        line = line.replace(wrong, correct)
    
    if "=" in line:
        key, value = (*line.split('=', 1),)
        
        value = evaluate(value)

        return key, value
    
    elif str(line).lower() == 'stop':
        return 'stop'
    
    else:
        return None

    #elif str(line).upper() == 'STOP':
        
    
def readConfig(config_file_name):
    config_file = open(config_file_name,'r')
    config_dict = {}

    config_text = config_file.read()

    config_lines = config_text.split('\n')
        
    for line in config_lines:
    
        contents = readLine(line)

        if contents == 'stop':
            break

        elif contents == None:
            continue
        
        elif len(contents) == 2:
            key, value = contents
            config_dict[key] = value
            print(print_format.format(k=key,v=value))

    return config_dict
