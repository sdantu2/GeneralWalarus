# from globals import servers, vc_connections, elections
    
class _Command:
    """ A class that represents a Walarus Shell command """
    def __init__(self, name: str, description: str, fn) -> None:
        self.name = name
        self.description = description
        self.run = fn        
    
def help() -> None:
    for value in cmd_map.values():
        print(f"\t'{value.name}' --> {value.description}")
    
cmd_map: dict = {
    "help": _Command("help", "List out all the Walarus Shell commands", help)
}    

def run_walarus_shell():
    while True:
        command: str = input("8==D ")
        cmd_map[command].run()

run_walarus_shell()