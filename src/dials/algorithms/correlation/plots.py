from __future__ import annotations

import copy
import sys
from collections import OrderedDict

import numpy as np
from scipy.cluster import hierarchy

from dials.algorithms.clustering.plots import scipy_dendrogram_to_plotly_json


def linkage_matrix_to_dict(linkage_matrix: np.ndarray) -> OrderedDict:
    """
    Convert a linkage matrix to a dictionary.
    Args:
            linkage_matrix(numpy.ndarray): linkage matrix from hierarchy.linkage methods
    Returns:
            link_dict(collections.OrderedDict): linkage matrix converted to dictionary format
    """
    tree = hierarchy.to_tree(linkage_matrix, rd=False)

    d = {}

    # https://gist.github.com/mdml/7537455

    def add_node(node):
        if node.is_leaf():
            return
        cluster_id = node.get_id() - len(linkage_matrix) - 1
        row = linkage_matrix[cluster_id]
        d[cluster_id + 1] = {
            "datasets": [i + 1 for i in sorted(node.pre_order())],
            "height": row[2],
        }

        # Recursively add the current node's children
        if node.left:
            add_node(node.left)
        if node.right:
            add_node(node.right)

    add_node(tree)

    link_dict = OrderedDict(sorted(d.items()))

    return link_dict


def plot_dims(dims: list, funcs: list) -> dict:
    """
    Prepares a plotly-style plot of the dimension optimisation procedure.
    Args:
        dims(list): list of dimensions tested
        funcs(list): resulting functional when the tested number of dimensions is used in the cos-angle clustering procedure
    Returns:
        d(dict): dimensionality analysis plot saved as a dictionary for future plotting
    """
    d = {
        "dimensions": {
            "data": [
                {
                    "x": dims,
                    "y": funcs,
                    "type": "line",
                    "name": "Dimension Functionals",
                }
            ],
            "layout": {
                "title": "Residual for each tested dimension",
                "xaxis": {"title": "Dimension"},
                "yaxis": {"title": "Functional"},
            },
            "help": """\
A line graph showing the residual remaining in the minimisation for
each tested dimension. The chosen number of dimensions occurs when the
residual drops into the level of the noise as determined by an elbow plot
analysis (Zhang et al 2006).
""",
        }
    }
    return d


def to_plotly_json(
    correlation_matrix: np.ndarray,
    linkage_matrix: np.ndarray,
    labels: list = None,
    matrix_type: str = "correlation",
) -> dict:
    """
    Prepares a plotly-style plot of the heatmap corresponding to the input matrix
    with dendrograms on the top and left sides.
    Args:
        correlation_matrix(numpy.ndarray): pair-wise correlation matrix
        linkage_matrix(numpy.ndarray): linkage matrix describing dendrogram-style clustering of correlation matrix
        labels(list): desired labels for datasets
        matrix_type(str): must be "correlation" or "cos_angle"
    Returns:
        d(dict): heatmap and dendrogram plot expressed as a dictionary for future graphical display
    """

    if matrix_type not in ("correlation", "cos_angle"):
        sys.exit(
            f"Matrix type input as {matrix_type}, but needs to be 'correlation' or 'cos_angle'"
        )

    ddict = hierarchy.dendrogram(
        linkage_matrix,
        color_threshold=0.05,
        labels=labels,
        show_leaf_counts=False,
        no_plot=True,
    )

    # Converts the dendrogram to plotly json format - y2_dict is the one above the heatmap
    y2_dict = scipy_dendrogram_to_plotly_json(
        ddict, "Dendrogram", xtitle="Individual datasets", ytitle="Ward distance"
    )

    # x2_dict is the same dendrogram but positioned left of the heatmap
    x2_dict = copy.deepcopy(y2_dict)
    for d in y2_dict["data"]:
        d["yaxis"] = "y2"
        d["xaxis"] = "x2"

    # Switches x and y data so that the dendrogram will be rotated 90deg
    # This orientatates it to match with the heatmap
    for d in x2_dict["data"]:
        x = d["x"]
        y = d["y"]
        d["x"] = y
        d["y"] = x
        d["yaxis"] = "y3"
        d["xaxis"] = "x3"

    # Reorders the matrix into the same order as the dendrogram for the plots
    D = correlation_matrix
    index = ddict["leaves"]
    D = D[index, :]
    D = D[:, index]
    ccdict = {
        "data": [
            {
                "name": "%s_matrix" % matrix_type,
                "x": list(range(D.shape[0])),
                "y": list(range(D.shape[1])),
                "z": D.tolist(),
                "type": "heatmap",
                "colorbar": {
                    "title": (
                        "Correlation coefficient"
                        if matrix_type == "correlation"
                        else "cos(angle)"
                    ),
                    "titleside": "right",
                    "xpad": 0,
                },
                "colorscale": "YIOrRd",
                "xaxis": "x",
                "yaxis": "y",
            }
        ],
        "layout": {
            "autosize": False,
            "bargap": 0,
            "height": 1000,
            "hovermode": "closest",
            "margin": {"r": 20, "t": 50, "autoexpand": True, "l": 20},
            "showlegend": False,
            "title": "Dendrogram Heatmap",
            "width": 1000,
            "xaxis": {
                "domain": [0.2, 0.9],
                "mirror": "allticks",
                "showgrid": False,
                "showline": False,
                "showticklabels": True,
                "tickmode": "array",
                "ticks": "",
                "ticktext": y2_dict["layout"]["xaxis"]["ticktext"],
                "tickvals": list(range(len(y2_dict["layout"]["xaxis"]["ticktext"]))),
                "tickangle": 300,
                "title": "",
                "type": "linear",
                "zeroline": False,
            },
            "yaxis": {
                "domain": [0, 0.78],
                "anchor": "x",
                "mirror": "allticks",
                "showgrid": False,
                "showline": False,
                "showticklabels": True,
                "tickmode": "array",
                "ticks": "",
                "ticktext": y2_dict["layout"]["xaxis"]["ticktext"],
                "tickvals": list(range(len(y2_dict["layout"]["xaxis"]["ticktext"]))),
                "title": "",
                "type": "linear",
                "zeroline": False,
            },
            "xaxis2": {
                "domain": [0.2, 0.9],
                "anchor": "y2",
                "showgrid": False,
                "showline": False,
                "showticklabels": False,
                "zeroline": False,
            },
            "yaxis2": {
                "domain": [0.8, 1],
                "anchor": "x2",
                "showgrid": False,
                "showline": False,
                "zeroline": False,
            },
            "xaxis3": {
                "domain": [0.0, 0.1],
                "anchor": "y3",
                "range": [max(max(d["x"]) for d in x2_dict["data"]), 0],
                "showgrid": False,
                "showline": False,
                "tickangle": 300,
                "zeroline": False,
            },
            "yaxis3": {
                "domain": [0, 0.78],
                "anchor": "x3",
                "showgrid": False,
                "showline": False,
                "showticklabels": False,
                "zeroline": False,
            },
        },
    }
    d = ccdict
    d["data"].extend(y2_dict["data"])
    d["data"].extend(x2_dict["data"])

    d["clusters"] = linkage_matrix_to_dict(linkage_matrix)

    return d
