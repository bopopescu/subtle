# Copyright 2017 Google Inc. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""gcloud shell styles."""

from prompt_toolkit import styles
from prompt_toolkit.token import Token


BLUE = '#00DED1'
GREEN = '#008000'
GRAY = '#666666'
DARK_GRAY = '#333333'
BLACK = '#000000'


def Color(foreground=None, background=None):
  components = []
  if foreground:
    components.append(foreground)
  if background:
    components.append('bg:' + background)
  return ' '.join(components)


def GetDocumentStyle():
  """Return the color styles for the layout."""
  prompt_styles = styles.default_style_extensions
  prompt_styles.update({
      Token.Menu.Completions.Completion.Current: Color(BLUE, GRAY),
      Token.Menu.Completions.Completion: Color(BLUE, DARK_GRAY),
      Token.Toolbar: Color(BLUE),
      Token.Toolbar.Account: Color(),
      Token.Toolbar.Separator: Color(),
      Token.Toolbar.Project: Color(),
      Token.Toolbar.Help: Color(),
      Token.Prompt: Color(),
      Token.HSep: Color(GREEN),
      Token.HelpToolbar.SectionName: Color(BLUE),
      Token.HelpToolbar.SectionValue: Color(GREEN),
  })
  return styles.PygmentsStyle.from_defaults(style_dict=prompt_styles)
