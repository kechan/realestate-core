from ipywidgets import VBox, HBox, Text, HTML, Label, Layout, Button
import pandas as pd

from realestate_core.common.utils import join_df

# Monkey patch this to pd.DataFrame
pd.DataFrame.render = lambda self, **kwargs: EditableDataFrame(df=self, **kwargs).render()

class EditableDataFrame:
  def __init__(self, 
               df: pd.DataFrame, 
               display_cols=[], 
               editable_cols=[], 
               longtext_cols=[], 
               html_cols=[], 
               n_row_per_page=10, 
               long_text_width='400px',
               aux_df=None,
               aux_key=None):
    self.df = df
    assert self.df.index.is_unique, "df's index must be unique for editing to work correctly."

    self.n_row_per_page = n_row_per_page

    if len(display_cols) == 0:    # not provided, display first 5 cols
      display_cols = list(self.df.columns[:5])

    assert len(editable_cols) <= 1, 'Only 1 editable col is supported for now'  # TODO: support multiple editable cols
    # assert len(longtext_cols) <= 1, 'Only 1 longtext col is supported for now'  # TODO: support multiple longtext cols
    # assert len(html_cols) <= 1, 'Only 1 html col is supported for now'  # TODO: support multiple html cols

    self.display_cols = display_cols
    self.editable_cols = editable_cols
    self.longtext_cols = longtext_cols  # will be a non-editable HTML with word-wrap and width 400px
    self.html_cols = html_cols  # will be a non-editable HTML with word-wrap

    self._display_df = None    # use for display
    self._criteria = None
    self._indices = None

    self.table = None
    self.current_idx = 0

    # top label to show total rows
    self.total_rows_label = Label(value=f'Total rows: {len(self.df)}')

    # back button
    self.back_button = Button(
      description='Back',
      tooltip='Back',
    )
    self.back_button.on_click(self._back_button_clicked)

    # long text width in px
    self.long_text_width = long_text_width

    # render with aux info provided by aux_df, using aux_key as join key with self._display_df
    self.aux_df = aux_df
    if self.aux_df is not None: assert aux_key is not None, 'aux_key must be provided if aux_df is provided'
    self.aux_key = aux_key

  @property
  def filter(self):
    return self._criteria
  
  @filter.setter
  def filter(self, new_criteria):
    self._criteria = new_criteria
    self._display_df = self.df.q(self._criteria)[self.display_cols]
    self._indices = None   # indices not used if filter is provided, and vice versa

  def filter_by(self, col_name, values) -> 'EditableDataFrame':
    idxs = [self.df.index[self.df[col_name] == value][0] for value in values]
    self.indices = idxs
    return self


  @property
  def indices(self):
    return self._indices

  @indices.setter
  def indices(self, new_indices):
    self._indices = new_indices

    display_cols_in_df = [c for c in self.display_cols if c in self.df.columns]
    self._display_df = self.df.loc[self._indices][display_cols_in_df]

    if self.aux_df is not None:   # join this with _display_df
      self._display_df = self._display_df.reset_index()
      self._display_df = join_df(self._display_df, self.aux_df, left_on=self.aux_key, how='left')
      self._display_df = self._display_df.set_index(self._display_df.columns[0])

      self._display_df = self._display_df[self.display_cols]
    self._criteria = None  # critera filter not used if indices is provided, and vice versa

  def set_indices(self, new_indices):
    self.indices = new_indices 
    return self

  def render(self) -> VBox:  
    # assert self._display_df is not None, 'a filter or indice must be provided'
    if self._display_df is None:
      self.indices = self.df.index    # all of them, Note: this trigger setter call and populate self._display_df
      
    
    # if len(self.longtext_cols) > 0:
    #   longtext_col = self.longtext_cols[0]
    # else:
    #   longtext_col = 'dfglhsdf@#$'

    # header = HBox([self._make_textbox(c, disabled=True, layout=Layout(width=self.long_text_width) if c == longtext_col else Layout(width='auto')) for c in ['index'] + list(self._display_df.columns)])
    header = []
    for c in ['index'] + list(self._display_df.columns):
      if c in self.longtext_cols:
          header.append(self._make_textbox(c, disabled=True, layout=Layout(width=self.long_text_width)))
      else:
          header.append(self._make_textbox(c, disabled=True, layout=Layout(width='auto')))

    header = HBox(header)

    if self.n_row_per_page is not None:
      rows = [self._make_row(index, row) for index, row in self._display_df.iloc[self.current_idx: self.current_idx+self.n_row_per_page].iterrows()]
      next_button = Button(
        description='Next',
        tooltip='Next',
      )
      next_button.on_click(self._next_button_clicked)

      if self.table is None:
        self.table = VBox([self.total_rows_label, HBox([self.back_button, next_button]), header, VBox(rows), HBox([self.back_button, next_button])])
      else:
        self.table.children = [self.total_rows_label, HBox([self.back_button, next_button]), header, VBox(rows), HBox([self.back_button, next_button])]

      return self.table
    else:  
      rows = [self._make_row(index, row) for index, row in self._display_df.iterrows()]
      return VBox([self.total_rows_label, header, VBox(rows)])

  def _make_textbox(self, value, disabled=False, layout=Layout(width='auto')):
    return Text(value=str(value),                 
                layout=layout, 
                disabled=disabled)
    
  def _make_html(self, value):
    return HTML(value= '<style>p{word-wrap: break-word}</style> <p>'+ str(value) +' </p>', layout=Layout(width=self.long_text_width))

  def _make_label(self, value):
    return Label(value=str(value), layout=Layout(width='auto'))

  def _make_row(self, index, row):

    # TODO: fix to support multiple editable cols later, just pick the first one for now
    editable_col = self.editable_cols[0] if len(self.editable_cols) > 0 else 'dfglhsdf@#$'  # just random stuff that shold never hit
    html_col = self.html_cols[0] if len(self.html_cols) > 0 else 'dfglhsdf@#$'  # just random stuff that shold never hit

    row_widgets = []
    row_widgets.append(self._make_textbox(index, disabled=True))
    # row_widgets += [self._make_textbox(row[c], disabled=(True if c != editable_col else False)) if c != html_col else self._make_html(row[c]) for c in self._display_df.columns]

    for c in self._display_df.columns:
      if c in self.html_cols:
        widget = self._make_html(row[c])
      elif c in self.longtext_cols:
        widget = self._make_html(row[c])
      elif c in self.editable_cols:
        widget = self._make_textbox(row[c], disabled=False)
      else:
        widget = self._make_textbox(row[c], disabled=True)
      row_widgets.append(widget)

    for widget, column in zip(row_widgets, ['index'] + list(self._display_df.columns)):
      def save_value(change, column=column, row=row):
        print(f"index: {index}, col: {column}, change: {change.new}")
        row[column] = change.new
        self.df.loc[index, column] = change.new    
        self._display_df.loc[index, column] = change.new    # keep display version in sync.
      widget.observe(save_value, 'value')
    return HBox(row_widgets)
  
  def _next_button_clicked(self, b):
    self.current_idx += self.n_row_per_page
    self.table.children = []

    self.render()

  def _back_button_clicked(self, b):
    self.current_idx = max(0, self.current_idx - self.n_row_per_page)
    self.table.children = []
    self.render()

