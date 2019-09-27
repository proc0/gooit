from gooey import Gooey, GooeyParser
from pprint import pprint
import json, os, sys
from colored import stylize, attr, fg

# model
GOO = [
  {
    'name': 'compose',
    'subs': []
  },
  {
    'name': 'commands',
    'label': 'Commands',
    'info': 'Current directory: ',
    'gooey_args':[
      'action',
      'help',
      'gooey_options',
      'widget'
    ],
    'gooey_map':{
      'info': 'help',
      'options': 'gooey_options'
    },
    'subs': [{
        'name': 'status',
        'flag': '--status',
        'info': 'Simple status',
        'action': 'store_true',
        'widget': 'BlockCheckbox',
        'options': {
          'checkbox_label': '',
        },
        'args': ''
      },{
        'name': 'add',
        'flag': '--add',
        'info': 'Add all files in current and sub directories.',
        'action': 'store_true',
        'widget': 'BlockCheckbox',
        'options': {
          'checkbox_label': ''
        },
        'args': '-A .'
      },{
        'name': 'commit',
        'flag': '--commit',
        'info': 'Commit current staged files.',
        'args': '-m'
      },{
        'name': 'push',
        'flag': '--push',
        'info': 'Push local changes to remote origin.',
        'action': 'store_true',
        'widget': 'BlockCheckbox',
        'options': {
          'checkbox_label': ''
        },
        'args': ''
      }]
  },
  {
    'name': 'settings',
    'subs': []
  }
]

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

# creates a clean, indexed dictionary
# with a method to process collections
class Model(dict):
  def __init__(self, sub_key=None):
    if(sub_key):
      self['sub_key'] = sub_key

  def __setitem__(self, key, value):
    if key in self or value is not None:
      dict.__setitem__(self, key, value)

  def transduce(self, keyName, branchKey, collection):
    if('sub_key' not in self):
      raise NameError('Model requires a submodel key $: Model(<some_str>)')
    else:      
      self.mapCollection(keyName, branchKey, collection, None)
    return self

  def mapCollection(self, keyName, branchKey, collection, parentKey):
    for model in collection:
      key = model[keyName] if keyName in model else None
      sub_model_key = self['sub_key']
      if(key and branchKey and self.hasBranches(branchKey, model)):
        self[key] = model
        self[key][sub_model_key] = Model()
        # 
        self.mapCollection(keyName, branchKey, model[branchKey], key)
      else:
        branch = self[parentKey] if parentKey and parentKey in self else None
        if(branch and sub_model_key in branch):
          branch[sub_model_key][key] = model

  def hasBranches(self, branchKey, model):
    if(branchKey in model and type(model[branchKey]) == list and len(model[branchKey]) > 0):
      branches = model[branchKey]
      answer = branches and len(list(filter(lambda b: type(b) == dict, branches))) == len(branches)
    else:
      answer = False
    return answer

# builds clean, indexed model from a list of arg names
# and a map of model keys to arg names
class ArgModel(Model):
  def __init__(self, model, arg_list, arg_map):
    for key in model:
      is_arg_key = key in arg_list
      is_arg_map = key in arg_map

      if(is_arg_key):
        meta_key = key
      elif(is_arg_map):
        meta_key = arg_map[key]
      else:
        meta_key = None

      meta_val = model[key] if meta_key else None
      
      self.__setitem__(meta_key, meta_val)


curDir = os.getcwd()
isGitDir = os.system('git status 1>'+os.devnull) == 0

@Gooey(
  program_name='Gooit v0.1.0', 
  program_description='Simple Git CLI GUI',
  advanced=True,
  clear_before_run=True, # TEST
  show_success_modal=False,
  # poll_external_updates=True,
  # progress_regex=r"^(?P<stat>.*)$",
  # progress_expr="stat",
  richtext_controls=True,
  requires_shell=True,
  supress_gooey_flag=True,
  navigation='TABBED',
  optional_cols=2,
  show_sidebar=False
  ) 
