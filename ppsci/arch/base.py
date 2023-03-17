"""Copyright (c) 2023 PaddlePaddle Authors. All Rights Reserved.

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
"""

from typing import Dict
from typing import List

import numpy as np
import paddle
import paddle.nn as nn

from ppsci.utils import logger


class NetBase(nn.Layer):
    """Base class for Network"""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._input_transform = None
        self._output_transform = None

    def forward(self, *args, **kwargs):
        raise NotImplementedError(f"NetBase.forward is not implemented")

    @property
    def num_params(self):
        num = 0
        for name, param in self.named_parameters():
            if hasattr(param, "shape"):
                num += np.prod(list(param.shape))
            else:
                logger.warning(f"{name} has no attribute 'shape'")
        return num

    def concat_to_tensor(
        self, data_dict: Dict[str, paddle.Tensor], keys: List[str], axis=-1
    ) -> List[paddle.Tensor]:
        data = [data_dict[key] for key in keys]
        return paddle.concat(data, axis)

    def split_to_dict(
        self, data_tensor: paddle.Tensor, keys: List[str], axis=-1
    ) -> Dict[str, paddle.Tensor]:
        data = paddle.split(data_tensor, len(keys), axis=axis)
        return {key: data[i] for i, key in enumerate(keys)}

    def register_input_transform(self, transform):
        self._input_transform = transform

    def register_output_transform(self, transform):
        self._output_transform = transform

    def __str__(self):
        num_fc = 0
        num_conv = 0
        num_bn = 0
        for layer in self.sublayers(include_self=True):
            if isinstance(layer, nn.Linear):
                num_fc += 1
            elif isinstance(layer, (nn.Conv2D, nn.Conv3D, nn.Conv1D)):
                num_conv += 1
            elif isinstance(layer, (nn.BatchNorm, nn.BatchNorm2D, nn.BatchNorm3D)):
                num_bn += 1
        _str = ", ".join(
            [
                self.__class__.__name__,
                f"input_keys = {self.input_keys}",
                f"output_keys = {self.output_keys}",
                f"num_fc = {num_fc}",
                f"num_conv = {num_conv}",
                f"num_bn = {num_bn}",
                f"num_params = {self.num_params}",
            ]
        )
        return _str
