from gooey import Gooey, GooeyParser
@Gooey(
    target="git", 
    program_name='Gooit v0.1.0', 
    progress_regex=r"^(?P<stat>.*)$",
    progress_expr="stat",
    show_sidebar=True,
    suppress_gooey_flag=True,
    advanced=True) 
def status():
    parser = GooeyParser()
    git = parser.add_argument_group('Git')
    git.add_argument('command', metavar='command')
    parser.parse_args()

if __name__ == '__status__':
    status()