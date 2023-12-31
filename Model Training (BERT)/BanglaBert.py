import os
import logging
import transformers
from transformers import BertModel, BertForSequenceClassification, BertTokenizer, AdamW, get_linear_schedule_with_warmup
import torch
import numpy as np
import pandas as pd
import seaborn as sns
from pylab import rcParams
import matplotlib.pyplot as plt
from matplotlib import rc
from sklearn.model_selection import train_test_split
from sklearn.metrics import confusion_matrix, classification_report
from collections import defaultdict
from textwrap import wrap
from torch import nn, optim
from torch.utils.data import Dataset, DataLoader
import torch.nn.functional as F



sns.set(style='whitegrid', palette='muted', font_scale=1.2)
HAPPY_COLORS_PALETTE = ["#01BEFE", "#FFDD00", "#FF7D00", "#FF006D", "#ADFF02", "#8F00FF"]
sns.set_palette(sns.color_palette(HAPPY_COLORS_PALETTE))
rcParams['figure.figsize'] = 12, 8
RANDOM_SEED = 42
np.random.seed(RANDOM_SEED)
torch.manual_seed(RANDOM_SEED)
device = torch.device("cuda:0" if torch.cuda.is_available() else "cpu")

logging.basicConfig(level=logging.ERROR)
PRE_TRAINED_MODEL_NAME = 'bert-base-multilingual-cased'
tokenizer = BertTokenizer.from_pretrained(PRE_TRAINED_MODEL_NAME)

MAX_LEN = 300

class ShantoDataset(Dataset):
  def __init__(self, reviews, targets, tokenizer, max_len):
    self.reviews =  reviews
    self.targets = targets
    self.tokenizer = tokenizer
    self.max_len = max_len

  def __len__(self):
    return len(self.reviews)

  def __getitem__(self, item):
    reviews = str(self.reviews[item])
    target = self.targets[item]

    encoding = self.tokenizer.encode_plus(
        reviews,
        add_special_tokens = True,
        max_length = self.max_len,
        return_token_type_ids=True,
        pad_to_max_length=True,
        return_attention_mask=True,
        return_tensors='pt',
    )

    return {
      'review_text': reviews,
      'input_ids': encoding['input_ids'].flatten(),
      'attention_mask': encoding['attention_mask'].flatten(),
      'targets': torch.tensor(target, dtype=torch.long)
    }

def create_data_loader(df, tokenizer, max_len, batch_size):
  ds = ShantoDataset(
    reviews=df.tokenized_sentence.to_numpy(),
    targets=df.Author.to_numpy(),
    tokenizer=tokenizer,
    max_len=max_len
  )
  return DataLoader(
    ds,
    batch_size=batch_size
  )

BATCH_SIZE = 16

path_parent = os.path.dirname( os.getcwd() )
os.chdir( path_parent )
df_train = pd.read_csv("Model Training (BERT)/Final_Train.csv")
df_val =  pd.read_csv("Model Training (BERT)/Final_Val.csv")
df_test = pd.read_csv("Model Training (BERT)/Final_Test.csv")

train_data_loader = create_data_loader(df_train, tokenizer, MAX_LEN, BATCH_SIZE)
val_data_loader = create_data_loader(df_val, tokenizer, MAX_LEN, BATCH_SIZE)
test_data_loader = create_data_loader(df_test, tokenizer, MAX_LEN, BATCH_SIZE)

data = next(iter(train_data_loader))
data.keys()

bert_model = BertModel.from_pretrained(PRE_TRAINED_MODEL_NAME)

class SentimentClassifier(nn.Module):
  def __init__(self, n_classes):
    super(SentimentClassifier, self).__init__()
    self.bert = BertModel.from_pretrained(PRE_TRAINED_MODEL_NAME)
    self.drop = nn.Dropout(p=0.3)
    self.out = nn.Linear(self.bert.config.hidden_size, n_classes)
    self.softmax = nn.LogSoftmax(dim = 1)

  def forward(self, input_ids, attention_mask):
    last_hidden, pooled_output = self.bert(
      input_ids=input_ids,
      attention_mask=attention_mask,
      return_dict=False
    )
    output = self.drop(pooled_output)
    output = self.out(output)
    output = self.softmax(output)
    return output

model = SentimentClassifier(3)

model = model.to(device)

for name, param in model.named_parameters():
    if name.startswith('bert'):
        param.requires_grad = False

input_ids = data['input_ids'].to(device)
attention_mask = data['attention_mask'].to(device)
target = data['targets'].to(device)
print(input_ids.shape)
print(attention_mask.shape)
print(target)
preds = model(input_ids,attention_mask)

EPOCHS = 2

optimizer = AdamW(model.parameters(), lr=2e-4)
total_steps = len(train_data_loader) * EPOCHS
loss_fn = nn.NLLLoss().to(device)