def main():
  # init parser
  gooit = GooeyParser(description="Gooit")
  cmd_parser = gooit.add_subparsers(help='commands', dest='main')

  # transform collection to indexed model
  goo = Model('models')
  goo.transduce('name', 'subs', GOO)

  # render arguments UI
  if(isGitDir):
    for g in GOO:
      if(g['name'] == 'commands'):
        cmd_grp = cmd_parser.add_parser(g['name'])
        cmd = cmd_grp.add_argument_group(g['label'], g['info'])
        if(len(g['subs'])):
          for s in g['subs']:
            meta_args = ArgModel(s, g['gooey_args'], g['gooey_map'])
            cmd.add_argument(s['flag'], **meta_args)
  # else:
  #   gitDir = gooit.add_subparsers(help='git', dest='git')
  #   gitDir.add_argument(metavar="directory path", dest='cwd', help='Choose directory', widget='FileChooser')

  # process UI arguments
  args = gooit.parse_args()
  # process commands
  git_cmd = []
  for arg in vars(args):
    models = goo['commands']['models']
    if(arg in models):
      val = getattr(args, arg)
      has_val = type(val) is str and len(val) > 0
      args_val = '"' + val + '"' if has_val else ''
      if(has_val or val):
        cmd_args = models[arg]['args'] if 'args' in models[arg] else ''
        cmd_txt = 'git ' + arg + ' ' + cmd_args + ' ' + args_val
        git_cmd.append(cmd_txt)

  # print command
  pipe_sym = ' | ' if os.name is 'nt' else ' && '
  final_command = str.join(pipe_sym, git_cmd)
  pprint(goo)
  print(stylize('$: ' + final_command, fg("green") + attr("bold")))

  # run command 
  os.system(final_command)

  # exit(0)
  # if('cmds' in args):
  #   print(args.cmds)
    # if(args.cmds == 'add'):
    #   os.system('git add -A .')
    # else:
    #   print(args.git)
    #   os.system('git ' + a)
  # if(isGitDir):
  #   gitDir = git.add_parser('settings', help='settings')
  #   branch_list = list_branches()
  #   gitDir.add_argument('--branch',
  #     metavar="Current: " + branch_list[0],
  #     help='Change branch',
  #     choices=branch_list,
  #     widget='Dropdown',
  #     gooey_options={'message':'blah'})

  #   git.add_parser('status', help="status")
  #   gitAdd = git.add_parser('add', help="add files")
  #   gitAddOpts = gitAdd.add_argument_group('Blah')
  #   gitAddOpts.add_argument('-A', help="status", widget='CheckBox')
  #   gitAddOpts.add_argument('-B', help="status", widget='CheckBox')
  #   gitCi = git.add_parser('commit', help="add all files")
  #   gitCi.add_argument('-m', metavar="comment", widget='Textarea')
  #   gitPush = git.add_parser('push', help="push to origin")
  # else:
  #   gitDir = gooit.add_subparsers(help='git', dest='git')
  #   gitDir.add_argument(metavar="directory path", dest='cwd', help='Choose directory', widget='FileChooser')

  # args = gooit.parse_args()
  # # print(args)
  # # # args2 = git.parse_args()
  # if('branch' in args):
  #   print(args.branch)
  # if('git' in args):
  #   if(args.git == 'add'):
  #     os.system('git add -A .')
  #   else:
  #     print(args.git)
  #     os.system('git ' + args.git)


if __name__ == '__main__':
  main()
  # if 'gooey-seed-ui' in sys.argv:
  #   print(json.dumps({'--branch': list_branches() }))
  # else:
  #   main()

def show_error_modal(error_msg):
  """ Spawns a modal with error_msg"""
  # wx imported locally so as not to interfere with Gooey
  import wx
  app = wx.App()
  dlg = wx.MessageDialog(None, error_msg, 'Error', wx.ICON_ERROR)
  dlg.ShowModal()
  dlg.Destroy()