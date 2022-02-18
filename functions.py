import sys
import time
import pickle
import os.path

def repeatable_input(message, lambda_condition, datatype):
  while True:
    usrinput = input(message)
    try:
      datatype(usrinput)
      try:
        if lambda_condition(datatype(usrinput)) == True:
          break
      
        else:
          return [usrinput, False]
      except:
        [usrinput, False]
    except:
      return [usrinput, False]
  return [usrinput, True]

def repeatable_input_textbox(lambda_condition, datatype, textorentrybox):
  while True:
    usrinput = textorentrybox.get()
    try:
      datatype(usrinput)
      if lambda_condition(datatype(usrinput)) == True:
        break
    except:
      pass
  return usrinput

def scroll_text(message, scroll_speed=20) :
  for x in message:
    print(str(x), end="")
    time.sleep(scroll_speed/1000)
    sys.stdout.flush()

def create_save(name,num):
  dictionary = {"save" : str(num)}
  if(os.path.isfile(name + str(num) + ".txt")):
    pass
  else:
    f = open(name + str(num) + ".txt", "wb+") 
    pickle.dump(dictionary, f)
    f.close()  

def delete_save(name, num):
  os.remove(name + num + ".txt")

def save_data(file_name, key, entry):    
    f = open(file_name + ".txt", "rb+")
    currentdict = pickle.load(f)
    f.close()
    currentdict[key] = entry
    f = open(file_name + ".txt", "wb+") 
    pickle.dump(currentdict, f)
    f.close() 
    
def load_data(file_name, key):
  f = open(file_name + ".txt", "rb+")
  currentdict = pickle.load(f)
  f.close()
  if key in currentdict:
    return currentdict.get(key) 
  else:
    return None

def check_for_key(file_name, key):
  f = open(file_name + ".txt", "rb+")
  currentdict = pickle.load(f)
  f.close()
  if(key in currentdict):
    return True
  else:
    return False

def get_amount_of_entries(filename):
  f = open(filename + ".txt", "rb+")
  currentdict = pickle.load(f)
  f.close()
  return len(currentdict)

def load_whole_dictionary(filename):
  f = open(filename + ".txt", "rb+")
  currentdict = pickle.load(f)
  f.close()
  return currentdict




  
