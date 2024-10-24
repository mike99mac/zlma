#!/srv/venv/bin/python3
import os
import subprocess
import sys
from urllib.parse import parse_qs
sys.path.append('/srv/www/zlma')
from zlma_buttons import Zlma_buttons

class Vif_img_set:
  def __init__(self):
    """
    get arguemnts to call the 'vif image create' command 
    """
    print('Content-Type: text/html')       # start the HTML page
    print()
    print('<!DOCTYPE html>')
    print('<html><head><title>Run vif image set</title>')
    print('<link rel="stylesheet" href="/zlma.css">')
    print('</head><body>')
    zlma_buttons = Zlma_buttons("using-vif") # add navigation buttons

  def create_page(self):                   # make the HTML page
    query_string = os.environ.get('QUERY_STRING', '') # get env var
    query_params = parse_qs(query_string)  # parse query string
    sub_cmd = query_params.get('sub_cmd', [''])[0] # get first element of 'sub_cmd' value

    html_code = "<table><tr><td><pre>"     # start table, row, cell, preformatted text
    html_code += f"TODO: gather args to call 'vif image set {sub_cmd}' - how much memory/CPU to add/delete?\n"
    html_code += "</pre></td></tr></table>\n" # end cell, row and table
    html_code += "</body></html>"
    print(html_code)

# main()
vif_img_set = Vif_img_set()                # create a singleton
vif_img_set.create_page()                  # create a web page

