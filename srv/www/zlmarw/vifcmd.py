#!/srv/venv/bin/python3
#import html
import os
import subprocess
import sys
from urllib.parse import parse_qs
sys.path.append('/srv/www/zlma')
from zlma_buttons import Zlma_buttons

class Vif_cmd:
  def __init__(self):
    """
    Initialize globals, create page header, set background
    """
    print('Content-Type: text/html')       # start the HTML page
    print()
    print('<!DOCTYPE html>')
    print('<html><head><title>Run a vif command</title>')
    print('<link rel="stylesheet" href="/zlma.css">')
    print('</head><body>')
    zlma_buttons = Zlma_buttons("using-vif")     # add navigation buttons

  def create_table(self, table_name, data):
    """
    Create an HTML table
    Args:
      table_name: The name of the table.
      data: A list of lists representing the table data.
    """
    html_code = f'<table class="greenScreenTable"><thead><tr><th>{table_name}</th></tr></thead>\n<tbody>\n'
    for row in data:
      html_code += f"<tr><td>{row}</td></tr>\n"
    html_code += "</tbody></table>\n"
    return html_code

  def run_vif_cmd(self, cmd: str, sub_cmd: str) -> str:
    """
    Run a vif command showing command and output in preformatted text
    """
    output = f"Running command: vif {cmd} {sub_cmd}\n"
    the_cmd = f"/srv/venv/bin/python3 /usr/local/sbin/vif {cmd} {sub_cmd}"
    proc = subprocess.run(the_cmd, shell=True, capture_output=True, text=True)
    rc = proc.returncode
    if rc != 0:
      output += f"Vif_cmd.run_cmd(): subprocess.run({the_cmd}) returned {rc}"
    else:
      output += f"{proc.stdout}"
    return output

  def create_page(self):
    """
    Create an HTML page with four tables: hypervisor, image, disk, and query.
    Handle dynamically based on vif commands and subcommands.
    """
    query_string = os.environ.get('QUERY_STRING', '')
    query_params = parse_qs(query_string)  # Parse the query string
    cmd = query_params.get('cmd', [''])[0] # Get 'cmd', default to '' if not found
    sub_cmd = query_params.get('sub_cmd', [''])[0].rstrip()

    # Dictionary of commands and their valid subcommands
    valid_commands = {
      'hypervisor': ['collect', 'errors', 'export', 'import', 'restart', 'service', 'shutdown', 'verify', 'volume'],
      'image': ['create', 'delete', 'network', 'set', 'start', 'stop', 'stopall'],
      'disk': ['copy', 'create', 'delete', 'share'],
      'query': ['active', 'all', 'configuration', 'disks', 'errors', 'image', 'level', 'network', 'paging', 'performance', 'shared', 'volumes']
    }

    # Validate the command and subcommand
    if cmd not in valid_commands:
      print(f"<h3>Invalid command: {cmd}</h3>")
      return
        
    if sub_cmd and sub_cmd not in valid_commands[cmd]:
      print(f"<h3>Invalid subcommand '{sub_cmd}' for command '{cmd}'</h3>")
      return

    # If both the command and subcommand are valid, execute the command
    html_code = '<table class="greenScreenTable">' # start a 'green screen' table
    html_code += "<tr><td><pre>"                   # start row, cell, preformatted text
    html_code += self.run_vif_cmd(cmd, sub_cmd)    # run the vif command
    html_code += "</pre></td></tr></table>\n"       # end cell, row and table
    html_code += "</body></html>"
    print(html_code)

# main()
vif_cmd = Vif_cmd()                        # create a singleton
vif_cmd.create_page()                      # create a web page

