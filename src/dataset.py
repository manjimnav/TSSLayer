
import tensorflow as tf
from sklearn.preprocessing import StandardScaler
import numpy as np
from functools import partial

def collate_pair(x, pred_len, values_idxs, label_idxs, selection_idxs=None, select_timesteps=False, keep_dims=False):
    seq_len = len(x)-pred_len
    inputs = x[:-pred_len]

    feat_size = len(label_idxs)+ len(values_idxs)

    if select_timesteps:
        selected_inputs = tf.squeeze(tf.gather(tf.reshape(inputs, [seq_len*feat_size]), selection_idxs))
    else:
        selected_inputs = tf.squeeze(tf.gather(inputs, selection_idxs, axis=1))
    
    if keep_dims:
        padded_selection = tf.zeros_like(tf.reshape(inputs, [seq_len*feat_size]))
        padded_selection = tf.tensor_scatter_nd_add(padded_selection, selection_idxs.reshape(-1, 1), selected_inputs)
        selected_inputs = tf.reshape(padded_selection, [seq_len, feat_size])
    
    outputs = tf.squeeze(tf.reshape(tf.gather(x[-pred_len:], [label_idxs], axis=1), [pred_len*len(label_idxs)]))

    return selected_inputs, outputs

def batch(seq_len, x):
    return x.batch(seq_len)

def get_values_and_labels_index(data):
    label_idxs = [idx for idx, col in enumerate(data.columns) if 'target' in col]
    values_idxs = [idx for idx, col in enumerate(data.columns) if 'target' not in col]

    return label_idxs, values_idxs

def split_and_scale(data):

    scaler = StandardScaler()

    train_df = data.iloc[:int(len(data)*0.7)]
    train_scaled = scaler.fit_transform(train_df.values)

    valid_df = data.iloc[int(len(data)*0.7):int(len(data)*0.8)]
    valid_scaled = scaler.transform(valid_df.values)

    test_df = data.iloc[int(len(data)*0.8):]
    test_scaled = scaler.transform(test_df.values)

    return train_scaled, valid_scaled, test_scaled, scaler

def windowing(train_scaled, valid_scaled, test_scaled, values_idxs, label_idxs, selection_idxs, parameters):

    seq_len = parameters['dataset']['params']['seq_len']
    pred_len = parameters['dataset']['params']['pred_len']
    shift = parameters['dataset']['params']['shift'] or seq_len
    select_timesteps = parameters['dataset']['params']['select_timesteps']

    keep_dims = parameters['model']['params'].get('keep_dims', False) 

    data_train = tf.data.Dataset.from_tensor_slices(train_scaled)
    data_valid = tf.data.Dataset.from_tensor_slices(valid_scaled)
    data_test = tf.data.Dataset.from_tensor_slices(test_scaled)
    
    batch_seq = partial(batch, seq_len+pred_len)

    data_train = data_train.window(seq_len+pred_len, shift=shift, drop_remainder=True).flat_map(batch_seq).map(lambda x: collate_pair(x, pred_len, values_idxs, label_idxs, selection_idxs, select_timesteps, keep_dims))
    data_valid = data_valid.window(seq_len+pred_len, shift=shift, drop_remainder=True).flat_map(batch_seq).map(lambda x: collate_pair(x, pred_len, values_idxs, label_idxs, selection_idxs, select_timesteps, keep_dims))
    data_test = data_test.window(seq_len+pred_len, shift=shift, drop_remainder=True).flat_map(batch_seq).map(lambda x: collate_pair(x, pred_len, values_idxs, label_idxs, selection_idxs, select_timesteps, keep_dims))

    data_train = data_train.batch(32, drop_remainder=True).cache().prefetch(tf.data.AUTOTUNE)
    data_valid = data_valid.batch(32, drop_remainder=True).cache().prefetch(tf.data.AUTOTUNE)
    data_test = data_test.batch(32, drop_remainder=True).cache().prefetch(tf.data.AUTOTUNE)

    return data_train, data_valid, data_test
    
def get_feature_names(data, parameters):

    seq_len = parameters['dataset']['params']['seq_len']
    select_timesteps = parameters['dataset']['params']['select_timesteps']

    feature_names = np.array([col for  col in data.columns])
    
    if select_timesteps:
        features = np.array([np.core.defchararray.add(feature_names, ' t-'+str(i)) for i in range(seq_len, 0, -1)]).flatten()
    else:
        features = feature_names
    
    return features