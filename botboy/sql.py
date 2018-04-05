"""Serves as a library for easier sql queries"""

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
    
  #I'll do the rest later
  return query
  
def insert(table_name, values, column_names = None):
  query = "INSERT INTO " + table_name
  if column_names != None:
    query += " (" + ",".join(column_names) + ")"
  query += " VALUES("
  # Strings (varchars) need to be enclosed in single quotes. This has a bug somewhere I can feel it.
  new_values = []
  for value in values:
    if type(value) is str:
      value = "'" + value + "'"
      new_values.append(value)
    else:
      new_values.append(str(value))
  query += ','.join(new_values) + ")"
  return query

