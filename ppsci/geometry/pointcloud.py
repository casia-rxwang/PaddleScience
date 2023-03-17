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

import os.path as osp

import numpy as np

from ppsci.geometry import geometry


class PointCloud(geometry.Geometry):
    """A geometry represented by a point cloud, i.e., a set of points in space.

    Args:
        interior_path (str): File which store interior points of a point cloud.
        boundary_path (str): File which store boundary points of a point cloud.
        boundary_normal_path (str): File which store boundary normals of a point cloud.
        coord_keys (List[str]): List of coordinate keys, such as ["x", "y"].
        alias_dict (List[str]): Alias name for coord key, such as {"X:0": "x", "X:1": "y"}.
    """

    def __init__(
        self,
        interior_path,
        coord_keys,
        boundary_path=None,
        boundary_normal_path=None,
        alias_dict=None,
    ):
        if not osp.exists(interior_path):
            raise FileNotFoundError(f"interior_path({interior_path}) not exist.")

        # PointCloud from CSV file
        if interior_path.endswith(".csv"):
            # read data
            import pandas as pd

            raw_data_frame = pd.read_csv(interior_path)

            # convert to numpy array
            self.interior = []
            for key in coord_keys:
                self.interior.append(
                    np.asarray(raw_data_frame[key], "float32").reshape([-1, 1])
                )
            self.interior = np.concatenate(self.interior, -1)

        # PointCloud from CSV file
        if boundary_path is not None and boundary_path.endswith(".csv"):
            # read data
            import pandas as pd

            raw_data_frame = pd.read_csv(boundary_path)

            # convert to numpy array
            self.boundary = {}
            for key in coord_keys:
                self.boundary.append(
                    np.asarray(raw_data_frame[key], "float32").reshape([-1, 1])
                )
            self.boundary = np.concatenate(self.boundary, -1)
        else:
            self.boundary = None

        # PointCloud from CSV file
        if boundary_normal_path is not None and boundary_normal_path.endswith(".csv"):
            # read data
            import pandas as pd

            raw_data_frame = pd.read_csv(boundary_normal_path)

            # convert to numpy array
            self.normal = {}
            for key in coord_keys:
                self.normal.append(
                    np.asarray(raw_data_frame[key], "float32").reshape([-1, 1])
                )
            self.normal = np.concatenate(self.normal, -1)
        else:
            self.normal = None

        self.input_keys = []
        for key in coord_keys:
            if key in alias_dict:
                self.input_keys.append(alias_dict[key])
            else:
                self.input_keys.append(key)

        super().__init__(
            len(coord_keys),
            (np.amin(self.interior, axis=0), np.amax(self.interior, axis=0)),
            np.inf,
        )

    @property
    def dim_keys(self):
        return self.input_keys

    def is_inside(self, x):
        # NOTE: point on boundary is included
        return (
            np.isclose((x[:, None, :] - self.interior[None, :, :]), 0, atol=1e-6)
            .all(axis=2)
            .any(axis=1)
        )

    def on_boundary(self, x):
        if not self.boundary:
            raise ValueError(
                "self.boundary must be initialized" " when call 'on_boundary' function"
            )
        return (
            np.isclose(
                (x[:, None, :] - self.boundary[None, :, :]),
                0,
                atol=1e-6,
            )
            .all(axis=2)
            .any(axis=1)
        )

    def translate(self, translation):
        for i, offset in enumerate(translation):
            self.interior[:, i] += offset
            if self.boundary:
                self.boundary += offset
        return self

    def scale(self, scale):
        for i, _scale in enumerate(scale):
            self.interior[:, i] *= _scale
            if self.boundary:
                self.boundary[:, i] *= _scale
            if self.normal:
                self.normal[:, i] *= _scale
        return self

    def uniform_boundary_points(self, n: int):
        """Compute the equispaced points on the boundary."""
        raise NotImplementedError(
            f"PointCloud do not have 'uniform_boundary_points' method"
        )

    def random_boundary_points(self, n, random="pseudo"):
        assert self.boundary is not None, (
            "boundary points can't be empty when call "
            "'random_boundary_points' method"
        )
        assert n <= len(self.boundary), (
            f"number of sample points({n}) "
            f"can't be more than that in boundary({len(self.boundary)})"
        )
        return self.boundary[
            np.random.choice(len(self.boundary), size=n, replace=False)
        ]

    def random_points(self, n, random="pseudo"):
        assert n <= len(self.interior), (
            f"number of sample points({n}) "
            f"can't be more than that in points({len(self.interior)})"
        )
        return self.interior[
            np.random.choice(len(self.interior), size=n, replace=False)
        ]

    def union(self, rhs):
        raise NotImplementedError(
            f"Union operation for PointCloud is not supported yet."
        )

    def __or__(self, rhs):
        raise NotImplementedError(
            f"Union operation for PointCloud is not supported yet."
        )

    def difference(self, rhs):
        raise NotImplementedError(
            f"Subtraction operation for PointCloud is not supported yet."
        )

    def __sub__(self, rhs):
        raise NotImplementedError(
            f"Subtraction operation for PointCloud is not supported yet."
        )

    def intersection(self, rhs):
        raise NotImplementedError(
            f"Intersection operation for PointCloud is not supported yet."
        )

    def __and__(self, rhs):
        raise NotImplementedError(
            f"Intersection operation for PointCloud is not supported yet."
        )

    def __str__(self) -> str:
        """Return the name of class"""
        _str = ", ".join(
            [
                self.__class__.__name__,
                f"num_points = {len(self.interior)}",
                f"ndim = {self.ndim}",
                f"bbox = {self.bbox}",
                f"dim_keys = {self.dim_keys}",
            ]
        )
        return _str