def train_epoch(
  model,
  data_loader,
  loss_fn,
  optimizer,
  device,
  n_examples,
  thresh
):
  model.train()
  losses = []
  targs = []
  preds = []
  correct_predictions = 0
  for d in data_loader:
    input_ids = d["input_ids"].to(device)
    attention_mask = d["attention_mask"].to(device)
    targets = d["targets"].to(device)
    outputs = model(
      input_ids = input_ids,
      attention_mask=attention_mask
    )
    optimizer.zero_grad()
    loss = loss_fn(outputs, targets)

    losses.append(loss.item())
    loss.backward()
    optimizer.step()
    preds = torch.max(outputs, 1)[1]
    correct_predictions += torch.sum(preds == targets)
  return correct_predictions.double()/n_examples, np.mean(losses)

def eval_model(model, data_loader, loss_fn, device, n_examples,thresh):
  model.eval()
  losses = []
  targs = []
  preds = []
  correct_predictions = 0
  check = False
  with torch.no_grad():
    for d in data_loader:
      input_ids = d["input_ids"].to(device)
      attention_mask = d["attention_mask"].to(device)
      targets = d["targets"].to(device)
      outputs = model(
        input_ids = input_ids,
        attention_mask=attention_mask
      )
      loss = loss_fn(outputs, targets)
      losses.append(loss.item())
      preds = torch.max(outputs, 1)[1]

      correct_predictions += torch.sum(preds == targets)
  return correct_predictions.double()/n_examples, np.mean(losses)

history = defaultdict(list)
best_accuracy = 0
thresh = 0.2
for epoch in range(EPOCHS):
  print(f'Epoch {epoch + 1}/{EPOCHS}')
  print('-' * 10)
  train_acc, train_loss = train_epoch(
    model,
    train_data_loader,
    loss_fn,
    optimizer,
    device,
    len(df_train),
    thresh
  )
  print(f'Train loss {train_loss} accuracy {train_acc}')
  val_acc, val_loss = eval_model(
    model,
    val_data_loader,
    loss_fn,
    device,
    len(df_val),
    thresh
  )
  print(f'Val   loss {val_loss} accuracy {val_acc}')
  print()
  history['train_acc'].append(train_acc)
  history['train_loss'].append(train_loss)
  history['val_acc'].append(val_acc)
  history['val_loss'].append(val_loss)
  if val_acc > best_accuracy:
    best_accuracy = val_acc

test_acc, _ = eval_model(
  model,
  test_data_loader,
  loss_fn,
  device,
  len(df_test),
  thresh
)
test_acc.item()


def get_predictions(model, data_loader):
  model.eval()
  review_texts = []
  predictions = []
  prediction_probs = []
  real_values = []
  with torch.no_grad():
    for d in data_loader:
      texts = d["review_text"]
      input_ids = d["input_ids"].to(device)
      attention_mask = d["attention_mask"].to(device)
      targets = d["targets"].to(device)
      outputs = model(
        input_ids=input_ids,
        attention_mask=attention_mask
      )
      preds = torch.max(outputs, 1)[1].detach().cpu().numpy()
      targets = targets.long()
      targets = targets.detach().cpu().numpy()
      review_texts.extend(texts)
      predictions.extend(preds)
      prediction_probs.extend(outputs)
      real_values.extend(targets)
  return review_texts, predictions, prediction_probs, real_values

def RecallPrecisionFScore(y_test, pred):
  arr = confusion_matrix(y_test, pred)
  fp = arr[0][1] + arr[0][2] + arr[1][0] + arr[1][2] + arr[2][1] + arr[2][2]
  fn = arr[1][0] + arr[2][0] + arr[0][1] + arr[2][1] + arr[0][2] + arr[1][2]
  tp = arr[0][0] + arr[1][1] + arr[2][2]
  print("tp: ", tp)
  print("fp: ",fp)
  print("fn: ", fn)
  precision = tp/(tp+fp)
  recall = tp/(tp+fn)
  f1 = (2*precision*recall )/(precision+recall)
  print("precision: ", round(tp/(tp+fp)*100,2) )
  print("recall: ", round(tp/(tp+fn)*100,2) )
  print("f1: ", round( ((2*precision*recall )/(precision+recall) )*100,2) )
  return float('{0:.2f}'.format(precision*100)), float('{0:.2f}'.format(recall*100)), float('{0:.2f}'.format(f1*100))

y_review_texts, y_pred, y_pred_probs, y_test = get_predictions(
  model,
  test_data_loader
)
print(y_pred)
print()
print(y_test)

class_names = df_test.columns.to_list()

print(classification_report(y_test, y_pred))
RecallPrecisionFScore(y_test, y_pred)