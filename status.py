from gooey import Gooey, GooeyParser

@Gooey(
    target="git status", 
    program_name='Gooit v0.1.0', 
    show_sidebar=True,
    suppress_gooey_flag=True,
    show_success_modal=False,
    advanced=True)
def status():
    parser = GooeyParser()
    parser.parse_args()

if __name__ == '__main__':
    status()