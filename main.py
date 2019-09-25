from gooey import Gooey, GooeyParser
import json, os, sys

curDir = os.getcwd()
isGitDir = os.system('git status 1>'+os.devnull) == 0

def list_branches():
    git_branches = os.popen('git branch').read().split()
    cur_branch = False
    branches = []
    for idx, val in enumerate(git_branches):
        br = val
        if(br == '*'):
            i = idx + 1
            cur_branch = git_branches[i]
        elif(br != cur_branch):
            branches.append(br)
        
    branch_opts = [cur_branch, *branches]

    return branch_opts

# progress_regex=r"^(?P<stat>.*)$",
# progress_expr="stat",

@Gooey(

    program_name='Gooit v0.1.0', 
    program_description='Simple Git CLI GUI',
    advanced=True,
    show_success_modal=False,
    poll_external_updates=True,
    progress_regex=r"^(?P<stat>.*)$",
    progress_expr="stat",
    requires_shell=True,
    show_sidebar=True,
    tabbed_groups=True
    ) 
def main():
    gooit = GooeyParser(description="Gooit")

    git = gooit.add_subparsers(dest='git', help='run git')
    if(isGitDir):
        gitDir = git.add_parser('settings', help='settings')
        branch_list = list_branches()
        gitDir.add_argument('--branch',
            metavar="Current: " + branch_list[0],
            help='Change branch',
            choices=branch_list,
            widget='Dropdown')

        git.add_parser('status', help="status")
        gitAdd = git.add_parser('add', help="add files")
        gitCi = git.add_parser('commit', help="add all files")
        gitCi.add_argument('-m', metavar="comment")
        gitPush = git.add_parser('push', help="push to origin")
    else:
        gitDir = gooit.add_subparsers(help='git', dest='git')
        gitDir.add_argument(metavar="directory path", dest='cwd', help='Choose directory', widget='FileChooser')

    args = gooit.parse_args()
    # print(args)
    # # args2 = git.parse_args()
    if('branch' in args):
        print(args.branch)
    if('git' in args):
        if(args.git == 'add'):
            os.system('git add -A .')
        else:
            print(args.git)
            os.system('git ' + args.git)


if __name__ == '__main__':
    if 'gooey-seed-ui' in sys.argv:
        print(json.dumps({'--branch': list_branches() }))
    else:
        main()

def show_error_modal(error_msg):
    """ Spawns a modal with error_msg"""
    # wx imported locally so as not to interfere with Gooey
    import wx
    app = wx.App()
    dlg = wx.MessageDialog(None, error_msg, 'Error', wx.ICON_ERROR)
    dlg.ShowModal()
    dlg.Destroy()