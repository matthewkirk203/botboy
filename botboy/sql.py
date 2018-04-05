"""Serves as a library for easier sql queries"""

def wrap_in_quotes(string:str):
  return "'" + string + "'"

def sqlize(value):
  """
  Checks the value to see if it needs to be wrapped in quotes for the SQL query.
  WORKS??!?!?
  """
  if type(value) is str:
    value = wrap_in_quotes(value)
  else:
    value = str(value)
  return value

#TODO: Change these to use dicts
def select(table_name, column_names = "*", WHERE = None, GROUP = None, HAVING = None, ORDER_BY = None):
  query = "SELECT "
  if column_names == "*":
    query += "*"
  else:
    query += ','.join(column_names)
  
  query += " FROM " + table_name
  
  if WHERE != None:
    query += " WHERE " + "AND ".join[WHERE]
    
  if ORDER_BY != None:
    query += " ORDER BY " + ORDER_BY
    
  #TODO: I'll do the rest later
  return query
  
def insert(table_name, values, column_names = None):
  query = "INSERT INTO " + table_name
  if column_names != None:
    query += " (" + ",".join(column_names) + ")"
  query += " VALUES("
  # Strings (varchars) need to be enclosed in single quotes. This has a bug somewhere I can feel it.
  #TODO: I can use sqlize here and will eventually do that.
  new_values = []
  for value in values:
    new_values.append(sqlize(value))
  query += ','.join(new_values) + ")"
  return query

def update(table_name, changing_columns:dict, condition:dict):
  """
  @param table_name The name of the table
  @param changing_columns The columns you want to change as a dictionary
  @param condition The column being used to find what row to change.
    This might be an id, a name, etc.
  """
  query = "UPDATE " + table_name + " SET "
  sets = []
  for key,value in changing_columns.items():
    sets.append(key + "=" + sqlize(value))
  query += ",".join(sets)
  query += " WHERE "
  for k,v in condition.items():
    query += k + "=" + sqlize(v)
  return query
  
  
