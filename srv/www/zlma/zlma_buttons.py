#!/srv/venv/bin/python3
#
# zlmabuttons.py - action buttons common to all zlma pages:
#                'commands', 'consoles', 'finder', 'vif', 'help'
#
class Zlma_buttons:
  def __init__(self, page: str):
    """
    draw buttons common to zlma pages in a table
    """
    self.green="style=\"background-color:#8CFF66\""
    self.yellow="style=\"background-color:#FFDB4D\""

    self.html = '<br><table align=center border="0" cellpadding="0" cellspacing="0"><tr>\n' # start a table
    self.html += "<td><form action='/zlmarw/commands.py' accept-charset=utf-8>"
    self.html += f"<button class=button {self.green}>Commands</button>"
    self.html += "</form></td>\n"

    self.html += "<td><form action='/zlmarw/consolez.py' accept-charset=utf-8>"
    self.html += f"<button class=button {self.green}>Consoles</button>"
    self.html += "</form></td>\n" 

    self.html += "<td><form action='/zlmarw/finder.py' accept-charset=utf-8>"
    self.html += f"<button class=button {self.green}>Finder</button>"
    self.html += "</form></td>\n" 

    self.html += "<td><form action='/zlma/vif.py' accept-charset=utf-8>"
    self.html += f"<button class=button {self.green}>Vif</button>"
    self.html += "</form></td>\n"

    self.html += "<td><form action='https://github.com/mike99mac/zlma#{page}' accept-charset=utf-8>"
    self.html += f"<button class=button {self.yellow}>Help</button>"
    self.html += "</form></td></tr></table>\n" 

    print(self.html)

# main()
# nothing to do?

