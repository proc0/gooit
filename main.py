from gooey import Gooey, GooeyParser
from pprint import pprint
import json, os, sys
from colored import stylize, attr, fg

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

# model
GOO = [
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
    'label': 'Settings',
    'info': 'Settings',
    'gooey_args':[
      'action',
      'help',
      'choices',
      'gooey_options',
      'widget'
    ],
    'gooey_map':{
      'info': 'help',
      'options': 'gooey_options'
    },
    'subs': [{
        'name': 'branch',
        'flag': '--branch',
        'info': 'Change branch.',
        'widget': 'Dropdown',
        'choices': list_branches(),
        'options': {
          'message':'blah'
        },
        'args': ''
      }]
  }
]

# creates a clean, indexed dictionary
# with a method to process collections
class Model(dict):
  def __init__(self, sub_key=None):
    if(sub_key):
      self['sub_key'] = sub_key

  def __setitem__(self, key, value):
    if key in self or value is not None:
      dict.__setitem__(self, key, value)

  def transduce(self, key_name, branch_key, collection):
    if('sub_key' not in self):
      raise NameError('Model requires a submodel key $: Model(<some_str>)')
    else:      
      self.mapCollection(key_name, branch_key, collection, parent_key=None)
    return self

  def mapCollection(self, key_name, branch_key, collection, parent_key):
    for model in collection:
      key = model[key_name] if key_name in model else None
      sub_model_key = self['sub_key']
      if(key and branch_key and self.hasBranches(branch_key, model)):
        self[key] = model
        self[key][sub_model_key] = Model()
        # 
        self.mapCollection(key_name, branch_key, model[branch_key], key)
      else:
        branch = self[parent_key] if parent_key and parent_key in self else None
        if(branch and sub_model_key in branch):
          branch[sub_model_key][key] = model

  def hasBranches(self, branch_key, model):
    branches = model[branch_key] if branch_key in model else None
    if(branches and type(branches) == list):
      is_model = lambda b: type(b) == dict
      models = list(filter(is_model, branches))
      answer = len(branches) > 0 and len(models) == len(branches)
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
  poll_external_updates=True,
  progress_regex=r"^(?P<stat>.*)$", # TODO: not working?
  progress_expr="stat", # TODO: not working?
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
  # pprint(goo)

  # render arguments UI
  if(isGitDir):
    for g in GOO:
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
  print(stylize('$: ' + final_command, fg("green") + attr("bold")))

  # run commands
  for cmd in git_cmd:
    os.system(cmd)

if __name__ == '__main__':
  # main()
  if 'gooey-seed-ui' in sys.argv:
    print(json.dumps({'commands': list_branches() }))
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