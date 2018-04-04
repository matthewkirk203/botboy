"""Serves as a library for easier sql queries"""

def select(table_name, column_names = "*" : list, WHERE = None : list, GROUP = None, HAVING = None, ORDER_BY = None):
  query = "SELECT "
  if column_names == "*":
    query += "*"
  else:
    query += ','.join(column_names)
  
  query += " " + table_name
  
  if WHERE != None:
    query += " WHERE " + "AND ".join[WHERE]
    
  if ORDER_BY != None:
    query += " ORDER BY " + ORDER_BY
    
  #I'll do the rest later
  return query
  
def insert(table_name, values : list, column_names = None : list)
  query = "INSERT INTO " + table_name
  if column_names != None:
    query += " (" + ",".join(column_names) + ")"
  query += " VALUES("
  # Strings (varchars) need to be enclosed in single quotes. Build correct type list
  new_values = []
  for value in values:
    if str(value).isnumeric():
      new_values.append(value)
    else:
    # Maybe this won't work? Might have to hard code single quotes
      new_values.append(str(value))
  query += ','.join(new_values) + ")"
  return query
