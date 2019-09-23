from gooey import Gooey, GooeyParser

    # progress_regex=r"^(?P<stat>.*)$",
    # progress_expr="stat",
@Gooey(
    target="git", 
    program_name='Gooit v0.1.0', 
    show_sidebar=True,
    suppress_gooey_flag=True,
    show_success_modal=False,
    advanced=True) 
def main():
    parser = GooeyParser(description="Git Dashboard")
    git = parser.add_argument_group('Git')
    subs = parser.add_subparsers(help='commands', dest='command')
    subs.add_parser('status', help="status")
    subs.add_parser('add -A .', help="add all files")
    ci = subs.add_parser('commit', help="add all files")
    ci.add_argument('-m', metavar="comment")
    parser.parse_args()


if __name__ == '__main__':
    main()