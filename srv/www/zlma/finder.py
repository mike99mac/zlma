#!/srv/venv/bin/python3
import subprocess
import sys
sys.path.append('/srv/www/zlma')
from zlma_buttons import Zlma_buttons

class Finder:
  def __init__(self):
    """
    Initialize globals, create page header, set background
    """
    self.pattern = ""                      # search pattern
    self.rows = []                         # resulting rows
    self.headers = ['Host name', 'LPAR', 'User ID', 'IP address', 'CPUs', 'GB Mem', 'Arch', 'Common arch', 'OS', 'OS ver', 'Kernel ver', 'Kernel rel', 'RootFS % full', 'Last ping', 'Created', 'App', 'Env', 'Group', 'Owner']


    # start the HTML page
    print('Content-Type: text/html')
    print()
    print('<!DOCTYPE html>')  
    print('<html><head>')

    # include jquery and three other libraries to make table editable
    print('<script type="text/javascript" src="/jquery-3.7.1.slim.min.js"></script>')
    print('<script type="text/javascript" src="/popper.min.js"></script>')
    print('<script type="text/javascript" src="/bootstrap.min.js"></script>')
    # TO DO: minimize bootstable when it is stable
    # print('<script type="text/javascript" src="/bootstable.min.js"></script>')
    print('<script type="text/javascript" src="/bootstable.js"></script>')
    print('<link rel="icon" type="image/png" href="/finder.ico">')
    print('<link rel="stylesheet" href="/zlma.css">') # common CSS's
    print('<link rel="stylesheet" href="/glyphicons-free.css">')   
    print('</head>')

    print('<body>') 
    zlma_buttons = Zlma_buttons("finder")  # add navigation buttons

  def add_menu_bar(self):
    """
    Add a menu bar with dropdowns for File, Edit, View, and Help
    """
    print('''
    <nav class="navbar navbar-expand-lg navbar-light bg-light">
      <a class="navbar-brand" href="#">Finder</a>
      <button class="navbar-toggler" type="button" data-bs-toggle="collapse" data-bs-target="#navbarNavDropdown" aria-controls="navbarNavDropdown" aria-expanded="false" aria-label="Toggle navigation">
        <span class="navbar-toggler-icon"></span>
      </button>
      <div class="collapse navbar-collapse" id="navbarNavDropdown">
        <ul class="navbar-nav">
          <li class="nav-item dropdown">
            <a class="nav-link dropdown-toggle" href="#" id="fileDropdown" role="button" data-bs-toggle="dropdown" aria-haspopup="true" aria-expanded="false">File</a>
            <div class="dropdown-menu" aria-labelledby="fileDropdown">
              <a class="dropdown-item" href="#">New</a>
              <a class="dropdown-item" href="#">Open</a>
              <a class="dropdown-item" href="#">Save</a>
              <div class="dropdown-divider"></div>
              <a class="dropdown-item" href="#">Exit</a>
            </div>
          </li>
          <li class="nav-item dropdown">
            <a class="nav-link dropdown-toggle" href="#" id="editDropdown" role="button" data-bs-toggle="dropdown" aria-haspopup="true" aria-expanded="false">Edit</a>
            <div class="dropdown-menu" aria-labelledby="editDropdown">
              <a class="dropdown-item" href="#">Cut</a>
              <a class="dropdown-item" href="#">Copy</a>
              <a class="dropdown-item" href="#">Paste</a>
              <a class="dropdown-item" href="#">Delete</a>
            </div>
          </li>
          <li class="nav-item dropdown">
            <a class="nav-link dropdown-toggle" href="#" id="viewDropdown" role="button" data-bs-toggle="dropdown" aria-haspopup="true" aria-expanded="false">
              View
            </a>
            <div class="dropdown-menu" aria-labelledby="viewDropdown">
              <a class="dropdown-item" href="#">Zoom In</a>
              <a class="dropdown-item" href="#">Zoom Out</a>
              <a class="dropdown-item" href="#">Full Screen</a>
            </div>
          </li>
          <li class="nav-item dropdown">
            <a class="nav-link dropdown-toggle" href="#" id="helpDropdown" role="button" data-bs-toggle="dropdown" aria-haspopup="true" aria-expanded="false">
              Help
            </a>
            <div class="dropdown-menu" aria-labelledby="helpDropdown">
              <a class="dropdown-item" href="#">Documentation</a>
              <a class="dropdown-item" href="#">About</a>
            </div>
          </li>
        </ul>
      </div>
    </nav>
    ''')

  def print_env(self):
    """
    Show all environment variables with the 'env' command
    """
    proc = subprocess.run("env", shell=True, capture_output=True, text=True)
    rc = proc.returncode
    env_vars = []
    env_vars = proc.stdout
    print('<pre>')
    for line in env_vars.split("\n"):
      print(str(line))
    print('</pre>')
    print()

  def search_cmdb(self):
    """
    Search zlma for pattern if included, else get all records
    """
    cmd = "/usr/local/sbin/zlma query"
    if len(self.pattern) > 1:              # search pattern specified
      cmd = f"{cmd} -p {self.pattern}"     # add -p <pattern> flag
    # print(f"search_cmdb() cmd: {cmd}<br>")
    try:
      proc = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    except Exception as e: 
      print(f"search_cmdb(): Exception calling zlma: {e}")
      exit(3)
    rc = proc.returncode
    self.rows = []
    row_list = proc.stdout.splitlines()
    for next_row in row_list: 
      list_row = next_row.split(",")
      self.rows.append(list_row)           # add list to list of rows

  def create_table(self, headers, data):
    """
    Given a list of table headers, and table data, produce an HTML table
    """
    html = "<table id='zlma-table'>\n" 
    html += "<tr>\n"
    for aHeader in headers:
      html += "  <th>"+aHeader+"</th>\n"
    html += "</tr>\n"
    for row in data:
      html += "<tr>\n"
      for cell in row:
        html += f"  <td>{cell}</td>\n"
      html += "</tr>\n"
    html += "</table>"
    return html

  def update_all(self):
    """
    Update all zlma records 
    """
    cmd = "/usr/local/sbin/zlma update"
    try:
      proc = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    except Exception as e: 
      print(f"search_cmdb(): Exception calling zlma: {e}")
      exit(3)

  def process_query(self):
    """
    Perform operation specified in env var QUERY_STRING.  There are two formats:
    - pattern=<pattern>
    - action=update
    """
    print('<h1>Finder search</h1>')
    proc = subprocess.run("echo $QUERY_STRING", shell=True, capture_output=True, text=True)
    rc = proc.returncode
    if rc != 0:
      print(f"Finder.process_query(): subprocess.run('echo $REQUEST_URI' returned {rc}")
      return 1
    query = []
    query = proc.stdout                    # get value
    query = query.split("=")
    verb = query[0]
    if verb == "action":                   # "update all" is only action
      self.update_all()
    else:                                  # assume pattern
      query_len = len(query)
      if query_len < 2:                    # no search pattern supplied
        self.pattern = ""                  # search for all
      else: 
        self.pattern = str(query[1])
    self.search_cmdb()                     # do search
    
    # print(f'<p> query: {query}<br>')
    # show the search pattern text box and submit button
    print('<form action="/finder.py" method="get" enctype="multipart/form-data">')
    print('  Search pattern: <input maxlength="60" size="60" value="" name="pattern">')
    print('  <input value="Submit" type="submit">')
    print('</form><br>')


    # show the current search pattern if one exists
    if len(self.pattern) > 1:              # there is a current search pattern
      print(f"Current search pattern: {self.pattern}<br><br>") 
    print(self.create_table(self.headers, self.rows))

    # make the table editable
    print('<script>')
    print('$("#zlma-table").SetEditable({columnsEd: "15,16,17,18", onEdit:function(){}})')
    print('</script>')
    print('</body></html>')                # end page

# main()
finder = Finder()                          # create a singleton
# finder.print_env() 
finder.process_query()                     # process the request
