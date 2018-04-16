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

#TODO: Implement all the parameters.
def select(table_name, distinct = False, column_names = "*", condition = None, GROUP = None, HAVING = None, order = None):
  query = "SELECT "
  if distinct is True:
    query += "DISTINCT "
  if column_names == "*":
    query += "*"
  else:
    query += ','.join(column_names)
  
  query += " FROM " + table_name
  
  #TODO: Test
  if condition != None:
    query += " WHERE "
    conditions = list()
    for column, value in condition.items():
      conditions.append(column + "=" + sqlize(value))
    query += "AND ".join(conditions)
    
  if order != None:
    query += " ORDER BY " + order
    
  return query
  
def insert(table_name, values:list, column_names = None):
  query = "INSERT INTO " + table_name
  if column_names != None:
    query += " (" + ",".join(column_names) + ")"
  query += " VALUES("
  # Strings (varchars) need to be enclosed in single quotes. This has a bug somewhere I can feel it.
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
    sets.append(key + "=" + value)
  query += ",".join(sets)
  query += " WHERE "
  for k,v in condition.items():
    query += k + "=" + sqlize(v)
  return query
  
  
